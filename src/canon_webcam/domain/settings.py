"""Configurações de exposição da câmera e suas tabelas de conversão."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from canon_webcam.sdk import constants as C


class ConversionTable(dict):
    """Tabela raw->label com busca reversa label->raw."""

    def label_for(self, code: int) -> Optional[str]:
        return self.get(code)

    def code_for(self, label: str) -> Optional[int]:
        for code, value in self.items():
            if value == label:
                return code
        return None

    @property
    def labels(self):
        return list(self.values())


class _ISO(ConversionTable):
    def __init__(self):
        super().__init__({
            0x00: "Auto", 0x18: "H", 0x28: "6", 0x30: "12", 0x38: "25",
            0x40: "50", 0x48: "100", 0x4B: "125", 0x4C: "160", 0x50: "200",
            0x53: "250", 0x54: "320", 0x58: "400", 0x5B: "500", 0x5C: "640",
            0x60: "800", 0x63: "1000", 0x64: "1250", 0x68: "1600", 0x6B: "2000",
            0x6C: "2500", 0x70: "3200", 0x73: "4000", 0x74: "5000", 0x78: "6400",
            0x7B: "8000", 0x7C: "10000", 0x80: "12800", 0x83: "16000",
            0x84: "20000", 0x88: "25600", 0x90: "51200", 0x98: "102400",
        })


class _AV(ConversionTable):
    def __init__(self):
        super().__init__({
            0x08: "1", 0x0B: "1.1", 0x0E: "1.2", 0x13: "1.4", 0x14: "1.6",
            0x18: "1.8", 0x1B: "2", 0x1C: "2.2", 0x20: "2.5", 0x23: "2.8",
            0x24: "3.2", 0x28: "3.5", 0x2B: "4", 0x2E: "4.5", 0x33: "5",
            0x34: "5.6", 0x38: "6.3", 0x3B: "7.1", 0x40: "8", 0x43: "9",
            0x44: "10", 0x48: "11", 0x4B: "13", 0x50: "14", 0x53: "16",
            0x58: "18", 0x5B: "20", 0x60: "22", 0x63: "25", 0x68: "29",
            0x6B: "32", 0x70: "36", 0x73: "40", 0x78: "45", 0x7B: "51",
            0x80: "57", 0x83: "64", 0x88: "72", 0x8B: "81", 0x90: "91",
        })


class _TV(ConversionTable):
    def __init__(self):
        super().__init__({
            0x0C: "30\"", 0x10: "25\"", 0x13: "20\"", 0x14: "15\"", 0x18: "13\"",
            0x1B: "10\"", 0x1C: "8\"", 0x20: "6\"", 0x23: "5\"", 0x24: "4\"",
            0x28: "3.2\"", 0x2B: "2.5\"", 0x2C: "2\"", 0x30: "1.6\"", 0x33: "1.3\"",
            0x34: "1\"", 0x38: "0.8\"", 0x3B: "0.6\"", 0x3C: "0.5\"", 0x40: "0.4\"",
            0x43: "0.3\"", 0x44: "0.25\"", 0x48: "0.2\"", 0x4B: "0.16\"",
            0x4C: "1/8", 0x50: "1/10", 0x53: "1/13", 0x54: "1/15", 0x58: "1/20",
            0x5B: "1/25", 0x5C: "1/30", 0x60: "1/40", 0x63: "1/50", 0x64: "1/60",
            0x68: "1/80", 0x6B: "1/100", 0x6C: "1/125", 0x70: "1/160",
            0x73: "1/200", 0x74: "1/250", 0x78: "1/320", 0x7B: "1/400",
            0x7C: "1/500", 0x80: "1/640", 0x83: "1/800", 0x84: "1/1000",
            0x88: "1/1250", 0x8B: "1/1600", 0x8C: "1/2000", 0x90: "1/2500",
            0x93: "1/3200", 0x94: "1/4000", 0x98: "1/5000", 0x9B: "1/6400",
            0x9C: "1/8000",
        })


ISO_TABLE = _ISO()
AV_TABLE = _AV()
TV_TABLE = _TV()


@dataclass(frozen=True)
class ExposureSetting:
    """Uma configuração de exposição exposta pela interface."""

    key: str
    name: str
    property_id: int
    table: ConversionTable


EXPOSURE_SETTINGS = {
    "iso": ExposureSetting("iso", "ISO", C.kEds_PropertyID_ISOSpeed, ISO_TABLE),
    "av": ExposureSetting("av", "Aperture (Av)", C.kEds_PropertyID_Av, AV_TABLE),
    "tv": ExposureSetting("tv", "Shutter (Tv)", C.kEds_PropertyID_Tv, TV_TABLE),
}