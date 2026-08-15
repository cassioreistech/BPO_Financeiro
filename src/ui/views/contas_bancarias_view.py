"""Tela de listagem de Contas Bancarias."""

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

from application.dto.conta_bancaria_dto import ContaBancariaResponseDTO
from application.services.empresa_context_service import EmpresaContextService
from application.use_cases.conta_bancaria_use_cases import (
    CadastrarContaBancariaUseCase,
    DesativarContaBancariaUseCase,
    EditarContaBancariaUseCase,
    ListarContasBancariasUseCase,
    ObterContaBancariaUseCase,
)
from application.use_cases.empresa_use_cases import ListarEmpresasUseCase
from ui.views.conta_bancaria_form_view import ContaBancariaFormView
from ui.views.table_helpers import (
    configurar_tabela_padrao,
    criar_item_centralizado,
)


class ContasBancariasView(QWidget):
    """Tela de listagem e gerenciamento de contas bancarias."""

    COLUNAS = [
        "ID",
        "Empresa",
        "Banco",
        "Agencia",
        "Conta",
        "Tipo",
        "Descricao",
        "Ativo",
    ]

    def __init__(
        self,
        listar: ListarContasBancariasUseCase,
        obter: ObterContaBancariaUseCase,
        criar: CadastrarContaBancariaUseCase,
        editar: EditarContaBancariaUseCase,
        desativar: DesativarContaBancariaUseCase,
        listar_empresas: ListarEmpresasUseCase,
        contexto_empresa: EmpresaContextService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._listar = listar
        self._obter = obter
        self._criar = criar
        self._editar = editar
        self._desativar = desativar
        self._listar_empresas = listar_empresas
        self._contexto_empresa = contexto_empresa
        self._montar()
        self.carregar_empresa_ativa()

    def _montar(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        cabecalho = QHBoxLayout()
        titulo = QLabel("Contas Bancarias")
        titulo.setObjectName("viewTitulo")
        cabecalho.addWidget(titulo)
        cabecalho.addStretch()

        btn_novo = QPushButton("Nova Conta Bancaria")
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
        btn_desativar = QPushButton("Desativar")
        btn_desativar.clicked.connect(self._desativar_selecionado)
        botoes.addWidget(btn_desativar)
        botoes.addStretch()
        layout.addLayout(botoes)

    def carregar_empresa_ativa(self) -> None:
        """Recarrega a listagem usando a empresa ativa do contexto global."""
        self.atualizar_lista()

    def atualizar_lista(self) -> None:
        try:
            empresas = self._listar_empresas.execute(skip=0, limit=1000)
            mapa_emp = {
                e.id: e.nome_fantasia for e in empresas if e.id is not None
            }
        except Exception:
            mapa_emp = {}

        empresa_id = self._contexto_empresa.get_empresa_ativa()
        try:
            contas = self._listar.execute(
                empresa_id=empresa_id, skip=0, limit=500
            )
        except Exception as e:
            QMessageBox.warning(
                self, "Erro", f"Erro ao listar contas bancarias: {e}"
            )
            return

        self._tabela.setRowCount(len(contas))
        for i, conta in enumerate(contas):
            self._tabela.setItem(
                i, 0, criar_item_centralizado(str(conta.id or ""))
            )
            self._tabela.setItem(
                i, 1, QTableWidgetItem(mapa_emp.get(conta.empresa_id, "—"))
            )
            self._tabela.setItem(i, 2, QTableWidgetItem(conta.banco_nome))
            self._tabela.setItem(i, 3, QTableWidgetItem(conta.agencia))
            self._tabela.setItem(i, 4, QTableWidgetItem(conta.conta))
            self._tabela.setItem(i, 5, QTableWidgetItem(conta.tipo))
            self._tabela.setItem(i, 6, QTableWidgetItem(conta.descricao))
            self._tabela.setItem(
                i, 7, criar_item_centralizado("Sim" if conta.ativo else "Nao")
            )

    def _obter_selecionado(self) -> ContaBancariaResponseDTO | None:
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
                "Cadastre uma empresa antes de cadastrar contas bancarias.",
            )
            return
        form = ContaBancariaFormView(
            criar_use_case=self._criar,
            editar_use_case=self._editar,
            opcoes_empresa=opcoes,
            empresa_id=self._contexto_empresa.get_empresa_ativa(),
            parent=self,
        )
        if form.exec() == ContaBancariaFormView.DialogCode.Accepted:
            self.atualizar_lista()

    def _editar_selecionado(self) -> None:
        conta = self._obter_selecionado()
        if conta is None:
            QMessageBox.information(
                self, "Selecao", "Selecione uma conta bancaria para editar."
            )
            return
        opcoes = self._obter_opcoes_empresa()
        form = ContaBancariaFormView(
            criar_use_case=self._criar,
            editar_use_case=self._editar,
            opcoes_empresa=opcoes,
            parent=self,
            conta=conta,
        )
        if form.exec() == ContaBancariaFormView.DialogCode.Accepted:
            self.atualizar_lista()

    def _desativar_selecionado(self) -> None:
        conta = self._obter_selecionado()
        if conta is None:
            QMessageBox.information(
                self, "Selecao", "Selecione uma conta bancaria para desativar."
            )
            return
        if not conta.ativo:
            QMessageBox.information(self, "Aviso", "Esta conta ja esta desativada.")
            return
        resposta = QMessageBox.question(
            self,
            "Confirmar desativacao",
            f"Deseja desativar a conta '{conta.banco_nome} - {conta.conta}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resposta == QMessageBox.StandardButton.Yes:
            try:
                self._desativar.execute(conta.id)
                self.atualizar_lista()
                QMessageBox.information(
                    self, "Sucesso", "Conta bancaria desativada com sucesso."
                )
            except ValueError as e:
                QMessageBox.warning(self, "Erro", str(e))
