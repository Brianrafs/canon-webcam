"""Fontes de captura de vídeo."""

from canon_webcam.capture.base import CaptureSource
from canon_webcam.capture.edsdk_source import EdsdkSource
from canon_webcam.capture.factory import create_source
from canon_webcam.capture.opencv_source import OpenCVSource