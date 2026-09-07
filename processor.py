import cv2
import numpy as np


class HUDRemover:
    def __init__(self):
        self._roi_x = 0
        self._roi_y = 0
        self._roi_w = 0
        self._roi_h = 0
        self._crop_enabled = False
        self._blur_hud = False
        self._custom_mask = None
        self._hud_regions = []
        self._target_width = 1280
        self._target_height = 720

    def set_target_resolution(self, width, height):
        self._target_width = width
        self._target_height = height

    def set_crop_region(self, x, y, w, h):
        self._roi_x = x
        self._roi_y = y
        self._roi_w = w
        self._roi_h = h
        self._crop_enabled = True

    def set_auto_crop_enabled(self, enabled):
        self._crop_enabled = enabled

    def set_blur_hud(self, enabled):
        self._blur_hud = enabled

    def add_hud_region(self, x, y, w, h):
        self._hud_regions.append((x, y, w, h))

    def clear_hud_regions(self):
        self._hud_regions.clear()

    def process_frame(self, frame):
        if frame is None:
            return None

        processed = frame.copy()

        if self._crop_enabled and self._roi_w > 0 and self._roi_h > 0:
            processed = self._apply_crop(processed)

        if self._blur_hud:
            processed = self._apply_hud_blur(processed)

        if self._custom_mask is not None:
            processed = self._apply_mask(processed)

        processed = self._ensure_resolution(processed)

        return processed

    def _apply_crop(self, frame):
        h, w = frame.shape[:2]
        x = max(0, min(self._roi_x, w - 1))
        y = max(0, min(self._roi_y, h - 1))
        cw = min(self._roi_w, w - x)
        ch = min(self._roi_h, h - y)

        if cw <= 0 or ch <= 0:
            return frame

        return frame[y:y+ch, x:x+cw]

    def _apply_hud_blur(self, frame):
        h, w = frame.shape[:2]

        default_hud_regions = [
            (0, 0, w, int(h * 0.05)),
            (0, h - int(h * 0.05), w, int(h * 0.05)),
            (0, 0, int(w * 0.15), h),
            (w - int(w * 0.15), 0, int(w * 0.15), h),
            (int(w * 0.35), int(h * 0.40), int(w * 0.30), int(h * 0.20)),
        ]

        regions = default_hud_regions + self._hud_regions

        for (rx, ry, rw, rh) in regions:
            rx = max(0, min(rx, w - 1))
            ry = max(0, min(ry, h - 1))
            rw = min(rw, w - rx)
            rh = min(rh, h - ry)

            if rw > 0 and rh > 0:
                roi = frame[ry:ry+rh, rx:rx+rw]
                blurred = cv2.GaussianBlur(roi, (51, 51), 30)
                frame[ry:ry+rh, rx:rx+rw] = blurred

        return frame

    def _apply_mask(self, frame):
        if self._custom_mask is None:
            return frame

        mask = self._custom_mask
        if mask.shape[:2] != frame.shape[:2]:
            mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))

        if len(mask.shape) == 2:
            mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        black = np.zeros_like(frame)
        result = np.where(mask > 0, frame, black)
        return result.astype(np.uint8)

    def _ensure_resolution(self, frame):
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

        return resized[y_offset:y_offset+self._target_height, x_offset:x_offset+self._target_width]

    def remove_hud_overlay(self, frame):
        h, w = frame.shape[:2]

        top_bar = int(h * 0.06)
        bottom_bar = int(h * 0.06)
        left_bar = int(w * 0.04)
        right_bar = int(w * 0.04)

        result = frame.copy()

        overlay_color = (0, 0, 0)

        result[0:top_bar, :] = overlay_color
        result[h-bottom_bar:h, :] = overlay_color
        result[:, 0:left_bar] = overlay_color
        result[:, w-right_bar:w] = overlay_color

        cx, cy = w // 2, h // 2
        cv2.drawMarker(
            result,
            (cx, cy),
            (255, 255, 255),
            cv2.MARKER_CROSS,
            20,
            1
        )

        return result

    def paint_over_hud(self, frame, regions, color=(0, 0, 0)):
        result = frame.copy()
        for (x, y, w, h) in regions:
            result[y:y+h, x:x+w] = color
        return result

    def detect_hud_text_regions(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        regions = []
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
