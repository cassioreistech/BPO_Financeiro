"""Tela de dashboard financeiro com indicadores e grafico."""

from __future__ import annotations

from datetime import date
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
    QTableWidget,
    QTableWidgetItem,
    QToolTip,
    QVBoxLayout,
    QWidget,
)

from application.dto.empresa_dto import EmpresaResponseDTO
from application.services.empresa_context_service import EmpresaContextService
from application.use_cases.dashboard_use_cases import ResumoFinanceiroUseCase
from application.use_cases.empresa_use_cases import ListarEmpresasUseCase
from application.use_cases.escritorio_use_cases import ListarEscritoriosUseCase
from domain.entities.titulo import Titulo
from ui.views.table_helpers import (
    configurar_tabela_padrao,
    criar_item_centralizado,
)


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

    CORES_CATEGORIA = [
        QColor("#1565c0"),
        QColor("#c62828"),
        QColor("#2e7d32"),
        QColor("#6a1b9a"),
        QColor("#ef6c00"),
        QColor("#ad1457"),
    ]

    def __init__(
        self,
        resumo: ResumoFinanceiroUseCase,
        listar_escritorios: ListarEscritoriosUseCase,
        listar_empresas: ListarEmpresasUseCase,
        contexto_empresa: EmpresaContextService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._resumo = resumo
        self._listar_escritorios = listar_escritorios
        self._listar_empresas = listar_empresas
        self._contexto_empresa = contexto_empresa
        self._empresas: dict[int, EmpresaResponseDTO] = {}
        self._cards: dict[str, QLabel] = {}
        self._labels_tooltips: dict[str, tuple[str, str, str]] = {}
        self._montar()
        self._carregar_empresas()

    def _montar(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        cabecalho = QHBoxLayout()
        self._titulo = QLabel("Dashboard Financeiro")
        self._titulo.setObjectName("viewTitulo")
        cabecalho.addWidget(self._titulo)
        cabecalho.addStretch()

        cabecalho.addWidget(QLabel("Empresa:"))
        self._combo_empresa = QComboBox()
        self._combo_empresa.setMinimumWidth(280)
        self._combo_empresa.currentIndexChanged.connect(self._atualizar)
        cabecalho.addWidget(self._combo_empresa)

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
        self._cards["mes_receber"] = self._criar_card(
            "Total do Mes a Receber", "#00695c", "#e0f2f1"
        )
        self._cards["mes_pagar"] = self._criar_card(
            "Total do Mes a Pagar", "#d32f2f", "#ffebee"
        )

        grid.addWidget(self._cards["a_receber"], 0, 0)
        grid.addWidget(self._cards["a_pagar"], 0, 1)
        grid.addWidget(self._cards["recebido"], 0, 2)
        grid.addWidget(self._cards["pago"], 0, 3)
        grid.addWidget(self._cards["vencido_receber"], 1, 0)
        grid.addWidget(self._cards["vencido_pagar"], 1, 1)
        grid.addWidget(self._cards["mes_receber"], 1, 2)
        grid.addWidget(self._cards["mes_pagar"], 1, 3)

        for i in range(4):
            grid.setColumnStretch(i, 1)

        layout.addLayout(grid)

        grafico_titulo = QLabel("A Pagar/Receber por Categoria")
        grafico_titulo.setObjectName("sectionTitle")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        grafico_titulo.setFont(font)
        layout.addWidget(grafico_titulo)

        self._grafico = GraficoBarrasWidget()
        layout.addWidget(self._grafico)

        vencidos_titulo = QLabel("Titulos Vencidos (top 10)")
        vencidos_titulo.setObjectName("sectionTitle")
        vencidos_titulo.setFont(font)
        layout.addWidget(vencidos_titulo)

        self._tabela_vencidos = QTableWidget()
        self._tabela_vencidos.setColumnCount(5)
        self._tabela_vencidos.setHorizontalHeaderLabels(
            ["Vencimento", "Descricao", "Tipo", "Valor", "Dias"]
        )
        configurar_tabela_padrao(self._tabela_vencidos)
        layout.addWidget(self._tabela_vencidos)

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

    def _carregar_empresas(self) -> None:
        try:
            empresas = self._listar_empresas.execute(
                ativo=True, skip=0, limit=1000
            )
        except Exception as e:
            QMessageBox.warning(
                self, "Erro", f"Erro ao carregar empresas: {e}"
            )
            return

        self._empresas = {e.id: e for e in empresas if e.id is not None}

        self._combo_empresa.blockSignals(True)
        self._combo_empresa.clear()
        self._combo_empresa.addItem("Selecione...", None)
        for emp in empresas:
            if emp.id is not None:
                self._combo_empresa.addItem(emp.nome_fantasia, emp.id)

        empresa_ativa = self._contexto_empresa.get_empresa_ativa()
        if empresa_ativa is not None:
            idx = self._combo_empresa.findData(empresa_ativa)
            if idx >= 0:
                self._combo_empresa.setCurrentIndex(idx)

        self._combo_empresa.blockSignals(False)

    def carregar_empresa_ativa(self) -> None:
        """Recarrega o dashboard usando a empresa ativa do contexto global."""
        empresa_id = self._contexto_empresa.get_empresa_ativa()
        if empresa_id is None:
            return
        idx = self._combo_empresa.findData(empresa_id)
        if idx >= 0:
            self._combo_empresa.setCurrentIndex(idx)
        self._atualizar()

    def _atualizar(self) -> None:
        empresa_id = self._combo_empresa.currentData()
        if empresa_id is None:
            self._limpar_cards()
            self._grafico.definir_dados([])
            self._tabela_vencidos.setRowCount(0)
            self._titulo.setText("Dashboard Financeiro")
            return

        empresa = self._empresas.get(empresa_id)
        if empresa is None:
            QMessageBox.warning(self, "Erro", "Empresa nao encontrada.")
            return

        self._titulo.setText(f"Dashboard Financeiro — {empresa.nome_fantasia}")

        try:
            resumo = self._resumo.execute(
                escritorio_id=empresa.escritorio_id, empresa_id=empresa_id
            )
            por_categoria = self._resumo.resumo_por_categoria(
                escritorio_id=empresa.escritorio_id, empresa_id=empresa_id
            )
            vencidos = self._resumo.titulos_vencidos(
                escritorio_id=empresa.escritorio_id, empresa_id=empresa_id
            )
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
        self._atualizar_card(
            "mes_receber", "Total do Mes a Receber", resumo.total_mes_receber
        )
        self._atualizar_card(
            "mes_pagar", "Total do Mes a Pagar", resumo.total_mes_pagar
        )

        dados_grafico = [
            (item.categoria, item.total, self._cor_categoria(i))
            for i, item in enumerate(por_categoria)
        ]
        self._grafico.definir_dados(dados_grafico)

        self._atualizar_vencidos(vencidos)

    def _atualizar_vencidos(self, vencidos: list[Titulo]) -> None:
        self._tabela_vencidos.setRowCount(len(vencidos))
        hoje = date.today()
        for i, t in enumerate(vencidos):
            dias = (hoje - t.data_vencimento).days
            self._tabela_vencidos.setItem(
                i,
                0,
                criar_item_centralizado(
                    t.data_vencimento.strftime("%d/%m/%Y")
                ),
            )
            self._tabela_vencidos.setItem(i, 1, QTableWidgetItem(t.descricao))
            self._tabela_vencidos.setItem(
                i, 2, criar_item_centralizado(t.tipo.value)
            )
            self._tabela_vencidos.setItem(
                i,
                3,
                criar_item_centralizado(self._formatar_valor(t.valor)),
            )
            self._tabela_vencidos.setItem(
                i, 4, criar_item_centralizado(str(dias))
            )

    def _cor_categoria(self, indice: int) -> QColor:
        return self.CORES_CATEGORIA[indice % len(self.CORES_CATEGORIA)]

    def _atualizar_card(self, chave: str, titulo: str, valor: Decimal) -> None:
        valor_formatado = self._formatar_valor(valor)
        self._cards[chave].setText(
            f"<b>{titulo}</b><br><span style='font-size:18px;'>{valor_formatado}</span>"
        )
        self._cards[chave].setToolTip(f"{titulo}: {valor_formatado}")

    def _limpar_cards(self) -> None:
        for chave, card in self._cards.items():
            titulo = (
                card.text().split("<br>")[0].replace("<b>", "").replace("</b>", "")
            )
            self._atualizar_card(chave, titulo, Decimal("0"))

    @staticmethod
    def _formatar_valor(valor: Decimal) -> str:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
