"""Entrypoint do Sistema BPO Financeiro."""

import sys

from PySide6.QtWidgets import QApplication

from infrastructure.database import init_db
from infrastructure.logging_config import configure_logging
from ui.main_window import MainWindow
from ui.styles import APP_STYLESHEET


def main() -> int:
    """Inicializa logging, banco e interface do sistema."""
    configure_logging()
    init_db()

    app = QApplication(sys.argv)
    app.setApplicationName("Sistema BPO Financeiro")
    app.setStyleSheet(APP_STYLESHEET)

    janela = MainWindow()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
