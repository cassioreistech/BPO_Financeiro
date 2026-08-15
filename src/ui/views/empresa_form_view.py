"""Formulario de cadastro/edicao de Empresa."""

from __future__ import annotations

import re

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
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
from domain.value_objects.cnpj import CNPJ


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
        self._ignorar_sinal = False

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

        self._campo_cnpj = QLineEdit()
        self._campo_cnpj.setPlaceholderText("00.000.000/0000-00")
        validator = QRegularExpressionValidator(
            QRegularExpression(r"\d{0,14}")
        )
        self._campo_cnpj.setValidator(validator)
        self._campo_cnpj.textChanged.connect(self._formatar_cnpj)
        form.addRow("CNPJ:", self._campo_cnpj)

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
        self._campo_telefone.setMaxLength(11)
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

    def _formatar_cnpj(self, texto: str) -> None:
        if self._ignorar_sinal:
            return
        self._ignorar_sinal = True
        digitos = re.sub(r"\D", "", texto)
        if len(digitos) > 14:
            digitos = digitos[:14]
        formatado = self._aplicar_mascara_cnpj(digitos)
        self._campo_cnpj.setText(formatado)
        self._campo_cnpj.setCursorPosition(len(formatado))
        self._ignorar_sinal = False

    @staticmethod
    def _aplicar_mascara_cnpj(digitos: str) -> str:
        tamanho = len(digitos)
        if tamanho <= 2:
            return digitos
        if tamanho <= 5:
            return f"{digitos[:2]}.{digitos[2:]}"
        if tamanho <= 8:
            return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:]}"
        if tamanho <= 12:
            return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:8]}/{digitos[8:]}"
        return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:8]}/{digitos[8:12]}-{digitos[12:]}"

    def _obter_cnpj_digitos(self) -> str:
        return re.sub(r"\D", "", self._campo_cnpj.text())

    def _preencher_se_edicao(self) -> None:
        if self._empresa is None:
            return

        idx_esc = self._combo_escritorio.findData(self._empresa.escritorio_id)
        if idx_esc >= 0:
            self._combo_escritorio.setCurrentIndex(idx_esc)

        digitos = re.sub(r"\D", "", self._empresa.cnpj)
        self._campo_cnpj.setText(self._aplicar_mascara_cnpj(digitos))
        self._campo_razao.setText(self._empresa.razao_social)
        self._campo_fantasia.setText(self._empresa.nome_fantasia)

        idx_regime = self._combo_regime.findText(self._empresa.regime_tributario)
        if idx_regime >= 0:
            self._combo_regime.setCurrentIndex(idx_regime)

        if self._empresa.email_financeiro:
            self._campo_email.setText(self._empresa.email_financeiro)
        if self._empresa.telefone_financeiro:
            self._campo_telefone.setText(self._empresa.telefone_financeiro)

    def _salvar(self) -> None:
        escritorio_id = self._combo_escritorio.currentData()
        cnpj = self._obter_cnpj_digitos()
        razao = self._campo_razao.text().strip()
        fantasia = self._campo_fantasia.text().strip()
        regime = self._combo_regime.currentText()
        email = self._campo_email.text().strip() or None
        telefone = self._campo_telefone.text().strip() or None

        if not razao:
            QMessageBox.warning(
                self, "Campo obrigatorio", "A razao social nao pode ser vazia."
            )
            return
        if not fantasia:
            QMessageBox.warning(
                self, "Campo obrigatorio", "O nome fantasia nao pode ser vazio."
            )
            return
        if not cnpj:
            QMessageBox.warning(
                self, "Campo obrigatorio", "O CNPJ nao pode ser vazio."
            )
            return

        try:
            CNPJ(cnpj)
        except ValueError as e:
            msg = f"CNPJ: {cnpj}\n\n{e}"
            if len(cnpj) >= 12:
                base = cnpj[:12].ljust(12, "0")
                dv_corretos = CNPJ.calcular_digitos_verificadores(base)
                cnpj_correto = base + dv_corretos
                msg += f"\n\nCNPJ correto: {cnpj_correto}"
            QMessageBox.warning(self, "CNPJ invalido", msg)
            return

        try:
            if self._editando and self._empresa is not None:
                dto_editar = EditarEmpresaDTO(
                    id=self._empresa.id,
                    escritorio_id=escritorio_id,
                    cnpj=cnpj,
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
                    cnpj=cnpj,
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
