"""Formulario de cadastro/edicao de Empresa."""

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
from ui.views.formatadores import (
    aplicar_formatacao_campo,
    formatar_cnpj_cpf,
    formatar_telefone,
    limpar_documento,
)

from application.dto.empresa_dto import (
    CadastrarEmpresaDTO,
    EditarEmpresaDTO,
    EmpresaResponseDTO,
)
from application.use_cases.empresa_use_cases import (
    CadastrarEmpresaUseCase,
    EditarEmpresaUseCase,
)
from domain.enums.regime_tributario import RegimeTributario
from domain.value_objects.documento import Documento


class EmpresaFormView(QDialog):
    """Formulario modal para criar ou editar uma empresa."""

    REGIMES = [r.value for r in RegimeTributario]

    def __init__(
        self,
        criar_use_case: CadastrarEmpresaUseCase,
        editar_use_case: EditarEmpresaUseCase,
        opcoes_escritorio: list[tuple[int, str]],
        parent: QWidget | None = None,
        empresa: EmpresaResponseDTO | None = None,
    ) -> None:
        super().__init__(parent)
        self._criar = criar_use_case
        self._editar = editar_use_case
        self._opcoes_escritorio = opcoes_escritorio
        self._empresa = empresa
        self._editando = empresa is not None

        self._configurar_janela()
        self._montar_formulario()
        self._preencher_se_edicao()

    def _configurar_janela(self) -> None:
        titulo = "Editar Empresa" if self._editando else "Nova Empresa"
        self.setWindowTitle(titulo)
        self.setMinimumWidth(520)
        self.setModal(True)

    def _montar_formulario(self) -> None:
        layout = QVBoxLayout(self)

        titulo = QLabel("Editar Empresa" if self._editando else "Nova Empresa")
        titulo.setObjectName("formTitulo")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(12)

        self._combo_escritorio = QComboBox()
        for eid, nome in self._opcoes_escritorio:
            self._combo_escritorio.addItem(nome, eid)
        form.addRow("Escritorio:", self._combo_escritorio)

        self._campo_documento = QLineEdit()
        self._campo_documento.setPlaceholderText("Cole o CNPJ ou CPF aqui (com ou sem pontuacao)")
        self._campo_documento.setMaxLength(18)
        self._campo_documento.textChanged.connect(self._ao_mudar_documento)
        form.addRow("CNPJ/CPF:", self._campo_documento)

        self._campo_razao = QLineEdit()
        self._campo_razao.setPlaceholderText("Razao social da empresa")
        form.addRow("Razao Social:", self._campo_razao)

        self._campo_fantasia = QLineEdit()
        self._campo_fantasia.setPlaceholderText("Nome comercial")
        form.addRow("Nome Fantasia:", self._campo_fantasia)

        self._combo_regime = QComboBox()
        self._combo_regime.addItems(self.REGIMES)
        form.addRow("Regime Tributario:", self._combo_regime)

        self._campo_email = QLineEdit()
        self._campo_email.setPlaceholderText("financeiro@empresa.com.br")
        form.addRow("Email Financeiro:", self._campo_email)

        self._campo_telefone = QLineEdit()
        self._campo_telefone.setPlaceholderText("(XX) XXXXX-XXXX")
        self._campo_telefone.setMaxLength(16)
        self._campo_telefone.textChanged.connect(self._ao_mudar_telefone)
        form.addRow("Telefone Financeiro:", self._campo_telefone)

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

    def _ao_mudar_documento(self, texto: str) -> None:
        """Formata CNPJ ou CPF automaticamente ao digitar ou colar."""
        aplicar_formatacao_campo(self._campo_documento, formatar_cnpj_cpf, texto)

    def _ao_mudar_telefone(self, texto: str) -> None:
        """Formata telefone automaticamente ao digitar ou colar."""
        aplicar_formatacao_campo(self._campo_telefone, formatar_telefone, texto)

    def _obter_documento_digitos(self) -> str:
        return limpar_documento(self._campo_documento.text())

    def _preencher_se_edicao(self) -> None:
        if self._empresa is None:
            return

        idx_esc = self._combo_escritorio.findData(self._empresa.escritorio_id)
        if idx_esc >= 0:
            self._combo_escritorio.setCurrentIndex(idx_esc)

        # EmpresaResponseDTO tem cnpj como string (compatibilidade)
        self._campo_documento.setText(formatar_cnpj_cpf(self._empresa.cnpj))
        self._campo_razao.setText(self._empresa.razao_social)
        self._campo_fantasia.setText(self._empresa.nome_fantasia)

        idx_regime = self._combo_regime.findText(self._empresa.regime_tributario)
        if idx_regime >= 0:
            self._combo_regime.setCurrentIndex(idx_regime)

        if self._empresa.email_financeiro:
            self._campo_email.setText(self._empresa.email_financeiro)
        if self._empresa.telefone_financeiro:
            self._campo_telefone.setText(formatar_telefone(self._empresa.telefone_financeiro))

    def _salvar(self) -> None:
        escritorio_id = self._combo_escritorio.currentData()
        documento = self._obter_documento_digitos()
        razao = self._campo_razao.text().strip()
        fantasia = self._campo_fantasia.text().strip()
        regime = self._combo_regime.currentText()
        email = self._campo_email.text().strip() or None
        telefone = self._campo_telefone.text().strip() or None

        if not razao:
            QMessageBox.warning(
                self, "Campo obrigatório", "A razao social não pode ser vazia."
            )
            return
        if not fantasia:
            QMessageBox.warning(
                self, "Campo obrigatório", "O nome fantasia não pode ser vazio."
            )
            return
        if not documento:
            QMessageBox.warning(
                self, "Campo obrigatório", "O CNPJ/CPF não pode ser vazio."
            )
            return

        try:
            Documento(documento)
        except ValueError as e:
            msg = f"Documento: {documento}\n\n{e}"
            QMessageBox.warning(self, "Documento invalido", msg)
            return

        try:
            if self._editando and self._empresa is not None:
                dto_editar = EditarEmpresaDTO(
                    id=self._empresa.id,
                    escritorio_id=escritorio_id,
                    cnpj=documento,
                    razao_social=razao,
                    nome_fantasia=fantasia,
                    regime_tributario=regime,
                    email_financeiro=email,
                    telefone_financeiro=telefone,
                )
                self._editar.execute(dto_editar)
                QMessageBox.information(
                    self, "Sucesso", "Empresa atualizada com sucesso."
                )
            else:
                dto_criar = CadastrarEmpresaDTO(
                    escritorio_id=escritorio_id,
                    cnpj=documento,
                    razao_social=razao,
                    nome_fantasia=fantasia,
                    regime_tributario=regime,
                    email_financeiro=email,
                    telefone_financeiro=telefone,
                )
                self._criar.execute(dto_criar)
                QMessageBox.information(self, "Sucesso", "Empresa criada com sucesso.")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Erro", str(e))
