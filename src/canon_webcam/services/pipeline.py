"""Pipeline de captura: lê, processa e entrega frames em thread própria."""

from __future__ import annotations

import threading
import time
from typing import Callable, List, Optional

import numpy as np

from canon_webcam.capture.base import CaptureSource
from canon_webcam.output.base import VideoOutput
from canon_webcam.processing.hud_remover import HUDRemover

FrameHandler = Callable[[np.ndarray, float], None]


class PreviewPipeline:
    """Loop de captura/processamento até ser explicitamente interrompido."""

    def __init__(self, source: CaptureSource, processor: Optional[HUDRemover] = None):
        self._source = source
        self._processor = processor or HUDRemover()
        self._outputs: List[VideoOutput] = []
        self._frame_handler: Optional[FrameHandler] = None

        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._frame: Optional[np.ndarray] = None
        self._frame_lock = threading.Lock()
        self._fps = 0.0

    # ------------------------------------------------------------------
    # Configuração
    # ------------------------------------------------------------------
    @property
    def source(self) -> CaptureSource:
        return self._source

    @property
    def processor(self) -> HUDRemover:
        return self._processor

    def add_output(self, output: VideoOutput) -> None:
        self._outputs.append(output)

    def on_frame(self, handler: Optional[FrameHandler]) -> None:
        """Callback recebido na thread de captura a cada frame processado."""
        self._frame_handler = handler

    def current_frame(self) -> Optional[np.ndarray]:
        with self._frame_lock:
            return None if self._frame is None else self._frame.copy()

    @property
    def fps(self) -> float:
        return self._fps

    @property
    def is_running(self) -> bool:
        return self._running

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------
    def start(self) -> bool:
        if self._running:
            return True
        if not self._source.open():
            return False

        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        return True

    def stop(self, timeout: float = 3.0) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=timeout)
            self._thread = None
        self._source.close()

    # ------------------------------------------------------------------
    # Loop interno
    # ------------------------------------------------------------------
    def _loop(self) -> None:
        frame_count = 0
        start_time = time.time()

        while self._running:
            frame = self._read_frame()

            if frame is None:
                time.sleep(0.03)
                continue

            processed = self._processor.process_frame(frame)
            if processed is None:
                continue

            with self._frame_lock:
                self._frame = processed.copy()

            for output in self._outputs:
                if output.is_active:
                    output.send(processed)

            frame_count += 1

            elapsed = time.time() - start_time
            if elapsed >= 1.0:
                self._fps = frame_count / elapsed
                frame_count = 0
                start_time = time.time()

            if self._frame_handler is not None:
                self._frame_handler(processed, self._fps)

    def _read_frame(self):
        try:
            return self._source.read()
        except Exception as e:
            print(f"[Pipeline] Read error: {e}")
            return None