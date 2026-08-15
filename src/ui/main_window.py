"""Janela principal do sistema."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget


class MainWindow(QMainWindow):
    """Janela minima da fundacao do sistema."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Sistema BPO Financeiro")
        self.resize(1024, 640)

        widget_central = QWidget(self)
        layout = QVBoxLayout(widget_central)

        rotulo = QLabel("Sistema BPO Financeiro — Base inicial")
        rotulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(rotulo)

        self.setCentralWidget(widget_central)
