"""Tela de listagem de Contadores."""

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

from application.dto.contador_dto import ContadorResponseDTO
from application.use_cases.contador_use_cases import (
    CadastrarContadorUseCase,
    EditarContadorUseCase,
    ExcluirContadorUseCase,
    ListarContadoresUseCase,
    ObterContadorUseCase,
)
from application.use_cases.escritorio_use_cases import ListarEscritoriosUseCase
from ui.views.contador_form_view import ContadorFormView


class ContadoresView(QWidget):
    """Tela de listagem e gerenciamento de contadores."""

    COLUNAS = ["ID", "Escritorio", "Nome", "CRC", "Email", "Telefone"]

    def __init__(
        self,
        listar: ListarContadoresUseCase,
        obter: ObterContadorUseCase,
        criar: CadastrarContadorUseCase,
        editar: EditarContadorUseCase,
        excluir: ExcluirContadorUseCase,
        listar_escritorios: ListarEscritoriosUseCase,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._listar = listar
        self._obter = obter
        self._criar = criar
        self._editar = editar
        self._excluir = excluir
        self._listar_escritorios = listar_escritorios
        self._montar()
        self.atualizar_lista()

    def _montar(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        cabecalho = QHBoxLayout()
        titulo = QLabel("Contadores")
        titulo.setObjectName("viewTitulo")
        cabecalho.addWidget(titulo)
        cabecalho.addStretch()

        btn_novo = QPushButton("Novo Contador")
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
        btn_excluir = QPushButton("Excluir")
        btn_excluir.clicked.connect(self._excluir_selecionado)
        botoes.addWidget(btn_excluir)
        botoes.addStretch()
        layout.addLayout(botoes)

    def atualizar_lista(self) -> None:
        try:
            escritorios = self._listar_escritorios.execute(skip=0, limit=1000)
            mapa_esc = {e.id: e.nome for e in escritorios if e.id is not None}
        except Exception:
            mapa_esc = {}

        try:
            contadores = self._listar.execute(skip=0, limit=500)
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao listar contadores: {e}")
            return

        self._tabela.setRowCount(len(contadores))
        for i, cont in enumerate(contadores):
            self._tabela.setItem(
                i, 0, self._item_centralizado(str(cont.id or ""))
            )
            self._tabela.setItem(
                i, 1, QTableWidgetItem(mapa_esc.get(cont.escritorio_id, "—"))
            )
            self._tabela.setItem(i, 2, QTableWidgetItem(cont.nome))
            self._tabela.setItem(i, 3, QTableWidgetItem(cont.crc or ""))
            self._tabela.setItem(i, 4, QTableWidgetItem(cont.email or ""))
            self._tabela.setItem(i, 5, QTableWidgetItem(cont.telefone or ""))

    def _item_centralizado(self, texto: str) -> QTableWidgetItem:
        item = QTableWidgetItem(texto)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        return item

    def _obter_selecionado(self) -> ContadorResponseDTO | None:
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
                "Cadastre um escritorio antes de cadastrar contadores.",
            )
            return
        form = ContadorFormView(
            criar_use_case=self._criar,
            editar_use_case=self._editar,
            opcoes_escritorio=opcoes,
            parent=self,
        )
        if form.exec() == ContadorFormView.DialogCode.Accepted:
            self.atualizar_lista()

    def _editar_selecionado(self) -> None:
        cont = self._obter_selecionado()
        if cont is None:
            QMessageBox.information(
                self, "Selecao", "Selecione um contador para editar."
            )
            return
        opcoes = self._obter_opcoes_escritorio()
        form = ContadorFormView(
            criar_use_case=self._criar,
            editar_use_case=self._editar,
            opcoes_escritorio=opcoes,
            parent=self,
            contador=cont,
        )
        if form.exec() == ContadorFormView.DialogCode.Accepted:
            self.atualizar_lista()

    def _excluir_selecionado(self) -> None:
        cont = self._obter_selecionado()
        if cont is None:
            QMessageBox.information(
                self, "Selecao", "Selecione um contador para excluir."
            )
            return
        resposta = QMessageBox.question(
            self,
            "Confirmar exclusao",
            f"Deseja excluir o contador '{cont.nome}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            try:
                self._excluir.execute(cont.id)
                self.atualizar_lista()
                QMessageBox.information(self, "Sucesso", "Contador excluido com sucesso.")
            except ValueError as e:
                QMessageBox.warning(self, "Erro", str(e))
