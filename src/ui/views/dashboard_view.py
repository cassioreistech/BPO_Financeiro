"""Tela de dashboard financeiro com indicadores e grafico."""

from __future__ import annotations

from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QEnterEvent, QFont, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QToolTip,
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
        self.setMinimumHeight(280)

    def definir_dados(self, dados: list[tuple[str, Decimal, QColor]]) -> None:
        self._dados = dados
        self.update()

    def enterEvent(self, event: QEnterEvent) -> None:  # noqa: ARG002
        super().enterEvent(event)

    def _mapear_posicao_barra(self, i: int) -> tuple[int, int, int, int]:
        rect = self.rect().adjusted(50, 40, -30, -60)
        bar_count = len(self._dados)
        spacing = 20
        bar_width = max(30, (rect.width() - spacing * (bar_count + 1)) // bar_count)
        x = rect.left() + spacing + i * (bar_width + spacing)
        return x, bar_width, rect.bottom(), rect.height()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if not self._dados:
            return
        for i, (rotulo, valor, _) in enumerate(self._dados):
            x, bar_width, y_base, height = self._mapear_posicao_barra(i)
            maximo = max([float(v) for _, v, _ in self._dados]) or 1.0
            altura = (float(valor) / maximo) * height
            y = y_base - int(altura)
            if x <= event.x() <= x + bar_width and y <= event.y() <= y_base:
                QToolTip.showText(
                    event.globalPosition().toPoint(),
                    f"{rotulo}: {self._formatar_valor(valor)}",
                )
                return
        return super().mouseMoveEvent(event)

    def paintEvent(self, event: object) -> None:  # noqa: ARG002
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(50, 40, -30, -60)
        painter.fillRect(rect, QColor("#ffffff"))

        if not self._dados:
            painter.setPen(QPen(QColor("#999999")))
            font = QFont()
            font.setPointSize(11)
            painter.setFont(font)
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "Sem dados para exibir",
            )
            return

        valores = [float(v) for _, v, _ in self._dados]
        maximo = max(valores) if max(valores) > 0 else 1.0
        bar_count = len(self._dados)
        spacing = 20
        bar_width = max(30, (rect.width() - spacing * (bar_count + 1)) // bar_count)

        painter.setPen(QPen(QColor("#cccccc"), 1))
        gridlines = 5
        for g in range(1, gridlines + 1):
            y = rect.bottom() - int((rect.height() / gridlines) * g)
            painter.drawLine(rect.left(), y, rect.right(), y)
            valor_label = maximo * (g / gridlines)
            painter.setPen(QPen(QColor("#888888")))
            painter.setFont(QFont("Arial", 8))
            painter.drawText(
                rect.left() - 34,
                y - 6,
                30,
                12,
                Qt.AlignmentFlag.AlignRight,
                self._formatar_valor(Decimal(str(valor_label))),
            )

        painter.setPen(QPen(QColor("#333333")))
        painter.setFont(QFont("Arial", 9))
        painter.drawLine(rect.bottomLeft(), rect.bottomRight())

        label_font = QFont("Arial", 9, QFont.Weight.Bold)
        valor_font = QFont("Arial", 9, QFont.Weight.Bold)

        for i, (rotulo, valor, cor) in enumerate(self._dados):
            altura = (float(valor) / maximo) * rect.height()
            x = rect.left() + spacing + i * (bar_width + spacing)
            y = rect.bottom() - int(altura)

            painter.setBrush(cor)
            painter.setPen(QPen(Qt.GlobalColor.black, 0, Qt.PenStyle.SolidLine))
            painter.drawRect(x, y, bar_width, int(altura))

            cor_borda = cor.darker(130)
            painter.setPen(QPen(cor_borda, 1))
            painter.drawRect(x, y, bar_width, int(altura))

            valor_texto = self._formatar_valor(valor)
            painter.setPen(QPen(QColor("#333333")))
            painter.setFont(valor_font)
            painter.drawText(
                x,
                y - 18,
                bar_width,
                16,
                Qt.AlignmentFlag.AlignHCenter,
                valor_texto,
            )
            painter.setFont(label_font)
            painter.drawText(
                x,
                rect.bottom() + 8,
                bar_width,
                24,
                Qt.AlignmentFlag.AlignHCenter
                | Qt.TextFlag.TextWordWrap,
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
        self._labels_tooltips: dict[str, tuple[str, str, str]] = {}
        self._montar()
        self._carregar_escritorios()

    def _montar(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        cabecalho = QHBoxLayout()
        self._titulo = QLabel("Dashboard Financeiro")
        self._titulo.setObjectName("viewTitulo")
        cabecalho.addWidget(self._titulo)
        cabecalho.addStretch()

        cabecalho.addWidget(QLabel("Escritorio:"))
        self._combo_escritorio = QComboBox()
        self._combo_escritorio.setMinimumWidth(220)
        self._combo_escritorio.currentIndexChanged.connect(self._atualizar)
        cabecalho.addWidget(self._combo_escritorio)

        btn_atualizar = QPushButton("Atualizar")
        btn_atualizar.setIcon  # noqa: B018 - placeholder para future icon
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

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)

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
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setToolTip(f"{titulo}: {valor_inicial}")
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        card.setStyleSheet(
            f"""
            QLabel {{
                background-color: {cor_fundo};
                color: {cor_texto};
                border-radius: 10px;
                padding: 18px 16px;
                border: 1px solid {cor_texto}88;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            QLabel:hover {{
                background-color: {cor_fundo};
                border: 2px solid {cor_texto};
            }}
            """
        )
        card.setMinimumHeight(100)
        self._labels_tooltips[card.objectName() or titulo] = (
            titulo,
            cor_texto,
            cor_fundo,
        )
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
        escritorio_nome = (
            self._combo_escritorio.currentText()
            if escritorio_id is not None
            else "todos"
        )
        self._titulo.setText(f"Dashboard Financeiro — {escritorio_nome}")

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
        valor_formatado = self._formatar_valor(valor)
        self._cards[chave].setText(
            f"<b>{titulo}</b><br><span style='font-size:18px;'>{valor_formatado}</span>"
        )
        self._cards[chave].setToolTip(f"{titulo}: {valor_formatado}")

    def _limpar_cards(self) -> None:
        for chave, card in self._cards.items():
            titulo = card.text().split("<br>")[0].replace("<b>", "").replace("</b>", "")
            self._atualizar_card(chave, titulo, Decimal("0"))

    @staticmethod
    def _formatar_valor(valor: Decimal) -> str:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
