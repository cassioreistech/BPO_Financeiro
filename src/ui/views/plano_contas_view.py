"""Tela de listagem de Plano de Contas."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from application.dto.escritorio_dto import EscritorioResponseDTO
from application.dto.plano_conta_dto import PlanoContaResponseDTO
from application.use_cases.escritorio_use_cases import ListarEscritoriosUseCase
from application.use_cases.plano_conta_use_cases import (
    CadastrarPlanoContaUseCase,
    EditarPlanoContaUseCase,
    ListarPlanoContaUseCase,
    ObterPlanoContaUseCase,
    RemoverPlanoContaUseCase,
)
from ui.views.plano_conta_form_view import PlanoContaFormView


class PlanoContasView(QWidget):
    """Tela de listagem e gerenciamento do plano de contas."""

    COLUNAS = ["ID", "Escritorio", "Codigo", "Nome", "Tipo", "Nivel", "Pai"]

    def __init__(
        self,
        listar: ListarPlanoContaUseCase,
        obter: ObterPlanoContaUseCase,
        criar: CadastrarPlanoContaUseCase,
        editar: EditarPlanoContaUseCase,
        remover: RemoverPlanoContaUseCase,
        listar_escritorios: ListarEscritoriosUseCase,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._listar = listar
        self._obter = obter
        self._criar = criar
        self._editar = editar
        self._remover = remover
        self._listar_escritorios = listar_escritorios
        self._montar()
        self.atualizar_lista()

    def _montar(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        cabecalho = QHBoxLayout()
        titulo = QLabel("Plano de Contas")
        titulo.setObjectName("viewTitulo")
        cabecalho.addWidget(titulo)
        cabecalho.addStretch()

        cabecalho.addWidget(QLabel("Escritorio:"))
        self._combo_filtro_escritorio = QComboBox()
        self._combo_filtro_escritorio.setMinimumWidth(200)
        self._combo_filtro_escritorio.currentIndexChanged.connect(
            self.atualizar_lista
        )
        cabecalho.addWidget(self._combo_filtro_escritorio)

        btn_novo = QPushButton("Nova Conta")
        btn_novo.setObjectName("btnPrimario")
        btn_novo.clicked.connect(self._novo)
        cabecalho.addWidget(btn_novo)

        btn_atualizar = QPushButton("Atualizar")
        btn_atualizar.clicked.connect(self.atualizar_lista)
        cabecalho.addWidget(btn_atualizar)

        layout.addLayout(cabecalho)

        self._tabela = QTableWidget()
        self._tabela.setColumnCount(len(self.COLUNAS))
        self._tabela.setHorizontalHeaderLabels(self.COLUNAS)
        self._tabela.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._tabela.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self._tabela.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tabela.setAlternatingRowColors(True)
        self._tabela.verticalHeader().setVisible(False)
        self._tabela.horizontalHeader().setStretchLastSection(True)
        self._tabela.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self._tabela.doubleClicked.connect(self._editar_selecionado)
        layout.addWidget(self._tabela)

        botoes = QHBoxLayout()
        btn_editar = QPushButton("Editar")
        btn_editar.clicked.connect(self._editar_selecionado)
        botoes.addWidget(btn_editar)
        btn_remover = QPushButton("Remover")
        btn_remover.clicked.connect(self._remover_selecionado)
        botoes.addWidget(btn_remover)
        botoes.addStretch()
        layout.addLayout(botoes)

    def atualizar_lista(self) -> None:
        try:
            escritorios = self._listar_escritorios.execute(skip=0, limit=1000)
            mapa_esc = {e.id: e.nome for e in escritorios if e.id is not None}
        except Exception:
            mapa_esc = {}
            escritorios = []

        self._atualizar_combo_filtro(escritorios)
        escritorio_id = self._combo_filtro_escritorio.currentData()
        if escritorio_id is None:
            self._tabela.setRowCount(0)
            return

        try:
            contas = self._listar.execute(
                escritorio_id=escritorio_id, skip=0, limit=500
            )
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao listar plano de contas: {e}")
            return

        self._tabela.setRowCount(len(contas))
        for i, conta in enumerate(contas):
            self._tabela.setItem(
                i, 0, self._item_centralizado(str(conta.id or ""))
            )
            self._tabela.setItem(
                i, 1, QTableWidgetItem(mapa_esc.get(conta.escritorio_id, "—"))
            )
            self._tabela.setItem(i, 2, QTableWidgetItem(conta.codigo))
            self._tabela.setItem(i, 3, QTableWidgetItem(conta.nome))
            self._tabela.setItem(i, 4, QTableWidgetItem(conta.tipo))
            self._tabela.setItem(
                i, 5, self._item_centralizado(str(conta.nivel))
            )
            self._tabela.setItem(
                i, 6, QTableWidgetItem(str(conta.pai_id) if conta.pai_id else "—")
            )

    def _atualizar_combo_filtro(
        self, escritorios: list[EscritorioResponseDTO]
    ) -> None:

        atual = self._combo_filtro_escritorio.currentData()
        self._combo_filtro_escritorio.blockSignals(True)
        self._combo_filtro_escritorio.clear()
        self._combo_filtro_escritorio.addItem("Selecione...", None)
        for esc in escritorios:
            if esc.id is not None:
                self._combo_filtro_escritorio.addItem(esc.nome, esc.id)
        if atual is not None:
            idx = self._combo_filtro_escritorio.findData(atual)
            if idx >= 0:
                self._combo_filtro_escritorio.setCurrentIndex(idx)
        self._combo_filtro_escritorio.blockSignals(False)

    def _item_centralizado(self, texto: str) -> QTableWidgetItem:
        item = QTableWidgetItem(texto)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _obter_selecionado(self) -> PlanoContaResponseDTO | None:
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

    def _obter_opcoes_escritorio(self) -> list[tuple[int, str]]:
        try:
            escritorios = self._listar_escritorios.execute(skip=0, limit=1000)
            return [(e.id, e.nome) for e in escritorios if e.id is not None]
        except Exception:
            return []

    def _novo(self) -> None:
        opcoes = self._obter_opcoes_escritorio()
        if not opcoes:
            QMessageBox.information(
                self,
                "Aviso",
                "Cadastre um escritorio antes de cadastrar contas do plano.",
            )
            return
        form = PlanoContaFormView(
            criar_use_case=self._criar,
            editar_use_case=self._editar,
            listar_use_case=self._listar,
            opcoes_escritorio=opcoes,
            escritorio_id=self._combo_filtro_escritorio.currentData(),
            parent=self,
        )
        if form.exec() == PlanoContaFormView.DialogCode.Accepted:
            self.atualizar_lista()

    def _editar_selecionado(self) -> None:
        plano = self._obter_selecionado()
        if plano is None:
            QMessageBox.information(
                self, "Selecao", "Selecione uma conta para editar."
            )
            return
        opcoes = self._obter_opcoes_escritorio()
        form = PlanoContaFormView(
            criar_use_case=self._criar,
            editar_use_case=self._editar,
            listar_use_case=self._listar,
            opcoes_escritorio=opcoes,
            escritorio_id=self._combo_filtro_escritorio.currentData(),
            parent=self,
            plano=plano,
        )
        if form.exec() == PlanoContaFormView.DialogCode.Accepted:
            self.atualizar_lista()

    def _remover_selecionado(self) -> None:
        plano = self._obter_selecionado()
        if plano is None:
            QMessageBox.information(
                self, "Selecao", "Selecione uma conta para remover."
            )
            return
        resposta = QMessageBox.question(
            self,
            "Confirmar remocao",
            f"Deseja remover a conta '{plano.codigo} - {plano.nome}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            try:
                self._remover.execute(plano.id)
                self.atualizar_lista()
                QMessageBox.information(self, "Sucesso", "Conta removida com sucesso.")
            except ValueError as e:
                QMessageBox.warning(self, "Erro", str(e))
