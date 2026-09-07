"""Localiza e carrega o EDSDK.dll, vinculando as funções usadas via ctypes."""

from __future__ import annotations

import ctypes
import os
import sys
from pathlib import Path
from typing import List, Set, Tuple


class EDSDKLoader:
    """Descobre a DLL em locais conhecidos e registra os protótipos ctypes."""

    def __init__(self, dll_path: str = ""):
        self._dll_path = dll_path
        self._callback_refs: List[object] = []

    # ------------------------------------------------------------------
    # Descoberta da DLL
    # ------------------------------------------------------------------
    def find_dll(self) -> str:
        if self._dll_path and os.path.exists(self._dll_path):
            return self._dll_path

        if self._dll_path:
            raise FileNotFoundError(f"EDSDK.dll não encontrada no caminho: {self._dll_path}")

        project_dir = Path(__file__).resolve().parents[3]
        search_paths: List[str] = [
            str(project_dir / "libs" / "EDSDK.dll"),
            str(project_dir / "EDSDK.dll"),
            str(Path(__file__).resolve().parents[1] / "EDSDK.dll"),
        ]

        if sys.platform == "win32":
            program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
            program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
            app_data = os.environ.get("APPDATA", "")

            search_paths.extend([
                os.path.join(program_files, "Canon", "EOS Webcam Utility Pro", "EDSDK.dll"),
                os.path.join(program_files, "Canon", "EOS Webcam Utility", "EDSDK.dll"),
                os.path.join(program_files, "Canon", "EDSDK", "Library", "DLL", "EDSDK.dll"),
                os.path.join(program_files, "Canon", "EOS Utility", "EDSDK.dll"),
                os.path.join(program_files, "Canon", "EOS Utility", "bin", "EDSDK.dll"),
                os.path.join(program_files_x86, "Canon", "EDSDK", "Library", "DLL", "EDSDK.dll"),
                os.path.join(program_files_x86, "Canon", "EOS Utility", "EDSDK.dll"),
                os.path.join(program_files_x86, "Canon", "EOS Utility", "bin", "EDSDK.dll"),
                os.path.join(program_files_x86, "Canon", "EOS Webcam Utility", "EDSDK.dll"),
                os.path.join(app_data, "Canon", "EDSDK", "EDSDK.dll"),
            ])

            for root in (Path(program_files), Path(program_files_x86)):
                if root.exists():
                    for path in root.rglob("EDSDK.dll"):
                        search_paths.append(str(path))

        for path in search_paths:
            if os.path.exists(path):
                return path

        raise FileNotFoundError(
            "Canon EDSDK.dll não foi encontrada. Instale o Canon EOS Utility ou "
            "baixe o EDSDK no site de desenvolvedores da Canon.\n"
            + "\n".join(f"  - {p}" for p in search_paths[:10])
        )

    # ------------------------------------------------------------------
    # Vinculação de funções
    # ------------------------------------------------------------------
    def load_and_bind(self) -> Tuple[ctypes.WinDLL, Set[str]]:
        path = self.find_dll()
        dll = ctypes.WinDLL(path)

        available: Set[str] = set()

        def setup_func(name, restype=None, argtypes=None):
            try:
                func = getattr(dll, name)
                if restype is not None:
                    func.restype = restype
                if argtypes is not None:
                    func.argtypes = argtypes
                available.add(name)
                return True
            except AttributeError:
                return False

        c_uint32 = ctypes.c_uint32
        c_int32 = ctypes.c_int32
        c_int64 = ctypes.c_int64
        c_void_p = ctypes.c_void_p
        POINTER = ctypes.POINTER

        setup_func("EdsInitializeSDK", c_uint32, [])
        setup_func("EdsTerminateSDK", c_uint32, [])
        setup_func("EdsGetCameraList", c_uint32, [POINTER(c_void_p)])
        setup_func("EdsGetChildCount", c_uint32, [c_void_p, POINTER(c_uint32)])
        setup_func("EdsGetChildAtIndex", c_uint32, [c_void_p, c_int32, POINTER(c_void_p)])
        setup_func("EdsOpenSession", c_uint32, [c_void_p])
        setup_func("EdsCloseSession", c_uint32, [c_void_p])
        setup_func("EdsRelease", c_uint32, [c_void_p])
        setup_func("EdsSendCommand", c_uint32, [c_void_p, c_uint32, c_int32])
        setup_func("EdsSendStatusCommand", c_uint32, [c_void_p, c_uint32, c_int32])
        setup_func("EdsGetPropertySize", c_uint32, [
            c_void_p, c_uint32, c_int32,
            POINTER(c_uint32), POINTER(c_uint32),
        ])
        setup_func("EdsGetPropertyData", c_uint32, [
            c_void_p, c_uint32, c_int32, c_uint32, c_void_p,
        ])
        setup_func("EdsSetPropertyData", c_uint32, [
            c_void_p, c_uint32, c_int32, c_uint32, c_void_p,
        ])
        setup_func("EdsGetPropertyDesc", c_uint32, [c_void_p, c_uint32, c_void_p])
        setup_func("EdsCreateEvfImageRef", c_uint32, [c_void_p, POINTER(c_void_p)])
        setup_func("EdsGetPointer", c_uint32, [c_void_p, POINTER(c_void_p)])
        setup_func("EdsGetLength", c_uint32, [c_void_p, POINTER(c_uint32)])
        setup_func("EdsGetEvfImageSize", c_uint32, [
            c_void_p, POINTER(c_uint32), POINTER(c_uint32),
        ])
        setup_func("EdsCreateMemoryStream", c_uint32, [c_int64, POINTER(c_void_p)])
        setup_func("EdsGetDirectoryItemSize", c_uint32, [c_void_p, POINTER(c_uint32)])
        setup_func("EdsGetDirectoryItemData", c_uint32, [
            c_void_p, c_uint32, c_void_p, POINTER(c_uint32),
        ])
        setup_func("EdsSetEventHandler", c_uint32, [c_void_p, c_uint32, c_void_p, c_void_p])
        setup_func("EdsSetCameraAddedHandler", c_uint32, [c_void_p, c_void_p])
        setup_func("EdsSetObjectEventHandler", c_uint32, [
            c_void_p, c_uint32, c_void_p, c_void_p,
        ])
        setup_func("EdsSetPropertyEventHandler", c_uint32, [
            c_void_p, c_uint32, c_void_p, c_void_p,
        ])
        setup_func("EdsSetCameraStateEventHandler", c_uint32, [
            c_void_p, c_uint32, c_void_p, c_void_p,
        ])

        return dll, available