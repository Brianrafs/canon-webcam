"""Testes das tabelas de conversão ISO/Av/Tv."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from canon_webcam.domain.settings import AV_TABLE, ISO_TABLE, TV_TABLE, EXPOSURE_SETTINGS  # noqa: E402


class ConversionTableTest(unittest.TestCase):
    def test_iso_code_for_reverse_lookup(self):
        self.assertEqual(ISO_TABLE.code_for("100"), 0x48)
        self.assertEqual(ISO_TABLE.code_for("Auto"), 0x00)

    def test_iso_label_for_known_code(self):
        self.assertEqual(ISO_TABLE.label_for(0x48), "100")
        self.assertEqual(ISO_TABLE.label_for(0x80), "12800")

    def test_av_round_trip(self):
        for code, label in AV_TABLE.items():
            self.assertEqual(AV_TABLE.code_for(label), code, f"Av {label}")

    def test_tv_round_trip(self):
        for code, label in TV_TABLE.items():
            self.assertEqual(TV_TABLE.code_for(label), code, f"Tv {label}")

    def test_lookup_unknown_returns_none(self):
        self.assertIsNone(ISO_TABLE.label_for(0x9999))
        self.assertIsNone(ISO_TABLE.code_for("inexistente"))

    def test_exposure_settings_registry(self):
        self.assertIn("iso", EXPOSURE_SETTINGS)
        self.assertIn("av", EXPOSURE_SETTINGS)
        self.assertIn("tv", EXPOSURE_SETTINGS)

        for key, setting in EXPOSURE_SETTINGS.items():
            self.assertEqual(setting.key, key)
            self.assertTrue(setting.table, f"tabela de {key}")
            self.assertGreater(setting.property_id, 0)


if __name__ == "__main__":
    unittest.main()