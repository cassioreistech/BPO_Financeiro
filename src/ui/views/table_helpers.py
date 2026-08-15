"""Helpers para padronizacao visual de tabelas QTableWidget."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem

# Altura padrao das linhas (px) - valor profissional e confortavel
DEFAULT_ROW_HEIGHT = 36


def configurar_tabela_padrao(tabela: QTableWidget) -> None:
    """Aplica configuracao visual padrao a uma QTableWidget."""
    tabela.setAlternatingRowColors(True)
    tabela.verticalHeader().setVisible(False)
    tabela.horizontalHeader().setStretchLastSection(True)
    tabela.horizontalHeader().setSectionResizeMode(
        QHeaderView.ResizeMode.Stretch
    )
    tabela.setSelectionBehavior(
        QTableWidget.SelectionBehavior.SelectRows
    )
    tabela.setSelectionMode(
        QTableWidget.SelectionMode.SingleSelection
    )
    tabela.setEditTriggers(
        QTableWidget.EditTrigger.NoEditTriggers
    )
    tabela.setAlternatingRowColors(True)
    tabela.verticalHeader().setVisible(False)
    tabela.horizontalHeader().setStretchLastSection(True)
    tabela.horizontalHeader().setSectionResizeMode(
        QHeaderView.ResizeMode.Stretch
    )
    # Centralizar cabecalhos
    tabela.horizontalHeader().setDefaultAlignment(
        Qt.AlignmentFlag.AlignCenter
    )
    # Altura padrao das linhas
    tabela.verticalHeader().setDefaultSectionSize(DEFAULT_ROW_HEIGHT)
    tabela.verticalHeader().setMinimumSectionSize(DEFAULT_ROW_HEIGHT)


def criar_item_centralizado(texto: str) -> QTableWidgetItem:
    """Cria QTableWidgetItem com texto centralizado."""
    item = QTableWidgetItem(texto)
    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    return item


def criar_item(texto: str, centralizado: bool = False) -> QTableWidgetItem:
    """Cria QTableWidgetItem opcionalmente centralizado."""
    item = QTableWidgetItem(texto)
    if centralizado:
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    return item


def aplicar_altura_linhas(tabela: QTableWidget, altura: int = DEFAULT_ROW_HEIGHT) -> None:
    """Define altura padrao para todas as linhas existentes e futuras."""
    tabela.verticalHeader().setDefaultSectionSize(altura)
    tabela.verticalHeader().setMinimumSectionSize(altura)
    for row in range(tabela.rowCount()):
        tabela.setRowHeight(row, altura)
