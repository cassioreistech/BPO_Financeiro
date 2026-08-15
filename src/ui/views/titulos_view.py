"""Tela de listagem de Titulos financeiros."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from decimal import Decimal
from typing import Any, cast

from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from application.dto.titulo_dto import QuitarTituloDTO, TituloResponseDTO
from application.services.empresa_context_service import EmpresaContextService
from application.use_cases.conta_bancaria_use_cases import (
    ListarContasBancariasUseCase,
)
from application.use_cases.empresa_use_cases import ListarEmpresasUseCase
from application.use_cases.escritorio_use_cases import ListarEscritoriosUseCase
from application.use_cases.plano_conta_use_cases import GarantirContaPadraoUseCase
from application.use_cases.relatorio_titulos_use_cases import (
    FluxoCaixaUseCase,
    ProjecaoFinanceiraUseCase,
    RelatorioTitulosUseCase,
)
from application.use_cases.titulo_use_cases import (
    CadastrarTituloUseCase,
    CancelarTituloUseCase,
    EditarTituloUseCase,
    ListarTitulosUseCase,
    ObterTituloUseCase,
    QuitarTituloUseCase,
    RemoverTituloUseCase,
)
from domain.enums.categoria_titulo import CategoriaTitulo
from domain.enums.forma_pagamento import FormaPagamento
from domain.enums.status_titulo import StatusTitulo
from domain.enums.tipo_titulo import TipoTitulo
from ui.views.quitacao_dialog import QuitacaoDialog
from ui.views.relatorio_dialog import RelatorioDialog
from ui.views.status_formatter import formatar_status_titulo
from ui.views.table_helpers import (
    configurar_tabela_padrao,
    criar_item_centralizado,
)
from ui.views.titulo_form_view import TituloFormView


class TitulosView(QWidget):
    """Tela de listagem e gerenciamento de titulos financeiros."""

    COLUNAS = [
        "ID",
        "Categoria",
        "Descricao",
        "Tipo",
        "Status",
        "Valor",
        "Valor Pago",
        "Forma Pagamento",
        "Vencimento",
    ]

    def __init__(
        self,
        listar: ListarTitulosUseCase,
        obter: ObterTituloUseCase,
        criar: CadastrarTituloUseCase,
        editar: EditarTituloUseCase,
        quitar: QuitarTituloUseCase,
        cancelar: CancelarTituloUseCase,
        remover: RemoverTituloUseCase,
        listar_escritorios: ListarEscritoriosUseCase,
        listar_empresas: ListarEmpresasUseCase,
        listar_contas_bancarias: ListarContasBancariasUseCase,
        garantir_conta_padrao: GarantirContaPadraoUseCase,
        relatorio_titulos: RelatorioTitulosUseCase,
        fluxo_caixa: FluxoCaixaUseCase,
        projecao_financeira: ProjecaoFinanceiraUseCase,
        contexto_empresa: EmpresaContextService,
        on_titulo_quitado: Callable[[], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._listar = listar
        self._obter = obter
        self._criar = criar
        self._editar = editar
        self._quitar = quitar
        self._cancelar = cancelar
        self._remover = remover
        self._listar_escritorios = listar_escritorios
        self._listar_empresas = listar_empresas
        self._listar_contas_bancarias = listar_contas_bancarias
        self._garantir_conta_padrao = garantir_conta_padrao
        self._relatorio_titulos = relatorio_titulos
        self._fluxo_caixa = fluxo_caixa
        self._projecao_financeira = projecao_financeira
        self._contexto_empresa = contexto_empresa
        self._on_titulo_quitado = on_titulo_quitado
        self._mapa_empresa_escritorio: dict[int, int] = {}
        self._montar()
        self.carregar_empresa_ativa()

    def _montar(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # --- Linha 1: Titulo + Acoes principais ---
        topo = QHBoxLayout()
        topo.setSpacing(12)

        titulo = QLabel("Titulos Financeiros")
        titulo.setObjectName("viewTitulo")
        topo.addWidget(titulo)
        topo.addStretch()

        btn_novo = QPushButton("Novo Titulo")
        btn_novo.setObjectName("btnPrimario")
        btn_novo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_novo.clicked.connect(self._novo)
        topo.addWidget(btn_novo)

        btn_relatorio = QPushButton("Relatorios")
        btn_relatorio.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_relatorio.clicked.connect(self._abrir_relatorios)
        topo.addWidget(btn_relatorio)

        layout.addLayout(topo)

        # --- Linha 2: Filtros (grid alinhado) ---
        filtros = QGridLayout()
        filtros.setHorizontalSpacing(16)
        filtros.setVerticalSpacing(8)
        filtros.setContentsMargins(0, 0, 0, 0)

        # Linha 0
        # Coluna 0: Empresa
        lbl_emp = QLabel("Empresa:")
        lbl_emp.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        filtros.addWidget(lbl_emp, 0, 0)
        self._combo_filtro_empresa = QComboBox()
        self._combo_filtro_empresa.setMinimumWidth(200)
        self._combo_filtro_empresa.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._combo_filtro_empresa.addItem("Selecione...", None)
        filtros.addWidget(self._combo_filtro_empresa, 0, 1)

        # Coluna 1: Categoria
        lbl_cat = QLabel("Categoria:")
        lbl_cat.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        filtros.addWidget(lbl_cat, 0, 2)
        self._combo_filtro_categoria = QComboBox()
        self._combo_filtro_categoria.setMinimumWidth(140)
        self._combo_filtro_categoria.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._combo_filtro_categoria.addItem("Todas", None)
        for c in CategoriaTitulo:
            self._combo_filtro_categoria.addItem(c.value, c.value)
        filtros.addWidget(self._combo_filtro_categoria, 0, 3)

        # Coluna 2: Forma Pagamento
        lbl_forma = QLabel("Forma Pag.:")
        lbl_forma.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        filtros.addWidget(lbl_forma, 0, 4)
        self._combo_filtro_forma = QComboBox()
        self._combo_filtro_forma.setMinimumWidth(140)
        self._combo_filtro_forma.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._combo_filtro_forma.addItem("Todas", None)
        for f in FormaPagamento:
            self._combo_filtro_forma.addItem(f.value, f.value)
        filtros.addWidget(self._combo_filtro_forma, 0, 5)

        # Coluna 3: Tipo
        lbl_tipo = QLabel("Tipo:")
        lbl_tipo.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        filtros.addWidget(lbl_tipo, 0, 6)
        self._combo_filtro_tipo = QComboBox()
        self._combo_filtro_tipo.setMinimumWidth(140)
        self._combo_filtro_tipo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._combo_filtro_tipo.addItem("Todos", None)
        for t in TipoTitulo:
            self._combo_filtro_tipo.addItem(t.value, t.value)
        filtros.addWidget(self._combo_filtro_tipo, 0, 7)

        # Linha 1
        # Coluna 0: Status
        lbl_status = QLabel("Status:")
        lbl_status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        filtros.addWidget(lbl_status, 1, 0)
        self._combo_filtro_status = QComboBox()
        self._combo_filtro_status.setMinimumWidth(140)
        self._combo_filtro_status.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._combo_filtro_status.addItem("Todos", None)
        for s in StatusTitulo:
            self._combo_filtro_status.addItem(
                formatar_status_titulo(s.value), s.value
            )
        filtros.addWidget(self._combo_filtro_status, 1, 1)

        # Coluna 1: Vencimento inicio
        lbl_venc_ini = QLabel("Venc. Inicio:")
        lbl_venc_ini.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        filtros.addWidget(lbl_venc_ini, 1, 2)
        self._date_filtro_venc_ini = QDateEdit()
        self._date_filtro_venc_ini.setCalendarPopup(True)
        self._date_filtro_venc_ini.setSpecialValueText("Sem limite")
        self._date_filtro_venc_ini.setDate(
            self._date_filtro_venc_ini.minimumDate()
        )
        filtros.addWidget(self._date_filtro_venc_ini, 1, 3)

        # Coluna 2: Vencimento fim
        lbl_venc_fim = QLabel("Venc. Fim:")
        lbl_venc_fim.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        filtros.addWidget(lbl_venc_fim, 1, 4)
        self._date_filtro_venc_fim = QDateEdit()
        self._date_filtro_venc_fim.setCalendarPopup(True)
        self._date_filtro_venc_fim.setSpecialValueText("Sem limite")
        self._date_filtro_venc_fim.setDate(
            self._date_filtro_venc_fim.minimumDate()
        )
        filtros.addWidget(self._date_filtro_venc_fim, 1, 5)

        # Linha 2
        # Coluna 0: Busca
        lbl_busca = QLabel("Busca:")
        lbl_busca.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        filtros.addWidget(lbl_busca, 2, 0)
        self._campo_busca = QLineEdit()
        self._campo_busca.setPlaceholderText(
            "Descricao, numero do documento ou codigo de barras"
        )
        filtros.addWidget(self._campo_busca, 2, 1, 1, 3)

        # Coluna 4: Botoes rapidos
        btn_vencidos = QPushButton("Vencidos")
        btn_vencidos.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_vencidos.clicked.connect(self._filtrar_vencidos)
        filtros.addWidget(btn_vencidos, 2, 4)

        btn_a_vencer = QPushButton("A vencer")
        btn_a_vencer.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_a_vencer.clicked.connect(self._filtrar_a_vencer)
        filtros.addWidget(btn_a_vencer, 2, 5)

        btn_do_mes = QPushButton("Do mes")
        btn_do_mes.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_do_mes.clicked.connect(self._filtrar_do_mes)
        filtros.addWidget(btn_do_mes, 2, 6)

        btn_limpar = QPushButton("Limpar")
        btn_limpar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_limpar.clicked.connect(self._limpar_filtros)
        filtros.addWidget(btn_limpar, 2, 7)

        # Linha 3: Botao Filtrar
        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_filtrar.clicked.connect(self.atualizar_lista)
        btn_filtrar.setFixedWidth(100)
        filtros.addWidget(btn_filtrar, 3, 7, Qt.AlignmentFlag.AlignRight)

        # Stretch na ultima coluna para empurrar tudo para a esquerda
        filtros.setColumnStretch(8, 1)

        layout.addLayout(filtros)

        self._tabela = QTableWidget()
        self._tabela.setColumnCount(len(self.COLUNAS))
        self._tabela.setHorizontalHeaderLabels(self.COLUNAS)
        configurar_tabela_padrao(self._tabela)
        self._configurar_colunas_tabela()
        self._tabela.doubleClicked.connect(self._editar_selecionado)
        self._tabela.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self._tabela.customContextMenuRequested.connect(
            self._exibir_menu_contexto
        )
        self._tabela.itemSelectionChanged.connect(
            self._atualizar_botoes_acoes
        )
        layout.addWidget(self._tabela, stretch=1)

        botoes = QHBoxLayout()
        btn_editar = QPushButton("Editar")
        btn_editar.clicked.connect(self._editar_selecionado)
        botoes.addWidget(btn_editar)

        self._btn_quitar = QPushButton("Quitar")
        self._btn_quitar.clicked.connect(self._quitar_selecionado)
        botoes.addWidget(self._btn_quitar)

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self._cancelar_selecionado)
        botoes.addWidget(btn_cancelar)

        btn_remover = QPushButton("Remover")
        btn_remover.clicked.connect(self._remover_selecionado)
        botoes.addWidget(btn_remover)
        botoes.addStretch()
        layout.addLayout(botoes)

    def _configurar_colunas_tabela(self) -> None:
        """Define larguras e comportamento de redimensionamento das colunas."""
        header = self._tabela.horizontalHeader()
        header.setStretchLastSection(False)

        # Larguras fixas para colunas pequenas
        larguras_fixas = {
            0: 60,   # ID
            3: 80,   # Tipo
            4: 90,   # Status
            5: 110,  # Valor
            6: 110,  # Valor Pago
            7: 130,  # Forma Pagamento
            8: 100,  # Vencimento
        }
        for coluna, largura in larguras_fixas.items():
            header.setSectionResizeMode(coluna, QHeaderView.ResizeMode.Fixed)
            self._tabela.setColumnWidth(coluna, largura)

        # Categoria ajusta ao conteudo
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

        # Descricao ocupa o espaco restante
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(False)

        # Altura das linhas um pouco maior para melhor legibilidade
        self._tabela.verticalHeader().setDefaultSectionSize(40)
        self._tabela.verticalHeader().setMinimumSectionSize(40)

        # Altura minima da tabela para aproveitar melhor a tela
        self._tabela.setMinimumHeight(400)

    def _carregar_empresas(self) -> None:
        try:
            empresas = self._listar_empresas.execute(skip=0, limit=1000)
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao carregar empresas: {e}")
            self._mapa_empresa_escritorio = {}
            return

        self._mapa_empresa_escritorio = {
            e.id: e.escritorio_id for e in empresas if e.id is not None
        }

        self._combo_filtro_empresa.blockSignals(True)
        atual = self._combo_filtro_empresa.currentData()
        self._combo_filtro_empresa.clear()
        self._combo_filtro_empresa.addItem("Selecione...", None)
        for emp in empresas:
            if emp.id is not None:
                self._combo_filtro_empresa.addItem(
                    emp.razao_social, emp.id
                )

        empresa_ativa = self._contexto_empresa.get_empresa_ativa()
        if empresa_ativa is not None:
            idx = self._combo_filtro_empresa.findData(empresa_ativa)
            if idx >= 0:
                self._combo_filtro_empresa.setCurrentIndex(idx)
        elif atual is not None:
            idx = self._combo_filtro_empresa.findData(atual)
            if idx >= 0:
                self._combo_filtro_empresa.setCurrentIndex(idx)
        self._combo_filtro_empresa.blockSignals(False)

    def carregar_empresa_ativa(self) -> None:
        """Recarrega a lista usando a empresa ativa do contexto global."""
        self.atualizar_lista()

    def _escritorio_da_empresa(self, empresa_id: int | None) -> int | None:
        if empresa_id is None:
            return None
        return self._mapa_empresa_escritorio.get(empresa_id)

    def atualizar_lista(self) -> None:
        self._carregar_empresas()
        empresa_id = self._combo_filtro_empresa.currentData()
        if empresa_id is None:
            self._tabela.setRowCount(0)
            return

        escritorio_id = self._escritorio_da_empresa(empresa_id)
        if escritorio_id is None:
            self._tabela.setRowCount(0)
            return

        tipo = self._combo_filtro_tipo.currentData()
        status = self._combo_filtro_status.currentData()
        categoria = self._combo_filtro_categoria.currentData()
        forma = self._combo_filtro_forma.currentData()
        venc_ini = self._data_filtro_venc_ini()
        venc_fim = self._data_filtro_venc_fim()
        busca = self._campo_busca.text().strip().lower()

        try:
            titulos = self._listar.execute(
                escritorio_id=escritorio_id,
                empresa_id=empresa_id,
                tipo=tipo,
                status=status,
                skip=0,
                limit=500,
            )
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao listar titulos: {e}")
            return

        if categoria is not None:
            titulos = [t for t in titulos if t.categoria == categoria]

        if forma is not None:
            titulos = [t for t in titulos if t.forma_pagamento == forma]

        if venc_ini is not None:
            titulos = [
                t for t in titulos if t.data_vencimento >= venc_ini
            ]

        if venc_fim is not None:
            titulos = [
                t for t in titulos if t.data_vencimento <= venc_fim
            ]

        if busca:
            titulos = [
                t
                for t in titulos
                if busca in t.descricao.lower()
                or (t.numero_documento is not None and busca in t.numero_documento.lower())
                or (t.codigo_barras is not None and busca in t.codigo_barras.lower())
            ]

        self._tabela.setRowCount(len(titulos))
        for i, t in enumerate(titulos):
            self._tabela.setItem(
                i, 0, criar_item_centralizado(str(t.id or ""))
            )
            self._tabela.setItem(
                i, 1, criar_item_centralizado(t.categoria)
            )
            self._tabela.setItem(i, 2, QTableWidgetItem(t.descricao))
            self._tabela.setItem(i, 3, QTableWidgetItem(t.tipo))
            self._tabela.setItem(
                i, 4, QTableWidgetItem(formatar_status_titulo(t.status))
            )
            self._tabela.setItem(
                i, 5, criar_item_centralizado(self._formatar_valor(t.valor))
            )
            valor_pago_texto = (
                self._formatar_valor(t.valor_pago)
                if t.valor_pago is not None
                else "—"
            )
            self._tabela.setItem(
                i, 6, criar_item_centralizado(valor_pago_texto)
            )
            self._tabela.setItem(
                i, 7, criar_item_centralizado(t.forma_pagamento)
            )
            self._tabela.setItem(
                i,
                8,
                criar_item_centralizado(
                    t.data_vencimento.strftime("%d/%m/%Y")
                ),
            )

            cor_texto, cor_fundo = self._cores_linha(t)
            for col in range(len(self.COLUNAS)):
                item = self._tabela.item(i, col)
                if item is not None:
                    item.setForeground(self._cor(cor_texto))
                    item.setBackground(self._cor(cor_fundo))

    def _cores_linha(self, titulo: TituloResponseDTO) -> tuple[str, str]:
        """Retorna (cor_texto, cor_fundo) para a linha do titulo."""
        if titulo.status == "PAGO":
            return "#2e7d32", "#e8f5e9"
        if titulo.status == "CANCELADO":
            return "#757575", "#eeeeee"
        if titulo.data_vencimento < date.today():
            return "#c62828", "#ffebee"
        if titulo.tipo == "RECEBER":
            return "#1565c0", "#e3f2fd"
        if titulo.tipo == "PAGAR":
            return "#ef6c00", "#fff3e0"
        return "#000000", "#ffffff"

    def _data_filtro_venc_ini(self) -> date | None:
        """Retorna a data inicial do filtro de vencimento ou None se nao definida."""
        if self._date_filtro_venc_ini.specialValueText() == "Sem limite":
            qdate = self._date_filtro_venc_ini.date()
            if qdate == self._date_filtro_venc_ini.minimumDate():
                return None
        return cast(date, self._date_filtro_venc_ini.date().toPython())

    def _data_filtro_venc_fim(self) -> date | None:
        """Retorna a data final do filtro de vencimento ou None se nao definida."""
        if self._date_filtro_venc_fim.specialValueText() == "Sem limite":
            qdate = self._date_filtro_venc_fim.date()
            if qdate == self._date_filtro_venc_fim.minimumDate():
                return None
        return cast(date, self._date_filtro_venc_fim.date().toPython())

    def _filtrar_vencidos(self) -> None:
        """Preenche os filtros para mostrar titulos abertos vencidos."""
        self._combo_filtro_status.setCurrentIndex(
            self._combo_filtro_status.findText("ABERTO")
        )
        self._date_filtro_venc_fim.setDate(
            QDate(date.today().year, date.today().month, date.today().day)
        )
        self._date_filtro_venc_fim.setSpecialValueText("")
        self.atualizar_lista()

    def _filtrar_a_vencer(self) -> None:
        """Preenche os filtros para mostrar titulos abertos a vencer."""
        self._combo_filtro_status.setCurrentIndex(
            self._combo_filtro_status.findText("ABERTO")
        )
        self._date_filtro_venc_ini.setDate(
            QDate(date.today().year, date.today().month, date.today().day)
        )
        self._date_filtro_venc_ini.setSpecialValueText("")
        self.atualizar_lista()

    def _filtrar_do_mes(self) -> None:
        """Preenche os filtros para mostrar titulos com vencimento no mes atual."""
        hoje = date.today()
        primeiro_dia = date(hoje.year, hoje.month, 1)
        ultimo_dia = date(hoje.year, hoje.month, self._ultimo_dia_mes(hoje))
        self._date_filtro_venc_ini.setDate(
            QDate(primeiro_dia.year, primeiro_dia.month, primeiro_dia.day)
        )
        self._date_filtro_venc_ini.setSpecialValueText("")
        self._date_filtro_venc_fim.setDate(
            QDate(ultimo_dia.year, ultimo_dia.month, ultimo_dia.day)
        )
        self._date_filtro_venc_fim.setSpecialValueText("")
        self.atualizar_lista()

    @staticmethod
    def _ultimo_dia_mes(data: date) -> int:
        import calendar

        return calendar.monthrange(data.year, data.month)[1]

    def _limpar_filtros(self) -> None:
        """Reseta os filtros para os valores padrao."""
        self._combo_filtro_empresa.setCurrentIndex(0)
        self._combo_filtro_categoria.setCurrentIndex(0)
        self._combo_filtro_forma.setCurrentIndex(0)
        self._combo_filtro_tipo.setCurrentIndex(0)
        self._combo_filtro_status.setCurrentIndex(0)
        self._date_filtro_venc_ini.setDate(
            self._date_filtro_venc_ini.minimumDate()
        )
        self._date_filtro_venc_ini.setSpecialValueText("Sem limite")
        self._date_filtro_venc_fim.setDate(
            self._date_filtro_venc_fim.minimumDate()
        )
        self._date_filtro_venc_fim.setSpecialValueText("Sem limite")
        self._campo_busca.clear()
        self.atualizar_lista()

    @staticmethod
    def _formatar_valor(valor: Decimal) -> str:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    @staticmethod
    def _cor(hex_code: str) -> QColor:
        return QColor(hex_code)

    def _obter_selecionado(self) -> TituloResponseDTO | None:
        linha = self._tabela.currentRow()
        if linha < 0:
            return None
        item_id = self._tabela.item(linha, 0)
        if item_id is None:
            return None
        try:
            id_int = int(item_id.text())
        except ValueError:
            return None
        return self._obter.execute(id_int)

    def _atualizar_botoes_acoes(self) -> None:
        """Habilita/desabilita acoes conforme o status do titulo selecionado."""
        titulo = self._obter_selecionado()
        permite_quitar = titulo is not None and titulo.status == "ABERTO"
        self._btn_quitar.setEnabled(permite_quitar)

    def _obter_opcoes(
        self, listar_use_case: Any, attr_id: str, attr_nome: str
    ) -> list[tuple[int, str]]:
        try:
            itens = listar_use_case.execute(skip=0, limit=1000)
            return [
                (getattr(item, attr_id), getattr(item, attr_nome))
                for item in itens
                if getattr(item, attr_id) is not None
            ]
        except Exception:
            return []

    def _obter_opcoes_empresa(self) -> list[tuple[int, str, int]]:
        try:
            empresas = self._listar_empresas.execute(skip=0, limit=1000)
            return [
                (e.id, e.razao_social, e.escritorio_id)
                for e in empresas
                if e.id is not None
            ]
        except Exception:
            return []

    def _abrir_relatorios(self) -> None:
        empresa_id = self._combo_filtro_empresa.currentData()
        if empresa_id is None:
            QMessageBox.information(
                self,
                "Aviso",
                "Selecione uma empresa para gerar o relatorio.",
            )
            return

        escritorio_id = self._escritorio_da_empresa(empresa_id)
        if escritorio_id is None:
            QMessageBox.information(
                self,
                "Aviso",
                "Empresa sem escritorio vinculado.",
            )
            return

        dialogo = RelatorioDialog(
            relatorio_use_case=self._relatorio_titulos,
            fluxo_caixa_use_case=self._fluxo_caixa,
            projecao_use_case=self._projecao_financeira,
            escritorio_id=escritorio_id,
            empresa_id=empresa_id,
            parent=self,
        )
        dialogo.exec()

    def _novo(self) -> None:
        opcoes_escritorio = self._obter_opcoes(
            self._listar_escritorios, "id", "nome"
        )
        if not opcoes_escritorio:
            QMessageBox.information(
                self,
                "Aviso",
                "Cadastre um escritorio antes de cadastrar titulos.",
            )
            return

        empresa_id = self._combo_filtro_empresa.currentData()
        if empresa_id is None:
            QMessageBox.information(
                self,
                "Aviso",
                "Selecione uma empresa para cadastrar um titulo.",
            )
            return

        escritorio_id = self._escritorio_da_empresa(empresa_id)
        if escritorio_id is None:
            QMessageBox.information(
                self,
                "Aviso",
                "Empresa sem escritorio vinculado.",
            )
            return

        try:
            plano_conta_id = self._garantir_conta_padrao.execute(escritorio_id)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Erro",
                f"Nao foi possivel garantir a conta padrao: {e}",
            )
            return

        opcoes_empresa = self._obter_opcoes_empresa()
        contas_por_id = self._obter_contas_por_id()

        form = TituloFormView(
            criar_use_case=self._criar,
            editar_use_case=self._editar,
            opcoes_escritorio=opcoes_escritorio,
            opcoes_empresa=opcoes_empresa,
            plano_conta_id=plano_conta_id,
            empresa_id=empresa_id,
            contas_por_id=contas_por_id,
            parent=self,
        )
        if form.exec() == TituloFormView.DialogCode.Accepted:
            self.atualizar_lista()

    def _editar_selecionado(self) -> None:
        titulo = self._obter_selecionado()
        if titulo is None:
            QMessageBox.information(
                self, "Selecao", "Selecione um titulo para editar."
            )
            return

        try:
            plano_conta_id = self._garantir_conta_padrao.execute(
                titulo.escritorio_id
            )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Erro",
                f"Nao foi possivel garantir a conta padrao: {e}",
            )
            return

        opcoes_escritorio = self._obter_opcoes(
            self._listar_escritorios, "id", "nome"
        )
        opcoes_empresa = self._obter_opcoes_empresa()
        contas_por_id = self._obter_contas_por_id()

        form = TituloFormView(
            criar_use_case=self._criar,
            editar_use_case=self._editar,
            opcoes_escritorio=opcoes_escritorio,
            opcoes_empresa=opcoes_empresa,
            plano_conta_id=plano_conta_id,
            empresa_id=titulo.empresa_id,
            contas_por_id=contas_por_id,
            parent=self,
            titulo=titulo,
        )
        if form.exec() == TituloFormView.DialogCode.Accepted:
            self.atualizar_lista()

    def _quitar_selecionado(self) -> None:
        titulo = self._obter_selecionado()
        if titulo is None:
            QMessageBox.information(
                self, "Selecao", "Selecione um titulo para quitar."
            )
            return
        if titulo.status == "PAGO":
            QMessageBox.information(
                self, "Aviso", "Titulo ja esta quitado."
            )
            return
        if titulo.status == "CANCELADO":
            QMessageBox.information(
                self, "Aviso", "Nao e possivel quitar um titulo cancelado."
            )
            return

        opcoes_conta = self._obter_opcoes_conta_bancaria(titulo.empresa_id)
        dialogo = QuitacaoDialog(
            titulo=titulo,
            opcoes_conta_bancaria=opcoes_conta,
            contexto_empresa=self._contexto_empresa,
            parent=self,
        )
        if dialogo.exec() != QuitacaoDialog.DialogCode.Accepted:
            return

        try:
            data_quitacao, valor_pago, conta_id, forma, observacao = (
                dialogo.obter_dados()
            )
            dto = QuitarTituloDTO(
                id=titulo.id,
                data_quitacao=data_quitacao,
                valor_pago=valor_pago,
                conta_bancaria_id=conta_id,
                forma_pagamento=forma,
                observacao_quitacao=observacao,
                empresa_id=titulo.empresa_id,
            )
            self._quitar.execute(dto)
            self.atualizar_lista()
            if self._on_titulo_quitado is not None:
                self._on_titulo_quitado()
            QMessageBox.information(
                self, "Sucesso", "Titulo quitado com sucesso."
            )
        except ValueError as e:
            QMessageBox.warning(self, "Erro", str(e))

    def _obter_opcoes_conta_bancaria(
        self, empresa_id: int | None
    ) -> list[tuple[int, str]]:
        try:
            contas = self._listar_contas_bancarias.execute(
                empresa_id=empresa_id, skip=0, limit=1000
            )
            return [
                (c.id, f"{c.banco_nome} - {c.conta}")
                for c in contas
                if c.id is not None and c.ativo
            ]
        except Exception:
            return []

    def _obter_contas_por_id(self) -> dict[int, str]:
        try:
            contas = self._listar_contas_bancarias.execute(
                skip=0, limit=1000
            )
            return {
                c.id: f"{c.banco_nome} - {c.conta}"
                for c in contas
                if c.id is not None
            }
        except Exception:
            return {}

    def _cancelar_selecionado(self) -> None:
        titulo = self._obter_selecionado()
        if titulo is None:
            QMessageBox.information(
                self, "Selecao", "Selecione um titulo para cancelar."
            )
            return
        if titulo.status == "CANCELADO":
            QMessageBox.information(
                self, "Aviso", "Titulo ja esta cancelado."
            )
            return
        resposta = QMessageBox.question(
            self,
            "Confirmar cancelamento",
            f"Deseja cancelar o titulo '{titulo.descricao}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            try:
                self._cancelar.execute(titulo.id)
                self.atualizar_lista()
                QMessageBox.information(
                    self, "Sucesso", "Titulo cancelado com sucesso."
                )
            except ValueError as e:
                QMessageBox.warning(self, "Erro", str(e))

    def _remover_selecionado(self) -> None:
        titulo = self._obter_selecionado()
        if titulo is None:
            QMessageBox.information(
                self, "Selecao", "Selecione um titulo para remover."
            )
            return
        resposta = QMessageBox.question(
            self,
            "Confirmar remocao",
            f"Deseja remover o titulo '{titulo.descricao}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            try:
                self._remover.execute(titulo.id)
                self.atualizar_lista()
                QMessageBox.information(
                    self, "Sucesso", "Titulo removido com sucesso."
                )
            except ValueError as e:
                QMessageBox.warning(self, "Erro", str(e))

    def _exibir_menu_contexto(self, pos: Any) -> None:
        """Exibe menu de contexto com acoes para o titulo selecionado."""
        item = self._tabela.itemAt(pos)
        if item is None:
            return
        self._tabela.selectRow(item.row())

        titulo = self._obter_selecionado()
        permite_quitar = titulo is not None and titulo.status == "ABERTO"

        menu = QMenu(self)
        acao_editar = menu.addAction("Editar")
        acao_quitar = menu.addAction("Quitar")
        acao_quitar.setEnabled(permite_quitar)
        acao_cancelar = menu.addAction("Cancelar")
        menu.addSeparator()
        acao_remover = menu.addAction("Apagar")

        acao = menu.exec(self._tabela.viewport().mapToGlobal(pos))
        if acao == acao_editar:
            self._editar_selecionado()
        elif acao == acao_quitar:
            self._quitar_selecionado()
        elif acao == acao_cancelar:
            self._cancelar_selecionado()
        elif acao == acao_remover:
            self._remover_selecionado()
