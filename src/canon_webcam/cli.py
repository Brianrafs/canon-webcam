"""Interface de linha de comando para processamento de webcam/arquivo."""

from __future__ import annotations

import argparse
import os
import time
from typing import Union

import cv2

from canon_webcam.output.virtual_cam import VirtualWebcam
from canon_webcam.processing.hud_remover import HUDRemover


class StandaloneProcessor:
    """Processa arquivos de vídeo ou o feed da webcam sem EDSDK/GUI."""

    def __init__(self):
        self.hud_remover = HUDRemover()

    def process_webcam(self, source: Union[int, str], output_virtual: bool = False) -> None:
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            print(f"Error: Cannot open video source {source}")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        print("Press 'q' to quit")
        print("Press 'h' to toggle HUD blur")
        print("Press 'c' to toggle crop")
        print("Press 'a' to auto-detect HUD")

        self.hud_remover.set_blur_hud(True)
        hud_blur = True

        vcam = None
        if output_virtual:
            try:
                vcam = VirtualWebcam(width=1280, height=720, fps=30)
                vcam.start()
            except Exception as e:
                print(f"Virtual camera not available: {e}")

        frame_count = 0
        start_time = time.time()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            processed = self.hud_remover.process_frame(frame)

            if vcam and vcam.is_active:
                vcam.send(processed)

            cv2.imshow("Preview (q=quit, h=hud, c=crop, a=auto)", processed)

            frame_count += 1
            elapsed = time.time() - start_time
            if elapsed >= 1.0:
                print(f"\rFPS: {frame_count / elapsed:.1f}", end="", flush=True)
                frame_count = 0
                start_time = time.time()

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('h'):
                hud_blur = not hud_blur
                self.hud_remover.set_blur_hud(hud_blur)
                print(f"\nHUD blur: {'ON' if hud_blur else 'OFF'}")
            elif key == ord('a'):
                regions = self.hud_remover.detect_hud_text_regions(frame)
                self.hud_remover.clear_hud_regions()
                for region in regions:
                    self.hud_remover.add_hud_region(*region)
                print(f"\nDetected {len(regions)} HUD regions")

        cap.release()
        cv2.destroyAllWindows()
        if vcam:
            vcam.stop()

    def process_file(self, input_path: str, output_path: str = "") -> None:
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            print(f"Error: Cannot open {input_path}")
            return

        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

        self.hud_remover.set_blur_hud(True)

        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

        print(f"Processing: {input_path} ({w}x{h} @ {fps:.1f}fps)")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            processed = self.hud_remover.process_frame(frame)

            if writer:
                writer.write(processed)

            cv2.imshow("Processed", processed)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        if writer:
            writer.release()
        cv2.destroyAllWindows()
        print("Done!")


def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Canon T5i Webcam - Standalone HUD Processor")
    parser.add_argument("--source", type=str, default="0", help="Video source (0 for webcam, or file path)")
    parser.add_argument("--output", type=str, help="Output video file path")
    parser.add_argument("--virtual", action="store_true", help="Also output to virtual webcam")
    return parser.parse_args(argv)


def main(argv=None) -> None:
    args = _parse_args(argv)

    try:
        source: Union[int, str] = int(args.source)
    except ValueError:
        source = args.source

    processor = StandaloneProcessor()

    if isinstance(source, str) and os.path.exists(source):
        processor.process_file(source, args.output)
    else:
        processor.process_webcam(source, args.virtual)


if __name__ == "__main__":
    main()