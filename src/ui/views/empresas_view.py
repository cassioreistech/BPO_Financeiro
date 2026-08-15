"""Tela de listagem de Empresas."""

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

from application.dto.empresa_dto import EmpresaResponseDTO
from application.use_cases.empresa_use_cases import (
    CadastrarEmpresaUseCase,
    EditarEmpresaUseCase,
    ExcluirEmpresaUseCase,
    ListarEmpresasUseCase,
    ObterEmpresaUseCase,
)
from application.use_cases.escritorio_use_cases import ListarEscritoriosUseCase
from ui.views.empresa_form_view import EmpresaFormView
from ui.views.table_helpers import (
    configurar_tabela_padrao,
    criar_item_centralizado,
)


class EmpresasView(QWidget):
    """Tela de listagem e gerenciamento de empresas."""

    COLUNAS = [
        "ID",
        "Escritorio",
        "Razao Social",
        "Nome Fantasia",
        "CNPJ",
        "Regime",
        "Ativo",
    ]

    def __init__(
        self,
        listar: ListarEmpresasUseCase,
        obter: ObterEmpresaUseCase,
        criar: CadastrarEmpresaUseCase,
        editar: EditarEmpresaUseCase,
        excluir: ExcluirEmpresaUseCase,
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
        titulo = QLabel("Empresas")
        titulo.setObjectName("viewTitulo")
        cabecalho.addWidget(titulo)
        cabecalho.addStretch()

        btn_novo = QPushButton("Nova Empresa")
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
            escritorios = self._listar_escritorios.execute(skip=0, limit=1000)
            mapa_esc = {e.id: e.nome for e in escritorios if e.id is not None}
        except Exception:
            mapa_esc = {}

        try:
            empresas = self._listar.execute(skip=0, limit=500)
        except Exception as e:
            QMessageBox.warning(self, "Erro", f"Erro ao listar empresas: {e}")
            return

        self._tabela.setRowCount(len(empresas))
        for i, emp in enumerate(empresas):
            self._tabela.setItem(i, 0, criar_item_centralizado(str(emp.id or "")))
            self._tabela.setItem(
                i, 1, QTableWidgetItem(mapa_esc.get(emp.escritorio_id, "—"))
            )
            self._tabela.setItem(i, 2, QTableWidgetItem(emp.razao_social))
            self._tabela.setItem(i, 3, QTableWidgetItem(emp.nome_fantasia))
            self._tabela.setItem(i, 4, QTableWidgetItem(emp.cnpj))
            self._tabela.setItem(i, 5, QTableWidgetItem(emp.regime_tributario))
            self._tabela.setItem(
                i, 6, criar_item_centralizado("Sim" if emp.ativo else "Nao")
            )

    def _obter_selecionado(self) -> EmpresaResponseDTO | None:
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
            return [
                (e.id, e.nome) for e in escritorios if e.id is not None
            ]
        except Exception:
            return []

    def _novo(self) -> None:
        opcoes = self._obter_opcoes_escritorio()
        if not opcoes:
            QMessageBox.information(
                self,
                "Aviso",
                "Cadastre um escritorio antes de cadastrar empresas.",
            )
            return
        form = EmpresaFormView(
            criar_use_case=self._criar,
            editar_use_case=self._editar,
            opcoes_escritorio=opcoes,
            parent=self,
        )
        if form.exec() == EmpresaFormView.DialogCode.Accepted:
            self.atualizar_lista()

    def _editar_selecionado(self) -> None:
        emp = self._obter_selecionado()
        if emp is None:
            QMessageBox.information(
                self, "Selecao", "Selecione uma empresa para editar."
            )
            return
        opcoes = self._obter_opcoes_escritorio()
        form = EmpresaFormView(
            criar_use_case=self._criar,
            editar_use_case=self._editar,
            opcoes_escritorio=opcoes,
            parent=self,
            empresa=emp,
        )
        if form.exec() == EmpresaFormView.DialogCode.Accepted:
            self.atualizar_lista()

    def _excluir_selecionado(self) -> None:
        emp = self._obter_selecionado()
        if emp is None:
            QMessageBox.information(
                self, "Selecao", "Selecione uma empresa para excluir."
            )
            return
        resposta = QMessageBox.question(
            self,
            "Confirmar exclusao",
            f"Deseja excluir a empresa '{emp.nome_fantasia}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            try:
                self._excluir.execute(emp.id)
                self.atualizar_lista()
                QMessageBox.information(self, "Sucesso", "Empresa excluida com sucesso.")
            except ValueError as e:
                QMessageBox.warning(self, "Erro", str(e))
