"""Delegate customizado para tabelas com cores semanticas e selecao translucida."""

from __future__ import annotations

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QBrush, QColor, QPainter
from PySide6.QtWidgets import QStyle, QStyledItemDelegate, QStyleOptionViewItem


class SemanticTableDelegate(QStyledItemDelegate):
    """Delegate que preserva cores semanticas e aplica selecao translucida."""

    # Cores de seleção translucida (mais transparente)
    SELECTION_BG = QColor(33, 150, 243, 25)
    SELECTION_BG_HOVER = QColor(33, 150, 243, 40)
    SELECTION_BORDER = QColor(33, 150, 243, 100)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        """Pinta a celula preservando cores semanticas e aplicando overlay de selecao."""
        foreground = index.data(Qt.ItemDataRole.ForegroundRole)
        background = index.data(Qt.ItemDataRole.BackgroundRole)

        painter.save()

        # Desenha fundo semantico se existir
        if background and isinstance(background, (QBrush, QColor)):
            painter.fillRect(option.rect, background)
        else:
            painter.fillRect(option.rect, QColor("#ffffff"))

        # Desenha seleção translucida por cima (overlay)
        if option.state & QStyle.StateFlag.State_Selected:
            painter.fillRect(option.rect, self.SELECTION_BG)
            painter.setPen(self.SELECTION_BORDER)
            painter.drawRect(option.rect.adjusted(0, 0, -1, -1))

        # Desenha texto com cor semantica
        if foreground and isinstance(foreground, (QBrush, QColor)):
            color = foreground.color() if isinstance(foreground, QBrush) else foreground
            painter.setPen(color)
        else:
            if option.state & QStyle.StateFlag.State_Selected:
                painter.setPen(QColor("#1a1a1a"))
            else:
                painter.setPen(QColor("#333333"))

        text_rect = option.rect.adjusted(4, 2, -4, -2)
        alignment = Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter

        text = index.data(Qt.ItemDataRole.DisplayRole)
        if text:
            painter.drawText(text_rect, alignment, str(text))

        painter.restore()

    def initStyleOption(
        self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ) -> None:
        super().initStyleOption(option, index)


class CenteredTextDelegate(QStyledItemDelegate):
    """Delegate simples para centralizar texto."""

    def initStyleOption(
        self, option: QStyleOptionViewItem, index: QModelIndex | QPersistentModelIndex
    ) -> None:
        super().initStyleOption(option, index)
        option.displayAlignment = (
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
        )
