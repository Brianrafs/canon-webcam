"""Testes do processador de HUD e dos modelos de dispositivo."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import numpy as np  # noqa: E402

from canon_webcam.domain.devices import BackendKind, CameraDevice  # noqa: E402
from canon_webcam.processing.hud_remover import HUDRemover  # noqa: E402


def _make_frame():
    rng = np.random.default_rng(42)
    return rng.integers(0, 256, size=(720, 1280, 3), dtype=np.uint8)


class HUDRemoverTest(unittest.TestCase):
    def setUp(self):
        self.processor = HUDRemover()

    def test_process_none_returns_none(self):
        self.assertIsNone(self.processor.process_frame(None))

    def test_no_filters_is_identity(self):
        frame = _make_frame()
        out = self.processor.process_frame(frame)
        self.assertEqual(out.shape, (720, 1280, 3))
        np.testing.assert_array_equal(out, frame)

    def test_blur_changes_pixels_not_shape(self):
        self.processor.set_blur_hud(True)
        frame = _make_frame()
        out = self.processor.process_frame(frame)
        self.assertEqual(out.shape, frame.shape)
        self.assertFalse(np.array_equal(out, frame))

    def test_crop_region(self):
        self.processor.set_target_resolution(300, 200)
        self.processor.set_crop_region(100, 100, 300, 200)
        out = self.processor.process_frame(_make_frame())
        self.assertEqual(out.shape, (200, 300, 3))

    def test_target_resolution_letterbox(self):
        self.processor.set_target_resolution(640, 360)
        out = self.processor.process_frame(_make_frame())
        self.assertEqual(out.shape, (360, 640, 3))

    def test_detect_hud_regions_on_blank_dark_frame(self):
        frame = np.zeros((720, 1280, 3), dtype=np.uint8)
        self.assertEqual(self.processor.detect_hud_text_regions(frame), [])

    def test_add_and_clear_regions(self):
        self.processor.add_hud_region(0, 0, 10, 10)
        self.assertEqual(len(self.processor._hud_regions), 1)
        self.processor.clear_hud_regions()
        self.assertEqual(self.processor._hud_regions, [])


class CameraDeviceTest(unittest.TestCase):
    def test_label_with_detail_and_resolution(self):
        device = CameraDevice(
            index=0,
            backend=BackendKind.OPENCV,
            name="Canon T5i (EOS Webcam Utility)",
            detail="MSMF",
            resolution=(1280, 720),
        )
        self.assertIn("Canon T5i (EOS Webcam Utility)", device.label)
        self.assertIn("MSMF", device.label)
        self.assertIn("1280x720", device.label)


if __name__ == "__main__":
    unittest.main()