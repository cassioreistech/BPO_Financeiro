"""Formulario de cadastro/edicao de Escritorio."""

from __future__ import annotations

from PySide6.QtWidgets import (
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

from application.dto.escritorio_dto import (
    CriarEscritorioDTO,
    EditarEscritorioDTO,
    EscritorioResponseDTO,
)
from application.use_cases.escritorio_use_cases import (
    CriarEscritorioUseCase,
    EditarEscritorioUseCase,
)


class EscritorioFormView(QDialog):
    """Formulario modal para criar ou editar um escritorio."""

    def __init__(
        self,
        criar_use_case: CriarEscritorioUseCase,
        editar_use_case: EditarEscritorioUseCase,
        parent: QWidget | None = None,
        escritorio: EscritorioResponseDTO | None = None,
    ) -> None:
        super().__init__(parent)
        self._criar = criar_use_case
        self._editar = editar_use_case
        self._escritorio = escritorio
        self._editando = escritorio is not None

        self._configurar_janela()
        self._montar_formulario()
        self._preencher_se_edicao()

    def _configurar_janela(self) -> None:
        titulo = "Editar Escritorio" if self._editando else "Novo Escritorio"
        self.setWindowTitle(titulo)
        self.setMinimumWidth(420)
        self.setModal(True)

    def _montar_formulario(self) -> None:
        layout = QVBoxLayout(self)

        titulo = QLabel("Editar Escritorio" if self._editando else "Novo Escritorio")
        titulo.setObjectName("formTitulo")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(12)

        self._campo_nome = QLineEdit()
        self._campo_nome.setPlaceholderText("Nome do escritorio")
        form.addRow("Nome:", self._campo_nome)

        self._campo_cnpj = QLineEdit()
        self._campo_cnpj.setPlaceholderText("Somente digitos")
        self._campo_cnpj.setMaxLength(14)
        form.addRow("CNPJ/CPF:", self._campo_cnpj)

        self._campo_email = QLineEdit()
        self._campo_email.setPlaceholderText("email@escritorio.com.br")
        form.addRow("Email:", self._campo_email)

        self._campo_telefone = QLineEdit()
        self._campo_telefone.setPlaceholderText("(XX) XXXXX-XXXX")
        self._campo_telefone.setMaxLength(11)
        form.addRow("Telefone:", self._campo_telefone)

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

    def _preencher_se_edicao(self) -> None:
        if self._escritorio is None:
            return
        self._campo_nome.setText(self._escritorio.nome)
        self._campo_cnpj.setText(self._escritorio.cnpj_cpf)
        if self._escritorio.email:
            self._campo_email.setText(self._escritorio.email)
        if self._escritorio.telefone:
            self._campo_telefone.setText(self._escritorio.telefone)

    def _salvar(self) -> None:
        nome = self._campo_nome.text().strip()
        cnpj = self._campo_cnpj.text().strip()
        email = self._campo_email.text().strip() or None
        telefone = self._campo_telefone.text().strip() or None

        if not nome:
            QMessageBox.warning(self, "Campo obrigatorio", "O nome nao pode ser vazio.")
            return
        if not cnpj:
            QMessageBox.warning(
                self, "Campo obrigatorio", "O CNPJ/CPF nao pode ser vazio."
            )
            return

        try:
            if self._editando and self._escritorio is not None:
                dto_editar = EditarEscritorioDTO(
                    id=self._escritorio.id,
                    nome=nome,
                    cnpj_cpf=cnpj,
                    email=email,
                    telefone=telefone,
                )
                self._editar.execute(dto_editar)
                QMessageBox.information(
                    self, "Sucesso", "Escritorio atualizado com sucesso."
                )
            else:
                dto_criar = CriarEscritorioDTO(
                    nome=nome,
                    cnpj_cpf=cnpj,
                    email=email,
                    telefone=telefone,
                )
                self._criar.execute(dto_criar)
                QMessageBox.information(
                    self, "Sucesso", "Escritorio criado com sucesso."
                )
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Erro", str(e))
