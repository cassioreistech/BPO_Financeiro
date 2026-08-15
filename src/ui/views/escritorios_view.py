"""Tela de listagem de Escritorios."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from application.dto.escritorio_dto import EscritorioResponseDTO
from application.use_cases.escritorio_use_cases import (
    CriarEscritorioUseCase,
    EditarEscritorioUseCase,
    ExcluirEscritorioUseCase,
    ListarEscritoriosUseCase,
    ObterEscritorioUseCase,
)
from ui.views.escritorio_form_view import EscritorioFormView
from ui.views.table_helpers import (
    configurar_tabela_padrao,
    criar_item_centralizado,
)


class EscritoriosView(QWidget):
    """Tela de listagem e gerenciamento de escritorios."""

    COLUNAS = ["ID", "Nome", "CNPJ/CPF", "Email", "Telefone"]

    def __init__(
        self,
        listar: ListarEscritoriosUseCase,
        obter: ObterEscritorioUseCase,
        criar: CriarEscritorioUseCase,
        editar: EditarEscritorioUseCase,
        excluir: ExcluirEscritorioUseCase,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._listar = listar
        self._obter = obter
        self._criar = criar
        self._editar = editar
        self._excluir = excluir
        self._montar()
        self.atualizar_lista()

    def _montar(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        cabecalho = QHBoxLayout()
        titulo = QLabel("Escritorios")
        titulo.setObjectName("viewTitulo")
        cabecalho.addWidget(titulo)
        cabecalho.addStretch()

        btn_novo = QPushButton("Novo Escritorio")
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
        configurar_tabela_padrao(self._tabela)
        self._tabela.doubleClicked.connect(self._editar_selecionado)
        layout.addWidget(self._tabela)

        botoes = QHBoxLayout()
        btn_editar = QPushButton("Editar")
        btn_editar.clicked.connect(self._editar_selecionado)
        botoes.addWidget(btn_editar)

        btn_excluir = QPushButton("Excluir")
        btn_excluir.setObjectName("btnPerigo")
        btn_excluir.clicked.connect(self._excluir_selecionado)
        botoes.addWidget(btn_excluir)

        botoes.addStretch()
        layout.addLayout(botoes)

    def atualizar_lista(self) -> None:
        try:
            escritorios = self._listar.execute(skip=0, limit=500)
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao listar escritorios: {e}")
            return

        self._tabela.setRowCount(len(escritorios))
        for i, esc in enumerate(escritorios):
            self._tabela.setItem(i, 0, criar_item_centralizado(str(esc.id or "")))
            self._tabela.setItem(i, 1, QTableWidgetItem(esc.nome))
            self._tabela.setItem(i, 2, QTableWidgetItem(esc.cnpj_cpf))
            self._tabela.setItem(i, 3, QTableWidgetItem(str(esc.email) if esc.email else ""))
            self._tabela.setItem(i, 4, QTableWidgetItem(str(esc.telefone) if esc.telefone else ""))

    def _obter_selecionado(self) -> EscritorioResponseDTO | None:
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

    def _novo(self) -> None:
        form = EscritorioFormView(
            criar_use_case=self._criar,
            editar_use_case=self._editar,
            parent=self,
        )
        if form.exec() == EscritorioFormView.DialogCode.Accepted:
            self.atualizar_lista()

    def _editar_selecionado(self) -> None:
        esc = self._obter_selecionado()
        if esc is None:
            QMessageBox.information(
                self, "Selecao", "Selecione um escritorio para editar."
            )
            return
        form = EscritorioFormView(
            criar_use_case=self._criar,
            editar_use_case=self._editar,
            parent=self,
            escritorio=esc,
        )
        if form.exec() == EscritorioFormView.DialogCode.Accepted:
            self.atualizar_lista()

    def _excluir_selecionado(self) -> None:
        esc = self._obter_selecionado()
        if esc is None:
            QMessageBox.information(
                self, "Selecao", "Selecione um escritorio para excluir."
            )
            return
        resposta = QMessageBox.question(
            self,
            "Confirmar exclusao",
            f"Deseja excluir o escritorio '{esc.nome}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            try:
                self._excluir.execute(esc.id)
                self.atualizar_lista()
                QMessageBox.information(self, "Sucesso", "Escritorio excluido com sucesso.")
            except ValueError as e:
                QMessageBox.warning(self, "Erro", str(e))
