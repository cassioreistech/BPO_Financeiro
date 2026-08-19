"""Tela de alertas e dashboard de vencimentos de titulos multiempresa."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import cast

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QDateEdit,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from application.dto.alerta_titulo_dto import (
    DashboardAlertasTitulosResponseDTO,
    FiltroAlertasTitulosDTO,
    ItemAlertaTituloResponseDTO,
)
from application.services.empresa_context_service import EmpresaContextService
from application.use_cases.alerta_titulo_use_cases import (
    ObterDashboardAlertasTitulosUseCase,
)
from application.use_cases.escritorio_use_cases import ListarEscritoriosUseCase
from ui.views.status_formatter import formatar_status_titulo
from ui.views.table_delegate import SemanticTableDelegate
from ui.views.table_helpers import (
    configurar_tabela_padrao,
    criar_item_centralizado,
)


class AlertasTitulosView(QWidget):
    """Dashboard de alertas de vencimentos de titulos."""

    COLUNAS = [
        "Empresa",
        "Descricao",
        "Categoria",
        "Documento",
        "Valor",
        "Vencimento",
        "Status",
        "Urgencia",
    ]

    CORES_URGENCIA = {
        "CRITICO": ("#b71c1c", "#ffcdd2"),
        "ALTO": ("#0d47a1", "#bbdefb"),
        "MEDIO": ("#0d47a1", "#bbdefb"),
        "INFORMATIVO": ("#1b5e20", "#a5d6a7"),
    }

    ROTULOS_GRUPOS = {
        "CRITICO": "Vencidos",
        "ALTO": "Vence hoje",
        "MEDIO": "Vence amanha",
        "INFORMATIVO": "Esta semana",
    }

    def __init__(
        self,
        dashboard_use_case: ObterDashboardAlertasTitulosUseCase,
        listar_escritorios: ListarEscritoriosUseCase,
        contexto_empresa: EmpresaContextService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._dashboard_uc = dashboard_use_case
        self._listar_escritorios = listar_escritorios
        self._contexto_empresa = contexto_empresa
        self._cards: dict[
            str, tuple[QWidget, tuple[QLabel, QLabel]]
        ] = {}
        self._montar()
        self._atualizar()

    def _montar(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # Cabecalho
        cabecalho = QHBoxLayout()
        titulo = QLabel("Alertas de Titulos")
        titulo.setObjectName("viewTitulo")
        cabecalho.addWidget(titulo)
        cabecalho.addStretch()

        cabecalho.addWidget(QLabel("Data referencia:"))
        self._date_referencia = QDateEdit()
        self._date_referencia.setCalendarPopup(True)
        hoje = date.today()
        self._date_referencia.setDate(QDate(hoje.year, hoje.month, hoje.day))
        self._date_referencia.dateChanged.connect(self._atualizar)
        cabecalho.addWidget(self._date_referencia)

        layout.addLayout(cabecalho)

        # Cards de resumo
        grid = QGridLayout()
        grid.setSpacing(12)

        self._cards["CRITICO"] = self._criar_card("Vencidos", "#c62828", "#ffebee")
        self._cards["ALTO"] = self._criar_card("Vence hoje", "#ef6c00", "#fff3e0")
        self._cards["MEDIO"] = self._criar_card("Vence amanha", "#1565c0", "#e3f2fd")
        self._cards["INFORMATIVO"] = self._criar_card(
            "Esta semana", "#2e7d32", "#e8f5e9"
        )

        grid.addWidget(self._cards["CRITICO"][0], 0, 0)
        grid.addWidget(self._cards["ALTO"][0], 0, 1)
        grid.addWidget(self._cards["MEDIO"][0], 0, 2)
        grid.addWidget(self._cards["INFORMATIVO"][0], 0, 3)

        for i in range(4):
            grid.setColumnStretch(i, 1)

        layout.addLayout(grid)

        # Total consolidado
        self._label_total = QLabel("Total: 0 titulo(s) — R$ 0,00")
        font_total = QFont()
        font_total.setPointSize(11)
        font_total.setBold(True)
        self._label_total.setFont(font_total)
        self._label_total.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self._label_total)

        # Tabela detalhada
        titulo_tabela = QLabel("Detalhamento")
        titulo_tabela.setObjectName("sectionTitle")
        font_secao = QFont()
        font_secao.setPointSize(12)
        font_secao.setBold(True)
        titulo_tabela.setFont(font_secao)
        layout.addWidget(titulo_tabela)

        self._tabela = QTableWidget()
        self._tabela.setColumnCount(len(self.COLUNAS))
        self._tabela.setHorizontalHeaderLabels(self.COLUNAS)
        configurar_tabela_padrao(self._tabela)
        self._tabela.setItemDelegate(SemanticTableDelegate(self._tabela))
        self._configurar_colunas_tabela()
        layout.addWidget(self._tabela, stretch=1)

    def _criar_card(
        self, titulo: str, cor_texto: str, cor_fundo: str
    ) -> tuple[QWidget, tuple[QLabel, QLabel]]:
        card = QWidget()
        card.setStyleSheet(
            f"""
            QWidget {{
                background-color: {cor_fundo};
                border: 1px solid {cor_texto}88;
                border-radius: 10px;
            }}
            """
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(4)

        lbl_titulo = QLabel(titulo)
        font_titulo = QFont()
        font_titulo.setPointSize(11)
        font_titulo.setBold(True)
        lbl_titulo.setFont(font_titulo)
        lbl_titulo.setStyleSheet(f"color: {cor_texto}; border: none;")
        layout.addWidget(lbl_titulo)

        lbl_quantidade = QLabel("0 titulos")
        lbl_quantidade.setStyleSheet(f"color: {cor_texto}; border: none;")
        layout.addWidget(lbl_quantidade)

        lbl_valor = QLabel("R$ 0,00")
        font_valor = QFont()
        font_valor.setPointSize(14)
        font_valor.setBold(True)
        lbl_valor.setFont(font_valor)
        lbl_valor.setStyleSheet(f"color: {cor_texto}; border: none;")
        layout.addWidget(lbl_valor)

        layout.addStretch()
        card.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        card.setMinimumHeight(110)

        return card, (lbl_quantidade, lbl_valor)

    def _configurar_colunas_tabela(self) -> None:
        from PySide6.QtWidgets import QHeaderView

        header = self._tabela.horizontalHeader()
        header.setStretchLastSection(False)

        larguras_fixas = {
            2: 130,  # Categoria
            3: 120,  # Documento
            4: 110,  # Valor
            5: 100,  # Vencimento
            6: 90,   # Status
            7: 110,  # Urgencia
        }
        for coluna, largura in larguras_fixas.items():
            header.setSectionResizeMode(coluna, QHeaderView.ResizeMode.Fixed)
            self._tabela.setColumnWidth(coluna, largura)

        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self._tabela.verticalHeader().setDefaultSectionSize(38)
        self._tabela.verticalHeader().setMinimumSectionSize(38)
        self._tabela.setMinimumHeight(300)

    def atualizar(self) -> None:
        """Atualiza os alertas de titulos."""
        self._atualizar()

    def _atualizar(self) -> None:
        escritorio_id = self._obter_escritorio_id()
        if escritorio_id is None:
            self._limpar_dashboard()
            return

        empresa_id = self._contexto_empresa.get_empresa_ativa()

        data_referencia = cast(
            date, self._date_referencia.date().toPython()
        )
        filtro = FiltroAlertasTitulosDTO(
            empresa_id=empresa_id,
            data_referencia=data_referencia,
            incluir_vencidos=True,
        )

        try:
            dashboard = self._dashboard_uc.execute(
                escritorio_id=escritorio_id,
                filtro=filtro,
            )
        except Exception as e:
            QMessageBox.warning(
                self, "Erro", f"Erro ao carregar alertas: {e}"
            )
            return

        self._atualizar_cards(dashboard)
        self._atualizar_tabela(dashboard)
        self._label_total.setText(
            f"Total: {dashboard.total_quantidade} titulo(s) — "
            f"{self._formatar_valor(dashboard.total_valor)}"
        )

    def _obter_escritorio_id(self) -> int | None:
        try:
            escritorios = self._listar_escritorios.execute(skip=0, limit=1)
        except Exception:
            return None
        if not escritorios:
            return None
        return escritorios[0].id

    def _limpar_dashboard(self) -> None:
        for chave in self._cards:
            lbl_quantidade, lbl_valor = self._cards[chave][1]
            lbl_quantidade.setText("0 titulos")
            lbl_valor.setText("R$ 0,00")
        self._tabela.setRowCount(0)
        self._label_total.setText("Total: 0 titulo(s) — R$ 0,00")

    def _atualizar_cards(
        self, dashboard: DashboardAlertasTitulosResponseDTO
    ) -> None:
        grupos = {
            "CRITICO": dashboard.vencidos,
            "ALTO": dashboard.vence_hoje,
            "MEDIO": dashboard.vence_amanha,
            "INFORMATIVO": dashboard.semana,
        }
        for chave, grupo in grupos.items():
            lbl_quantidade, lbl_valor = self._cards[chave][1]
            lbl_quantidade.setText(
                f"{grupo.quantidade} "
                f"{'titulos' if grupo.quantidade != 1 else 'titulo'}"
            )
            lbl_valor.setText(self._formatar_valor(grupo.valor_total))

    def _atualizar_tabela(
        self, dashboard: DashboardAlertasTitulosResponseDTO
    ) -> None:
        itens: list[ItemAlertaTituloResponseDTO] = []
        ordem = ["CRITICO", "ALTO", "MEDIO", "INFORMATIVO"]
        grupos = {
            "CRITICO": dashboard.vencidos,
            "ALTO": dashboard.vence_hoje,
            "MEDIO": dashboard.vence_amanha,
            "INFORMATIVO": dashboard.semana,
        }
        for chave in ordem:
            itens.extend(grupos[chave].itens)

        self._tabela.setRowCount(len(itens))
        for i, item in enumerate(itens):
            self._tabela.setItem(
                i, 0, QTableWidgetItem(item.empresa_nome)
            )
            self._tabela.setItem(i, 1, QTableWidgetItem(item.descricao))
            self._tabela.setItem(
                i, 2, criar_item_centralizado(item.categoria)
            )
            self._tabela.setItem(
                i,
                3,
                criar_item_centralizado(
                    item.numero_documento or "—"
                ),
            )
            self._tabela.setItem(
                i,
                4,
                criar_item_centralizado(self._formatar_valor(item.valor)),
            )
            self._tabela.setItem(
                i,
                5,
                criar_item_centralizado(
                    item.data_vencimento.strftime("%d/%m/%Y")
                ),
            )
            self._tabela.setItem(
                i,
                6,
                criar_item_centralizado(formatar_status_titulo(item.status, item.data_vencimento)),
            )
            self._tabela.setItem(
                i, 7, criar_item_centralizado(self.ROTULOS_GRUPOS[item.urgencia])
            )

            cor_texto, cor_fundo = self.CORES_URGENCIA[item.urgencia]
            for col in range(len(self.COLUNAS)):
                widget_item = self._tabela.item(i, col)
                if widget_item is not None:
                    widget_item.setForeground(QColor(cor_texto))
                    widget_item.setBackground(QColor(cor_fundo))

    @staticmethod
    def _formatar_valor(valor: Decimal) -> str:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
