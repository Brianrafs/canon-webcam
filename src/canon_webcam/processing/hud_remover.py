"""Remoção de HUD/overlay dos frames da câmera."""

from __future__ import annotations

from typing import List, Optional, Tuple

import cv2
import numpy as np

Region = Tuple[int, int, int, int]

_DEFAULT_TARGET = (1280, 720)


class HUDRemover:
    """Aplica blur, crop e máscara para remover HUD do feed."""

    def __init__(self, target_width: int = _DEFAULT_TARGET[0], target_height: int = _DEFAULT_TARGET[1]):
        self._target_width = target_width
        self._target_height = target_height

        self._roi = (0, 0, 0, 0)
        self._crop_enabled = False
        self._blur_hud = False
        self._custom_mask: Optional[np.ndarray] = None
        self._hud_regions: List[Region] = []

    # ------------------------------------------------------------------
    # Configuração
    # ------------------------------------------------------------------
    def set_target_resolution(self, width: int, height: int) -> None:
        self._target_width = width
        self._target_height = height

    def set_crop_region(self, x: int, y: int, w: int, h: int) -> None:
        self._roi = (x, y, w, h)
        self._crop_enabled = True

    def set_auto_crop_enabled(self, enabled: bool) -> None:
        self._crop_enabled = enabled

    def set_blur_hud(self, enabled: bool) -> None:
        self._blur_hud = enabled

    def set_custom_mask(self, mask: Optional[np.ndarray]) -> None:
        self._custom_mask = mask

    def add_hud_region(self, x: int, y: int, w: int, h: int) -> None:
        self._hud_regions.append((x, y, w, h))

    def clear_hud_regions(self) -> None:
        self._hud_regions.clear()

    # ------------------------------------------------------------------
    # Pipeline principal
    # ------------------------------------------------------------------
    def process_frame(self, frame: Optional[np.ndarray]) -> Optional[np.ndarray]:
        if frame is None:
            return None

        processed = frame.copy()

        if self._crop_enabled and self._roi[2] > 0 and self._roi[3] > 0:
            processed = self._apply_crop(processed)

        if self._blur_hud:
            processed = self._apply_hud_blur(processed)

        if self._custom_mask is not None:
            processed = self._apply_mask(processed)

        return self._ensure_resolution(processed)

    # ------------------------------------------------------------------
    # Operações internas
    # ------------------------------------------------------------------
    def _apply_crop(self, frame: np.ndarray) -> np.ndarray:
        h, w = frame.shape[:2]
        x, y, cw, ch = self._roi

        x = max(0, min(x, w - 1))
        y = max(0, min(y, h - 1))
        cw = min(cw, w - x)
        ch = min(ch, h - y)

        if cw <= 0 or ch <= 0:
            return frame

        return frame[y:y + ch, x:x + cw]

    def _apply_hud_blur(self, frame: np.ndarray) -> np.ndarray:
        h, w = frame.shape[:2]

        default_regions: List[Region] = [
            (0, 0, w, int(h * 0.05)),
            (0, h - int(h * 0.05), w, int(h * 0.05)),
            (0, 0, int(w * 0.15), h),
            (w - int(w * 0.15), 0, int(w * 0.15), h),
            (int(w * 0.35), int(h * 0.40), int(w * 0.30), int(h * 0.20)),
        ]

        for (rx, ry, rw, rh) in default_regions + self._hud_regions:
            rx = max(0, min(rx, w - 1))
            ry = max(0, min(ry, h - 1))
            rw = min(rw, w - rx)
            rh = min(rh, h - ry)

            if rw > 0 and rh > 0:
                roi = frame[ry:ry + rh, rx:rx + rw]
                blurred = cv2.GaussianBlur(roi, (51, 51), 30)
                frame[ry:ry + rh, rx:rx + rw] = blurred

        return frame

    def _apply_mask(self, frame: np.ndarray) -> np.ndarray:
        mask = self._custom_mask
        if mask is None:
            return frame

        if mask.shape[:2] != frame.shape[:2]:
            mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))

        if len(mask.shape) == 2:
            mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        black = np.zeros_like(frame)
        return np.where(mask > 0, frame, black).astype(np.uint8)

    def _ensure_resolution(self, frame: np.ndarray) -> np.ndarray:
        h, w = frame.shape[:2]
        if w == self._target_width and h == self._target_height:
            return frame

        src_aspect = w / h
        tgt_aspect = self._target_width / self._target_height

        if src_aspect > tgt_aspect:
            new_h = self._target_height
            new_w = int(new_h * src_aspect)
        else:
            new_w = self._target_width
            new_h = int(new_w / src_aspect)

        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

        x_offset = (new_w - self._target_width) // 2
        y_offset = (new_h - self._target_height) // 2

        return resized[y_offset:y_offset + self._target_height, x_offset:x_offset + self._target_width]

    # ------------------------------------------------------------------
    # Ferramentas auxiliares
    # ------------------------------------------------------------------
    def detect_hud_text_regions(self, frame: np.ndarray) -> List[Region]:
        """Detecta regiões claras nas bordas que provavelmente são HUD."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        regions: List[Region] = []
        h, w = frame.shape[:2]
        min_area = (w * h) * 0.001
        max_area = (w * h) * 0.05

        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area < area < max_area:
                x, y, cw, ch = cv2.boundingRect(contour)
                if y < h * 0.1 or y > h * 0.9 or x < w * 0.1 or x > w * 0.9:
                    regions.append((x, y, cw, ch))

        return regions