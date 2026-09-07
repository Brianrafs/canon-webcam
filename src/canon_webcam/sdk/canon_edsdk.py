"""Wrapper ao redor da API do Canon EDSDK via ctypes."""

from __future__ import annotations

import ctypes
import time
from typing import List, Optional, Set

import cv2
import numpy as np

from canon_webcam.sdk import constants as C
from canon_webcam.sdk.errors import check_result
from canon_webcam.sdk.loader import EDSDKLoader


class _PropDesc(ctypes.Structure):
    _fields_ = [
        ("PropID", ctypes.c_uint32),
        ("form", ctypes.c_int),
        ("numElements", ctypes.c_uint32),
        ("numElementsData", ctypes.c_uint32),
        ("PropDesc", ctypes.c_uint32 * 128),
    ]


class CanonEDSDK:
    """Gerencia ciclo de vida do SDK, sessão, Live View e propriedades."""

    def __init__(self, dll_path: str = ""):
        self._dll = None
        self._available: Set[str] = set()
        self._camera_ref = None
        self._live_view_active = False
        self._initialized = False

        loader = EDSDKLoader(dll_path)
        self._dll, self._available = loader.load_and_bind()

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------
    @property
    def available(self) -> Set[str]:
        return self._available

    @property
    def is_connected(self) -> bool:
        return self._camera_ref is not None

    def initialize(self) -> None:
        if self._initialized:
            return
        result = self._dll.EdsInitializeSDK()
        check_result(result, "Initialize SDK")
        self._initialized = True

    def terminate(self) -> None:
        if not self._initialized:
            return
        self.stop_live_view()
        if self._camera_ref:
            self._dll.EdsCloseSession(self._camera_ref)
            self._dll.EdsRelease(self._camera_ref)
            self._camera_ref = None
        self._dll.EdsTerminateSDK()
        self._initialized = False

    # ------------------------------------------------------------------
    # Descoberta de câmeras
    # ------------------------------------------------------------------
    def get_camera_list(self) -> List[dict]:
        camera_list = ctypes.c_void_p()
        check_result(self._dll.EdsGetCameraList(ctypes.byref(camera_list)), "Get camera list")

        count = ctypes.c_uint32(0)
        check_result(self._dll.EdsGetChildCount(camera_list, ctypes.byref(count)), "Get camera count")

        cameras: List[dict] = []
        for i in range(count.value):
            camera_ref = ctypes.c_void_p()
            check_result(
                self._dll.EdsGetChildAtIndex(camera_list, i, ctypes.byref(camera_ref)),
                f"Get camera at index {i}",
            )
            product_name = self._get_string_property(camera_ref, C.kEds_PropertyID_ProductName)
            body_id = self._get_string_property(camera_ref, C.kEds_PropertyID_BodyID)
            cameras.append({
                "ref": camera_ref,
                "name": product_name or f"Canon Camera {i}",
                "body_id": body_id or "Unknown",
            })

        self._dll.EdsRelease(camera_list)
        return cameras

    def connect(self, camera_index: int = 0) -> str:
        cameras = self.get_camera_list()
        if not cameras:
            from canon_webcam.sdk.errors import EdsError
            raise EdsError(
                0, "Nenhuma câmera Canon encontrada. Conecte a câmera via USB e ligue-a."
            )

        if camera_index >= len(cameras):
            camera_index = 0

        camera = cameras[camera_index]
        self._camera_ref = camera["ref"]

        check_result(self._dll.EdsOpenSession(self._camera_ref), "Open session")
        return camera["name"]

    def disconnect(self) -> None:
        if self._camera_ref:
            self.stop_live_view()
            self._dll.EdsCloseSession(self._camera_ref)
            self._dll.EdsRelease(self._camera_ref)
            self._camera_ref = None

    # ------------------------------------------------------------------
    # Leitura/escrita de propriedades
    # ------------------------------------------------------------------
    def get_property_u32(self, property_id: int, default: Optional[int] = None) -> Optional[int]:
        if not self._camera_ref:
            return default
        return self._get_int_property(self._camera_ref, property_id)

    def set_property_u32(self, property_id: int, value: int) -> int:
        if not self._camera_ref:
            return 0x00000002
        v = ctypes.c_uint32(value)
        return self._dll.EdsSetPropertyData(self._camera_ref, property_id, 0, 4, ctypes.byref(v))

    def get_property_desc(self, property_id: int) -> List[int]:
        if not self._camera_ref:
            return []
        d = _PropDesc()
        r = self._dll.EdsGetPropertyDesc(self._camera_ref, property_id, ctypes.byref(d))
        if r != 0 or d.numElements > 128:
            return []
        return list(d.PropDesc[: max(d.numElements, 0)])

    def get_label_for(self, property_id: int, value: int, table) -> str:
        label = table.get(value)
        return label if label is not None else f"0x{value:04X}"

    def _get_string_property(self, camera_ref, property_id: int) -> Optional[str]:
        try:
            size = ctypes.c_uint32(0)
            data_type = ctypes.c_uint32(0)
            result = self._dll.EdsGetPropertySize(
                camera_ref, property_id, 0, ctypes.byref(data_type), ctypes.byref(size)
            )
            if result != 0 or size.value == 0:
                return None

            buffer = ctypes.create_string_buffer(size.value)
            result = self._dll.EdsGetPropertyData(
                camera_ref, property_id, 0, size.value, buffer
            )
            if result != 0:
                return None

            return buffer.value.decode("utf-8", errors="replace").rstrip("\x00")
        except Exception:
            return None

    def _get_int_property(self, camera_ref, property_id: int) -> Optional[int]:
        try:
            size = ctypes.c_uint32(0)
            data_type = ctypes.c_uint32(0)
            result = self._dll.EdsGetPropertySize(
                camera_ref, property_id, 0, ctypes.byref(data_type), ctypes.byref(size)
            )
            if result != 0 or size.value == 0:
                return None

            value = ctypes.c_uint32(0)
            result = self._dll.EdsGetPropertyData(
                camera_ref, property_id, 0, size.value, ctypes.byref(value)
            )
            if result != 0:
                return None

            return value.value
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Comandos de câmera
    # ------------------------------------------------------------------
    def auto_focus(self, mode: int = C.kEdsEvfAf_ON) -> int:
        if not self._camera_ref:
            return 0x00000002
        return self._dll.EdsSendCommand(self._camera_ref, C.kEds_CameraCommand_DoEvfAf, mode)

    def drive_lens(self, direction: int) -> int:
        if not self._camera_ref:
            return 0x00000002
        return self._dll.EdsSendCommand(self._camera_ref, C.kEds_CameraCommand_DriveLensEvf, direction)

    def extend_shutdown_timer(self) -> int:
        if not self._camera_ref:
            return 0x00000002
        return self._dll.EdsSendCommand(self._camera_ref, C.kEds_CameraCommand_ExtendShutDownTimer, 0)

    def take_photo(self) -> int:
        if not self._camera_ref:
            return 0x00000002
        return self._dll.EdsSendCommand(self._camera_ref, C.kEds_CameraCommand_TakePicture, 0)

    def set_live_view_zoom(self, zoom: int) -> None:
        if self._camera_ref:
            self._dll.EdsSendCommand(self._camera_ref, 0x00000007, zoom)

    def get_battery_level(self) -> Optional[int]:
        if not self._camera_ref:
            return None
        return self._get_int_property(self._camera_ref, C.kEds_PropertyID_BatteryLevel)

    def get_camera_name(self) -> str:
        if not self._camera_ref:
            return "No camera"
        return self._get_string_property(self._camera_ref, C.kEds_PropertyID_ProductName) or "Canon Camera"

    # ------------------------------------------------------------------
    # Live View
    # ------------------------------------------------------------------
    def start_live_view(self) -> None:
        if not self._camera_ref:
            from canon_webcam.sdk.errors import EdsError
            raise EdsError(0, "Nenhuma câmera conectada")

        if "EdsSetPropertyData" in self._available:
            output_device = ctypes.c_uint32(C.kEds_EvfOutputDevice_PC)
            result = self._dll.EdsSetPropertyData(
                self._camera_ref,
                C.kEds_PropertyID_Evf_OutputDevice,
                0,
                ctypes.sizeof(output_device),
                ctypes.byref(output_device),
            )
            if result != 0:
                print(f"[EDSDK] WARNING: set EVF output device failed: 0x{result:08X}")

        last_error = None
        for attempt in range(3):
            result = self._dll.EdsSendCommand(
                self._camera_ref, C.kEds_CameraCommand_StartEvf, 0
            )
            if result == 0:
                self._live_view_active = True
                time.sleep(0.2)
                return
            last_error = result
            print(f"[EDSDK] Start Live View attempt {attempt + 1} failed: 0x{result:08X} (retrying)")
            time.sleep(0.3)

        check_result(last_error, "Start Live View")

    def stop_live_view(self) -> None:
        if not self._camera_ref or not self._live_view_active:
            return
        result = self._dll.EdsSendCommand(self._camera_ref, C.kEds_CameraCommand_EndEvf, 0)
        if result == 0:
            self._live_view_active = False

    def capture_live_view_frame(self):
        if not self._camera_ref or not self._live_view_active:
            return None

        try:
            evf_image_ref = ctypes.c_void_p()
            result = self._dll.EdsCreateEvfImageRef(self._camera_ref, ctypes.byref(evf_image_ref))
            if result != 0:
                return None

            stream_ref = ctypes.c_void_p()
            result = self._dll.EdsGetChildAtIndex(evf_image_ref, 0, ctypes.byref(stream_ref))
            if result != 0:
                self._dll.EdsRelease(evf_image_ref)
                return None

            pointer = ctypes.c_void_p()
            result = self._dll.EdsGetPointer(stream_ref, ctypes.byref(pointer))
            if result != 0:
                self._dll.EdsRelease(stream_ref)
                self._dll.EdsRelease(evf_image_ref)
                return None

            length = ctypes.c_uint32(0)
            result = self._dll.EdsGetLength(stream_ref, ctypes.byref(length))
            if result != 0 or length.value == 0:
                self._dll.EdsRelease(stream_ref)
                self._dll.EdsRelease(evf_image_ref)
                return None

            jpeg_data = ctypes.string_at(pointer, length.value)

            self._dll.EdsRelease(stream_ref)
            self._dll.EdsRelease(evf_image_ref)

            nparr = np.frombuffer(jpeg_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame

        except Exception as e:
            print(f"[EDSDK] Live View capture error: {e}")
            return None