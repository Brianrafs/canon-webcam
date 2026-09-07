"""Contratos de captura de vídeo."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Tuple

import numpy as np


class CaptureSource(ABC):
    """Fonte que entrega frames BGR do feed da câmera."""

    @abstractmethod
    def open(self) -> bool:
        """Abre a fonte de captura. Deve ser idempotente."""

    @abstractmethod
    def read(self) -> Optional[np.ndarray]:
        """Retorna o próximo frame BGR, ou None quando indisponível."""

    @abstractmethod
    def close(self) -> None:
        """Fecha a fonte e libera recursos."""

    @property
    @abstractmethod
    def is_open(self) -> bool:
        """True quando a fonte está aberta e pronta para leitura."""

    @property
    def resolution(self) -> Optional[Tuple[int, int]]:
        return None