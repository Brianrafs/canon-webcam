"""Contratos de saída de vídeo."""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class VideoOutput(ABC):
    """Destino para os frames processados (ex.: webcam virtual)."""

    @abstractmethod
    def start(self) -> bool:
        """Inicia o dispositivo de saída."""

    @abstractmethod
    def send(self, frame: np.ndarray) -> bool:
        """Envia um frame. Deve aceitar qualquer tamanho e converter."""

    @abstractmethod
    def stop(self) -> None:
        """Para e libera o dispositivo."""

    @property
    @abstractmethod
    def is_active(self) -> bool:
        """True enquanto o dispositivo estiver em execução."""

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Nome legível do backend usado."""

    @classmethod
    @abstractmethod
    def available(cls) -> bool:
        """True se o backend de saída estiver instalado no sistema."""