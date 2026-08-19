"""Tela de alertas e dashboard de vencimentos de titulos multiempresa."""

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
            str, tuple[QLabel, tuple[QLabel, QLabel]]
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
    ) -> tuple[QLabel, tuple[QLabel, QLabel]]:
        valor_inicial = "R$ 0,00"
        card = QLabel(
            f"<b>{titulo}</b><br>"
            f"<span style='font-size:14px;'>0 titulos</span><br>"
            f"<span style='font-size:18px;'>{valor_inicial}</span>"
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

        lbl_quantidade = QLabel("0 titulos")
        lbl_quantidade.setStyleSheet(f"color: {cor_texto}; border: none;")
        lbl_valor = QLabel(valor_inicial)
        font_valor = QFont()
        font_valor.setPointSize(14)
        font_valor.setBold(True)
        lbl_valor.setFont(font_valor)
        lbl_valor.setStyleSheet(f"color: {cor_texto}; border: none;")

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

    def obter_contagem_criticos(self) -> int:
        """Retorna a quantidade de titulos vencidos (criticos)."""
        try:
            filtro = FiltroAlertasTitulosDTO(
                empresa_id=None,
                data_referencia=date.today(),
                incluir_vencidos=True,
            )
            escritorios = self._listar_escritorios.execute(skip=0, limit=1)
            if not escritorios:
                return 0
            dashboard = self._dashboard_uc.execute(
                escritorio_id=escritorios[0].id,
                filtro=filtro,
            )
            return dashboard.vencidos.quantidade
        except Exception:
            return 0

    def _atualizar(self) -> None:
        filtro = FiltroAlertasTitulosDTO(
            empresa_id=None,
            data_referencia=date.today(),
            incluir_vencidos=True,
        )

        try:
            escritorios = self._listar_escritorios.execute(skip=0, limit=1)
            if not escritorios:
                self._limpar_dashboard()
                return
            escritorio_id = escritorios[0].id
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

    def _limpar_dashboard(self) -> None:
        titulos = {
            "CRITICO": "Vencidos",
            "ALTO": "Vence hoje",
            "MEDIO": "Vence amanha",
            "INFORMATIVO": "Esta semana",
        }
        for chave in self._cards:
            card = self._cards[chave][0]
            card.setText(
                f"<b>{titulos[chave]}</b><br>"
                f"<span style='font-size:14px;'>0 titulos</span><br>"
                f"<span style='font-size:18px;'>R$ 0,00</span>"
            )
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
        titulos = {
            "CRITICO": "Vencidos",
            "ALTO": "Vence hoje",
            "MEDIO": "Vence amanha",
            "INFORMATIVO": "Esta semana",
        }
        for chave, grupo in grupos.items():
            card = self._cards[chave][0]
            quantidade_texto = (
                f"{grupo.quantidade} "
                f"{'titulos' if grupo.quantidade != 1 else 'titulo'}"
            )
            valor_texto = self._formatar_valor(grupo.valor_total)
            card.setText(
                f"<b>{titulos[chave]}</b><br>"
                f"<span style='font-size:14px;'>{quantidade_texto}</span><br>"
                f"<span style='font-size:18px;'>{valor_texto}</span>"
            )
            card.setToolTip(f"{titulos[chave]}: {valor_texto}")

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
            item_empresa = QTableWidgetItem(item.empresa_nome.upper())
            font_empresa = item_empresa.font()
            font_empresa.setBold(True)
            item_empresa.setFont(font_empresa)
            self._tabela.setItem(i, 0, item_empresa)
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
