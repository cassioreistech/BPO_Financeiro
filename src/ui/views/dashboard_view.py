"""Tela de dashboard financeiro com indicadores e grafico."""

from __future__ import annotations

from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from application.use_cases.dashboard_use_cases import ResumoFinanceiroUseCase
from application.use_cases.escritorio_use_cases import ListarEscritoriosUseCase


class GraficoBarrasWidget(QWidget):
    """Widget customizado que desenha um grafico de barras simples."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._dados: list[tuple[str, Decimal, QColor]] = []
        self.setMinimumHeight(260)

    def definir_dados(self, dados: list[tuple[str, Decimal, QColor]]) -> None:
        self._dados = dados
        self.update()

    def paintEvent(self, event: object) -> None:  # noqa: ARG002
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(40, 30, -20, -50)
        painter.fillRect(rect, QColor("#f8f9fa"))

        if not self._dados:
            painter.setPen(QPen(QColor("#666666")))
            painter.drawText(
                self.rect(), Qt.AlignmentFlag.AlignCenter, "Sem dados para exibir"
            )
            return

        valores = [float(v) for _, v, _ in self._dados]
        maximo = max(valores) if max(valores) > 0 else 1.0
        bar_count = len(self._dados)
        spacing = 24
        bar_width = max(30, (rect.width() - spacing * (bar_count + 1)) // bar_count)

        painter.setPen(QPen(QColor("#333333")))
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        for i, (rotulo, valor, cor) in enumerate(self._dados):
            altura = (float(valor) / maximo) * rect.height()
            x = rect.left() + spacing + i * (bar_width + spacing)
            y = rect.bottom() - int(altura)

            bar_rect = self.rect().__class__(x, y, bar_width, int(altura))
            painter.fillRect(bar_rect, cor)
            painter.setPen(QPen(QColor("#333333")))
            painter.drawRect(bar_rect)

            valor_texto = self._formatar_valor(valor)
            painter.drawText(
                x,
                y - 20,
                bar_width,
                18,
                Qt.AlignmentFlag.AlignCenter,
                valor_texto,
            )
            painter.drawText(
                x,
                rect.bottom() + 8,
                bar_width,
                20,
                Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
                rotulo,
            )

    @staticmethod
    def _formatar_valor(valor: Decimal) -> str:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class DashboardView(QWidget):
    """Dashboard financeiro com cards de indicadores e grafico."""

    def __init__(
        self,
        resumo: ResumoFinanceiroUseCase,
        listar_escritorios: ListarEscritoriosUseCase,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._resumo = resumo
        self._listar_escritorios = listar_escritorios
        self._cards: dict[str, QLabel] = {}
        self._montar()
        self._carregar_escritorios()

    def _montar(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        cabecalho = QHBoxLayout()
        titulo = QLabel("Dashboard Financeiro")
        titulo.setObjectName("viewTitulo")
        cabecalho.addWidget(titulo)
        cabecalho.addStretch()

        cabecalho.addWidget(QLabel("Escritorio:"))
        self._combo_escritorio = QComboBox()
        self._combo_escritorio.setMinimumWidth(220)
        self._combo_escritorio.currentIndexChanged.connect(self._atualizar)
        cabecalho.addWidget(self._combo_escritorio)

        btn_atualizar = QPushButton("Atualizar")
        btn_atualizar.clicked.connect(self._atualizar)
        cabecalho.addWidget(btn_atualizar)

        layout.addLayout(cabecalho)

        grid = QGridLayout()
        grid.setSpacing(12)

        self._cards["a_receber"] = self._criar_card(
            "A Receber", "#1565c0", "#e3f2fd"
        )
        self._cards["a_pagar"] = self._criar_card(
            "A Pagar", "#c62828", "#ffebee"
        )
        self._cards["recebido"] = self._criar_card(
            "Recebido", "#2e7d32", "#e8f5e9"
        )
        self._cards["pago"] = self._criar_card("Pago", "#6a1b9a", "#f3e5f5")
        self._cards["vencido_receber"] = self._criar_card(
            "Vencido a Receber", "#ef6c00", "#fff3e0"
        )
        self._cards["vencido_pagar"] = self._criar_card(
            "Vencido a Pagar", "#ad1457", "#fce4ec"
        )

        grid.addWidget(self._cards["a_receber"], 0, 0)
        grid.addWidget(self._cards["a_pagar"], 0, 1)
        grid.addWidget(self._cards["recebido"], 0, 2)
        grid.addWidget(self._cards["pago"], 1, 0)
        grid.addWidget(self._cards["vencido_receber"], 1, 1)
        grid.addWidget(self._cards["vencido_pagar"], 1, 2)

        layout.addLayout(grid)

        grafico_titulo = QLabel("Resumo por Categoria")
        grafico_titulo.setObjectName("sectionTitle")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        grafico_titulo.setFont(font)
        layout.addWidget(grafico_titulo)

        self._grafico = GraficoBarrasWidget()
        layout.addWidget(self._grafico)

    def _criar_card(self, titulo: str, cor_texto: str, cor_fundo: str) -> QLabel:
        valor_inicial = self._formatar_valor(Decimal("0"))
        card = QLabel(
            f"<b>{titulo}</b><br><span style='font-size:18px;'>{valor_inicial}</span>"
        )
        card.setWordWrap(True)
        card.setTextFormat(Qt.TextFormat.RichText)
        card.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card.setStyleSheet(
            f"""
            QLabel {{
                background-color: {cor_fundo};
                color: {cor_texto};
                border-radius: 8px;
                padding: 16px;
                border: 1px solid {cor_texto};
            }}
            """
        )
        card.setMinimumHeight(90)
        return card

    def _carregar_escritorios(self) -> None:
        try:
            escritorios = self._listar_escritorios.execute(skip=0, limit=1000)
        except Exception as e:
            QMessageBox.warning(
                self, "Erro", f"Erro ao carregar escritorios: {e}"
            )
            return

        self._combo_escritorio.blockSignals(True)
        self._combo_escritorio.clear()
        self._combo_escritorio.addItem("Selecione...", None)
        for esc in escritorios:
            if esc.id is not None:
                self._combo_escritorio.addItem(esc.nome, esc.id)
        self._combo_escritorio.blockSignals(False)

    def _atualizar(self) -> None:
        escritorio_id = self._combo_escritorio.currentData()
        if escritorio_id is None:
            self._limpar_cards()
            self._grafico.definir_dados([])
            return

        try:
            resumo = self._resumo.execute(escritorio_id)
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao carregar resumo: {e}")
            return

        self._atualizar_card("a_receber", "A Receber", resumo.a_receber)
        self._atualizar_card("a_pagar", "A Pagar", resumo.a_pagar)
        self._atualizar_card("recebido", "Recebido", resumo.recebido)
        self._atualizar_card("pago", "Pago", resumo.pago)
        self._atualizar_card(
            "vencido_receber", "Vencido a Receber", resumo.vencido_receber
        )
        self._atualizar_card(
            "vencido_pagar", "Vencido a Pagar", resumo.vencido_pagar
        )

        dados = [
            ("A Receber", resumo.a_receber, QColor("#1565c0")),
            ("A Pagar", resumo.a_pagar, QColor("#c62828")),
            ("Recebido", resumo.recebido, QColor("#2e7d32")),
            ("Pago", resumo.pago, QColor("#6a1b9a")),
        ]
        self._grafico.definir_dados(dados)

    def _atualizar_card(self, chave: str, titulo: str, valor: Decimal) -> None:
        self._cards[chave].setText(
            f"<b>{titulo}</b><br><span style='font-size:18px;'>{self._formatar_valor(valor)}</span>"
        )

    def _limpar_cards(self) -> None:
        for chave, card in self._cards.items():
            titulo = card.text().split("<br>")[0].replace("<b>", "").replace("</b>", "")
            self._atualizar_card(chave, titulo, Decimal("0"))

    @staticmethod
    def _formatar_valor(valor: Decimal) -> str:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
