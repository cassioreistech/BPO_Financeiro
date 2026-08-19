"""Tela de dashboard financeiro com indicadores e grafico."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
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

from application.services.empresa_context_service import EmpresaContextService
from application.use_cases.dashboard_use_cases import ResumoFinanceiroUseCase
from application.use_cases.empresa_use_cases import ObterEmpresaUseCase
from domain.entities.titulo import Titulo
from infrastructure.database import SessionLocal
from infrastructure.database.repositories.sqlite_empresa_repository import (
    SQLiteEmpresaRepository,
)
from ui.views.table_helpers import (
    configurar_tabela_padrao,
    criar_item_centralizado,
)
from ui.views.table_delegate import SemanticTableDelegate


class DashboardView(QWidget):
    """Dashboard financeiro com cards de indicadores."""

    def __init__(
        self,
        resumo: ResumoFinanceiroUseCase,
        contexto_empresa: EmpresaContextService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._resumo = resumo
        self._contexto_empresa = contexto_empresa
        self._cards: dict[str, QLabel] = {}
        self._labels_tooltips: dict[str, tuple[str, str, str]] = {}
        self._montar()

    def _montar(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        cabecalho = QHBoxLayout()
        self._titulo = QLabel("Dashboard Financeiro")
        self._titulo.setObjectName("viewTitulo")
        cabecalho.addWidget(self._titulo)
        cabecalho.addStretch()

        self._label_empresa = QLabel("")
        self._label_empresa.setObjectName("labelEmpresaDashboard")
        self._label_empresa.setStyleSheet("color: #666; font-size: 13px;")
        cabecalho.addWidget(self._label_empresa)

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
            "Quitado a Receber", "#2e7d32", "#e8f5e9"
        )
        self._cards["pago"] = self._criar_card(
            "Quitado a Pagar", "#6a1b9a", "#f3e5f5"
        )
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

        font = QFont()
        font.setPointSize(12)
        font.setBold(True)

        vencidos_titulo = QLabel("Titulos Vencidos (top 10)")
        vencidos_titulo.setObjectName("sectionTitle")
        vencidos_titulo.setFont(font)
        layout.addWidget(vencidos_titulo)

        self._tabela_vencidos = QTableWidget()
        self._tabela_vencidos.setColumnCount(5)
        self._tabela_vencidos.setHorizontalHeaderLabels(
            ["Vencimento", "Descricao", "Tipo", "Valor", "Dias Vencidos"]
        )
        configurar_tabela_padrao(self._tabela_vencidos)
        self._tabela_vencidos.setItemDelegate(SemanticTableDelegate(self._tabela_vencidos))
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

    def carregar_empresa_ativa(self) -> None:
        """Recarrega o dashboard usando a empresa ativa do contexto global."""
        self.atualizar()

    def atualizar(self) -> None:
        """Atualiza os indicadores do dashboard."""
        self._atualizar()

    def _atualizar(self) -> None:
        empresa_id = self._contexto_empresa.get_empresa_ativa()
        if empresa_id is None:
            self._limpar_cards()
            self._tabela_vencidos.setRowCount(0)
            self._titulo.setText("Dashboard Financeiro")
            self._label_empresa.setText("Nenhuma empresa selecionada")
            return

        try:
            empresa_repo = SQLiteEmpresaRepository(SessionLocal)
            obter_empresa = ObterEmpresaUseCase(empresa_repo)
            empresa = obter_empresa.execute(empresa_id)
        except Exception:
            self._limpar_cards()
            self._tabela_vencidos.setRowCount(0)
            self._titulo.setText("Dashboard Financeiro")
            self._label_empresa.setText("Erro ao carregar empresa")
            return

        if empresa is None:
            self._limpar_cards()
            self._tabela_vencidos.setRowCount(0)
            self._titulo.setText("Dashboard Financeiro")
            self._label_empresa.setText("Empresa nao encontrada")
            return

        self._titulo.setText("Dashboard Financeiro")
        self._label_empresa.setText(
            f"{empresa.nome_fantasia}  —  CNPJ {self._formatar_cnpj(empresa.cnpj)}"
        )

        try:
            resumo = self._resumo.execute(
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
            item_desc = QTableWidgetItem(t.descricao.upper())
            item_desc.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font_desc = item_desc.font()
            font_desc.setBold(True)
            item_desc.setFont(font_desc)
            self._tabela_vencidos.setItem(i, 1, item_desc)
            self._tabela_vencidos.setItem(
                i, 2, criar_item_centralizado(t.tipo.value)
            )
            item_valor = QTableWidgetItem(self._formatar_valor(t.valor))
            item_valor.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            font_valor = item_valor.font()
            font_valor.setBold(True)
            font_valor.setPointSize(font_valor.pointSize() + 2)
            item_valor.setFont(font_valor)
            self._tabela_vencidos.setItem(i, 3, item_valor)
            item_dias = QTableWidgetItem(str(dias))
            item_dias.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item_dias.setForeground(QColor("#c62828"))
            font_dias = item_dias.font()
            font_dias.setBold(True)
            item_dias.setFont(font_dias)
            self._tabela_vencidos.setItem(i, 4, item_dias)

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

    @staticmethod
    def _formatar_cnpj(cnpj: str) -> str:
        if len(cnpj) != 14:
            return cnpj
        return (
            f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/"
            f"{cnpj[8:12]}-{cnpj[12:]}"
        )
