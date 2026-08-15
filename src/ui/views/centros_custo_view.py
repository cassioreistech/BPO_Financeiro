"""Tela de listagem de Centros de Custo."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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

from application.dto.centro_custo_dto import CentroCustoResponseDTO
from application.use_cases.centro_custo_use_cases import (
    CadastrarCentroCustoUseCase,
    DesativarCentroCustoUseCase,
    EditarCentroCustoUseCase,
    ListarCentroCustoUseCase,
    ObterCentroCustoUseCase,
)
from application.use_cases.empresa_use_cases import ListarEmpresasUseCase
from ui.views.centro_custo_form_view import CentroCustoFormView


class CentrosCustoView(QWidget):
    """Tela de listagem e gerenciamento de centros de custo."""

    COLUNAS = ["ID", "Empresa", "Codigo", "Nome", "Ativo"]

    def __init__(
        self,
        listar: ListarCentroCustoUseCase,
        obter: ObterCentroCustoUseCase,
        criar: CadastrarCentroCustoUseCase,
        editar: EditarCentroCustoUseCase,
        desativar: DesativarCentroCustoUseCase,
        listar_empresas: ListarEmpresasUseCase,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._listar = listar
        self._obter = obter
        self._criar = criar
        self._editar = editar
        self._desativar = desativar
        self._listar_empresas = listar_empresas
        self._montar()
        self.atualizar_lista()

    def _montar(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        cabecalho = QHBoxLayout()
        titulo = QLabel("Centros de Custo")
        titulo.setObjectName("viewTitulo")
        cabecalho.addWidget(titulo)
        cabecalho.addStretch()

        btn_novo = QPushButton("Novo Centro")
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
        btn_desativar = QPushButton("Desativar")
        btn_desativar.clicked.connect(self._desativar_selecionado)
        botoes.addWidget(btn_desativar)
        botoes.addStretch()
        layout.addLayout(botoes)

    def atualizar_lista(self) -> None:
        try:
            empresas = self._listar_empresas.execute(skip=0, limit=1000)
            mapa_emp = {e.id: e.nome_fantasia for e in empresas if e.id is not None}
        except Exception:
            mapa_emp = {}

        try:
            centros = self._listar.execute(empresa_id=0, skip=0, limit=500)
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao listar centros de custo: {e}")
            return

        self._tabela.setRowCount(len(centros))
        for i, centro in enumerate(centros):
            self._tabela.setItem(
                i, 0, self._item_centralizado(str(centro.id or ""))
            )
            self._tabela.setItem(
                i, 1, QTableWidgetItem(mapa_emp.get(centro.empresa_id, "—"))
            )
            self._tabela.setItem(i, 2, QTableWidgetItem(centro.codigo))
            self._tabela.setItem(i, 3, QTableWidgetItem(centro.nome))
            self._tabela.setItem(
                i, 4, self._item_centralizado("Sim" if centro.ativo else "Nao")
            )

    def _item_centralizado(self, texto: str) -> QTableWidgetItem:
        item = QTableWidgetItem(texto)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _obter_selecionado(self) -> CentroCustoResponseDTO | None:
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

    def _obter_opcoes_empresa(self) -> list[tuple[int, str]]:
        try:
            empresas = self._listar_empresas.execute(skip=0, limit=1000)
            return [(e.id, e.nome_fantasia) for e in empresas if e.id is not None]
        except Exception:
            return []

    def _novo(self) -> None:
        opcoes = self._obter_opcoes_empresa()
        if not opcoes:
            QMessageBox.information(
                self,
                "Aviso",
                "Cadastre uma empresa antes de cadastrar centros de custo.",
            )
            return
        form = CentroCustoFormView(
            criar_use_case=self._criar,
            editar_use_case=self._editar,
            opcoes_empresa=opcoes,
            parent=self,
        )
        if form.exec() == CentroCustoFormView.DialogCode.Accepted:
            self.atualizar_lista()

    def _editar_selecionado(self) -> None:
        centro = self._obter_selecionado()
        if centro is None:
            QMessageBox.information(
                self, "Selecao", "Selecione um centro de custo para editar."
            )
            return
        opcoes = self._obter_opcoes_empresa()
        form = CentroCustoFormView(
            criar_use_case=self._criar,
            editar_use_case=self._editar,
            opcoes_empresa=opcoes,
            parent=self,
            centro=centro,
        )
        if form.exec() == CentroCustoFormView.DialogCode.Accepted:
            self.atualizar_lista()

    def _desativar_selecionado(self) -> None:
        centro = self._obter_selecionado()
        if centro is None:
            QMessageBox.information(
                self, "Selecao", "Selecione um centro de custo para desativar."
            )
            return
        if not centro.ativo:
            QMessageBox.information(self, "Aviso", "Este centro ja esta desativado.")
            return
        resposta = QMessageBox.question(
            self,
            "Confirmar desativacao",
            f"Deseja desativar o centro '{centro.codigo} - {centro.nome}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            try:
                self._desativar.execute(centro.id)
                self.atualizar_lista()
                QMessageBox.information(
                    self, "Sucesso", "Centro de custo desativado com sucesso."
                )
            except ValueError as e:
                QMessageBox.warning(self, "Erro", str(e))
