"""Formulario de cadastro/edicao de ContaBancaria."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from application.dto.conta_bancaria_dto import (
    CadastrarContaBancariaDTO,
    ContaBancariaResponseDTO,
    EditarContaBancariaDTO,
)
from application.use_cases.conta_bancaria_use_cases import (
    CadastrarContaBancariaUseCase,
    EditarContaBancariaUseCase,
)
from domain.enums.tipo_conta_bancaria import TipoContaBancaria

BANCOS_MAIS_USADOS = [
    ("001", "Banco do Brasil"),
    ("104", "Caixa Economica Federal"),
    ("341", "Itau Unibanco"),
    ("237", "Bradesco"),
    ("033", "Santander"),
    ("260", "Nu Pagamentos (Nubank)"),
    ("077", "Banco Inter"),
    ("336", "C6 Bank"),
    ("756", "Sicoob"),
    ("208", "BTG Pactual"),
]

TIPOS_CONTA = [t.value for t in TipoContaBancaria]


class ContaBancariaFormView(QDialog):
    """Formulario modal para criar ou editar uma conta bancaria."""

    def __init__(
        self,
        criar_use_case: CadastrarContaBancariaUseCase,
        editar_use_case: EditarContaBancariaUseCase,
        opcoes_empresa: list[tuple[int, str]],
        empresa_id: int | None = None,
        parent: QWidget | None = None,
        conta: ContaBancariaResponseDTO | None = None,
    ) -> None:
        super().__init__(parent)
        self._criar = criar_use_case
        self._editar = editar_use_case
        self._opcoes_empresa = opcoes_empresa
        self._empresa_id = empresa_id
        self._conta = conta
        self._editando = conta is not None

        self._configurar_janela()
        self._montar_formulario()
        self._preencher_se_edicao()
        self._selecionar_empresa_inicial(empresa_id)

    def _configurar_janela(self) -> None:
        titulo = "Editar Conta Bancaria" if self._editando else "Nova Conta Bancaria"
        self.setWindowTitle(titulo)
        self.setMinimumWidth(520)
        self.setModal(True)

    def _montar_formulario(self) -> None:
        layout = QVBoxLayout(self)

        titulo = QLabel(
            "Editar Conta Bancaria" if self._editando else "Nova Conta Bancaria"
        )
        titulo.setObjectName("formTitulo")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(12)

        self._combo_empresa = QComboBox()
        for eid, nome in self._opcoes_empresa:
            self._combo_empresa.addItem(nome, eid)
        form.addRow("Empresa:", self._combo_empresa)

        self._combo_banco_rapido = QComboBox()
        self._combo_banco_rapido.addItem("Selecionar banco...", None)
        for codigo, nome in BANCOS_MAIS_USADOS:
            self._combo_banco_rapido.addItem(f"{codigo} - {nome}", codigo)
        self._combo_banco_rapido.currentIndexChanged.connect(self._banco_rapido_selecionado)
        form.addRow("Banco (rapido):", self._combo_banco_rapido)

        self._campo_banco_nome = QLineEdit()
        self._campo_banco_nome.setPlaceholderText("Nome do banco")
        form.addRow("Nome do Banco:", self._campo_banco_nome)

        self._campo_banco_codigo = QLineEdit()
        self._campo_banco_codigo.setPlaceholderText("Codigo FEBRABAN (3 digitos)")
        self._campo_banco_codigo.setMaxLength(3)
        form.addRow("Codigo Banco:", self._campo_banco_codigo)

        self._campo_agencia = QLineEdit()
        self._campo_agencia.setPlaceholderText("Numero da agencia")
        form.addRow("Agencia:", self._campo_agencia)

        self._campo_conta = QLineEdit()
        self._campo_conta.setPlaceholderText("Numero da conta")
        form.addRow("Conta:", self._campo_conta)

        self._combo_tipo = QComboBox()
        self._combo_tipo.addItems(TIPOS_CONTA)
        form.addRow("Tipo:", self._combo_tipo)

        self._campo_descricao = QLineEdit()
        self._campo_descricao.setPlaceholderText("Ex: Conta principal, Conta PJ...")
        form.addRow("Descricao:", self._campo_descricao)

        layout.addLayout(form)

        botoes = QHBoxLayout()
        botoes.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btnCancelar")
        btn_cancelar.clicked.connect(self.reject)
        botoes.addWidget(btn_cancelar)

        btn_salvar = QPushButton("Salvar")
        btn_salvar.setObjectName("btnSalvar")
        btn_salvar.setDefault(True)
        btn_salvar.clicked.connect(self._salvar)
        botoes.addWidget(btn_salvar)

        layout.addLayout(botoes)

    def _banco_rapido_selecionado(self, index: int) -> None:
        codigo = self._combo_banco_rapido.currentData()
        if codigo is not None:
            for cod, nome in BANCOS_MAIS_USADOS:
                if cod == codigo:
                    self._campo_banco_nome.setText(nome)
                    self._campo_banco_codigo.setText(codigo)
                    break

    def _selecionar_empresa_inicial(self, empresa_id: int | None) -> None:
        if empresa_id is None:
            return
        idx = self._combo_empresa.findData(empresa_id)
        if idx >= 0:
            self._combo_empresa.setCurrentIndex(idx)

    def _preencher_se_edicao(self) -> None:
        if self._conta is None:
            return

        idx_emp = self._combo_empresa.findData(self._conta.empresa_id)
        if idx_emp >= 0:
            self._combo_empresa.setCurrentIndex(idx_emp)

        self._campo_banco_nome.setText(self._conta.banco_nome)
        self._campo_banco_codigo.setText(self._conta.banco_codigo)
        self._campo_agencia.setText(self._conta.agencia)
        self._campo_conta.setText(self._conta.conta)
        self._campo_descricao.setText(self._conta.descricao)

        idx_tipo = self._combo_tipo.findText(self._conta.tipo)
        if idx_tipo >= 0:
            self._combo_tipo.setCurrentIndex(idx_tipo)

    def _salvar(self) -> None:
        empresa_id = self._combo_empresa.currentData()
        banco_nome = self._campo_banco_nome.text().strip()
        banco_codigo = self._campo_banco_codigo.text().strip()
        agencia = self._campo_agencia.text().strip()
        conta = self._campo_conta.text().strip()
        tipo = self._combo_tipo.currentText()
        descricao = self._campo_descricao.text().strip()

        if not banco_nome:
            QMessageBox.warning(
                self, "Campo obrigatório", "O nome do banco não pode ser vazio."
            )
            return
        if not agencia:
            QMessageBox.warning(
                self, "Campo obrigatório", "A agencia não pode ser vazia."
            )
            return
        if not conta:
            QMessageBox.warning(
                self, "Campo obrigatório", "A conta não pode ser vazia."
            )
            return
        if not descricao:
            QMessageBox.warning(
                self, "Campo obrigatório", "A descricao não pode ser vazia."
            )
            return

        try:
            if self._editando and self._conta is not None:
                dto_editar = EditarContaBancariaDTO(
                    id=self._conta.id,
                    empresa_id=empresa_id,
                    banco_nome=banco_nome,
                    banco_codigo=banco_codigo,
                    agencia=agencia,
                    conta=conta,
                    tipo=tipo,
                    descricao=descricao,
                )
                self._editar.execute(dto_editar)
                QMessageBox.information(
                    self, "Sucesso", "Conta bancaria atualizada com sucesso."
                )
            else:
                dto_criar = CadastrarContaBancariaDTO(
                    empresa_id=empresa_id,
                    banco_nome=banco_nome,
                    banco_codigo=banco_codigo,
                    agencia=agencia,
                    conta=conta,
                    tipo=tipo,
                    descricao=descricao,
                )
                self._criar.execute(dto_criar)
                QMessageBox.information(
                    self, "Sucesso", "Conta bancaria criada com sucesso."
                )
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Erro", str(e))
