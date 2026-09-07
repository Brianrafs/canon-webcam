"""Canon T5i Webcam - transforma a câmera DSLR em webcam virtual do OBS."""

__version__ = "0.2.0"

from canon_webcam.domain.devices import BackendKind, CameraDevice
from canon_webcam.domain.settings import EXPOSURE_SETTINGS, ConversionTable, ExposureSetting