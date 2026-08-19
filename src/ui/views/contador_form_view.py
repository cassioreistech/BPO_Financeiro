"""Formulario de cadastro/edicao de Contador."""

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

from application.dto.contador_dto import (
    CadastrarContadorDTO,
    ContadorResponseDTO,
    EditarContadorDTO,
)
from application.use_cases.contador_use_cases import (
    CadastrarContadorUseCase,
    EditarContadorUseCase,
)


class ContadorFormView(QDialog):
    """Formulario modal para criar ou editar um contador."""

    def __init__(
        self,
        criar_use_case: CadastrarContadorUseCase,
        editar_use_case: EditarContadorUseCase,
        opcoes_escritorio: list[tuple[int, str]],
        parent: QWidget | None = None,
        contador: ContadorResponseDTO | None = None,
    ) -> None:
        super().__init__(parent)
        self._criar = criar_use_case
        self._editar = editar_use_case
        self._opcoes_escritorio = opcoes_escritorio
        self._contador = contador
        self._editando = contador is not None

        self._configurar_janela()
        self._montar_formulario()
        self._preencher_se_edicao()

    def _configurar_janela(self) -> None:
        titulo = "Editar Contador" if self._editando else "Novo Contador"
        self.setWindowTitle(titulo)
        self.setMinimumWidth(450)
        self.setModal(True)

    def _montar_formulario(self) -> None:
        layout = QVBoxLayout(self)

        titulo = QLabel("Editar Contador" if self._editando else "Novo Contador")
        titulo.setObjectName("formTitulo")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(12)

        self._combo_escritorio = QComboBox()
        for eid, nome in self._opcoes_escritorio:
            self._combo_escritorio.addItem(nome, eid)
        form.addRow("Escritorio:", self._combo_escritorio)

        self._campo_nome = QLineEdit()
        self._campo_nome.setPlaceholderText("Nome completo do contador")
        form.addRow("Nome:", self._campo_nome)

        self._campo_crc = QLineEdit()
        self._campo_crc.setPlaceholderText("XX-XXXXXX/X (opcional)")
        self._campo_crc.setMaxLength(12)
        form.addRow("CRC:", self._campo_crc)

        self._campo_email = QLineEdit()
        self._campo_email.setPlaceholderText("contador@escritorio.com.br")
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
        if self._contador is None:
            return

        idx_esc = self._combo_escritorio.findData(self._contador.escritorio_id)
        if idx_esc >= 0:
            self._combo_escritorio.setCurrentIndex(idx_esc)

        self._campo_nome.setText(self._contador.nome)
        if self._contador.crc:
            self._campo_crc.setText(self._contador.crc)
        if self._contador.email:
            self._campo_email.setText(self._contador.email)
        if self._contador.telefone:
            self._campo_telefone.setText(self._contador.telefone)

    def _salvar(self) -> None:
        escritorio_id = self._combo_escritorio.currentData()
        nome = self._campo_nome.text().strip()
        crc = self._campo_crc.text().strip() or None
        email = self._campo_email.text().strip() or None
        telefone = self._campo_telefone.text().strip() or None

        if not nome:
            QMessageBox.warning(
                self, "Campo obrigatório", "O nome não pode ser vazio."
            )
            return

        try:
            if self._editando and self._contador is not None:
                dto_editar = EditarContadorDTO(
                    id=self._contador.id,
                    escritorio_id=escritorio_id,
                    nome=nome,
                    crc=crc,
                    email=email,
                    telefone=telefone,
                )
                self._editar.execute(dto_editar)
                QMessageBox.information(
                    self, "Sucesso", "Contador atualizado com sucesso."
                )
            else:
                dto_criar = CadastrarContadorDTO(
                    escritorio_id=escritorio_id,
                    nome=nome,
                    crc=crc,
                    email=email,
                    telefone=telefone,
                )
                self._criar.execute(dto_criar)
                QMessageBox.information(self, "Sucesso", "Contador criado com sucesso.")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Erro", str(e))
