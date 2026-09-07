"""Entry point da aplicação GUI."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from canon_webcam.ui.app import CanonWebcamApp  # noqa: E402


def main():
    app = CanonWebcamApp()
    app.run()


if __name__ == "__main__":
    main()