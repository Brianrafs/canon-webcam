"""Testes do pipeline de captura usando uma fonte fake."""

import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np  # noqa: E402

from canon_webcam.capture.base import CaptureSource  # noqa: E402
from canon_webcam.output.base import VideoOutput  # noqa: E402
from canon_webcam.services.pipeline import PreviewPipeline  # noqa: E402


class FakeSource(CaptureSource):
    def __init__(self, frames: int = 40):
        self._frames = frames
        self._count = 0
        self._open = False

    def open(self) -> bool:
        self._open = True
        return True

    def read(self):
        if not self._open or self._count >= self._frames:
            return None
        self._count += 1
        value = (self._count % 26) * 10
        return np.full((720, 1280, 3), value, dtype=np.uint8)

    def close(self) -> None:
        self._open = False

    @property
    def is_open(self) -> bool:
        return self._open


class RecordingOutput(VideoOutput):
    def __init__(self):
        self.sent = 0
        self.active = True
        self.last_frame = None

    def start(self) -> bool:
        self.active = True
        return True

    def send(self, frame) -> bool:
        self.sent += 1
        self.last_frame = frame
        return True

    def stop(self) -> None:
        self.active = False

    @property
    def is_active(self) -> bool:
        return self.active

    @property
    def backend_name(self) -> str:
        return "fake"

    @classmethod
    def available(cls) -> bool:
        return True


class PreviewPipelineTest(unittest.TestCase):
    def test_streams_frames_to_output_and_handler(self):
        source = FakeSource(frames=30)
        pipeline = PreviewPipeline(source)
        output = RecordingOutput()
        pipeline.add_output(output)

        seen = []
        pipeline.on_frame(lambda frame, fps: seen.append(frame))
        self.assertTrue(pipeline.start())

        time.sleep(0.8)
        pipeline.stop()

        self.assertGreater(output.sent, 0)
        self.assertGreater(len(seen), 0)
        self.assertEqual(output.last_frame.shape, (720, 1280, 3))
        self.assertFalse(pipeline.is_running)
        self.assertFalse(source.is_open)

    def test_current_frame_returns_processed_copy(self):
        source = FakeSource(frames=30)
        pipeline = PreviewPipeline(source)
        pipeline.processor.set_blur_hud(True)
        self.assertTrue(pipeline.start())

        time.sleep(0.5)
        frame = pipeline.current_frame()
        pipeline.stop()

        self.assertIsNotNone(frame)
        self.assertEqual(frame.shape, (720, 1280, 3))


if __name__ == "__main__":
    unittest.main()