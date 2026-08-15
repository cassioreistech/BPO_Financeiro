"""Formulario de cadastro/edicao de PlanoConta."""

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
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from application.dto.plano_conta_dto import (
    CadastrarPlanoContaDTO,
    EditarPlanoContaDTO,
    PlanoContaResponseDTO,
)
from application.use_cases.plano_conta_use_cases import (
    CadastrarPlanoContaUseCase,
    EditarPlanoContaUseCase,
    ListarPlanoContaUseCase,
)
from domain.enums.tipo_plano_conta import TipoPlanoConta


class PlanoContaFormView(QDialog):
    """Formulario modal para criar ou editar uma conta do plano."""

    TIPOS = [t.value for t in TipoPlanoConta]

    def __init__(
        self,
        criar_use_case: CadastrarPlanoContaUseCase,
        editar_use_case: EditarPlanoContaUseCase,
        listar_use_case: ListarPlanoContaUseCase,
        opcoes_escritorio: list[tuple[int, str]],
        escritorio_id: int | None = None,
        parent: QWidget | None = None,
        plano: PlanoContaResponseDTO | None = None,
    ) -> None:
        super().__init__(parent)
        self._criar = criar_use_case
        self._editar = editar_use_case
        self._listar = listar_use_case
        self._opcoes_escritorio = opcoes_escritorio
        self._plano = plano
        self._editando = plano is not None

        self._configurar_janela()
        self._montar_formulario()
        self._preencher_se_edicao()
        self._selecionar_escritorio_inicial(escritorio_id)
        self._atualizar_opcoes_pai()

    def _selecionar_escritorio_inicial(self, escritorio_id: int | None) -> None:
        if escritorio_id is None:
            return
        idx = self._combo_escritorio.findData(escritorio_id)
        if idx >= 0:
            self._combo_escritorio.setCurrentIndex(idx)

    def _configurar_janela(self) -> None:
        titulo = "Editar Plano de Conta" if self._editando else "Nova Conta do Plano"
        self.setWindowTitle(titulo)
        self.setMinimumWidth(480)
        self.setModal(True)

    def _montar_formulario(self) -> None:
        layout = QVBoxLayout(self)

        titulo = QLabel(
            "Editar Plano de Conta" if self._editando else "Nova Conta do Plano"
        )
        titulo.setObjectName("formTitulo")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(12)

        self._combo_escritorio = QComboBox()
        for eid, nome in self._opcoes_escritorio:
            self._combo_escritorio.addItem(nome, eid)
        self._combo_escritorio.currentIndexChanged.connect(
            self._atualizar_opcoes_pai
        )
        form.addRow("Escritorio:", self._combo_escritorio)

        self._campo_codigo = QLineEdit()
        self._campo_codigo.setPlaceholderText("Ex: 1.01.001")
        form.addRow("Codigo:", self._campo_codigo)

        self._campo_nome = QLineEdit()
        self._campo_nome.setPlaceholderText("Nome da conta")
        form.addRow("Nome:", self._campo_nome)

        self._combo_tipo = QComboBox()
        self._combo_tipo.addItems(self.TIPOS)
        form.addRow("Tipo:", self._combo_tipo)

        self._spin_nivel = QSpinBox()
        self._spin_nivel.setMinimum(1)
        self._spin_nivel.setMaximum(10)
        self._spin_nivel.setValue(1)
        form.addRow("Nivel:", self._spin_nivel)

        self._combo_pai = QComboBox()
        self._combo_pai.addItem("Nenhum (conta raiz)", None)
        form.addRow("Conta Pai:", self._combo_pai)

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
        if self._plano is None:
            return

        idx_esc = self._combo_escritorio.findData(self._plano.escritorio_id)
        if idx_esc >= 0:
            self._combo_escritorio.setCurrentIndex(idx_esc)

        self._campo_codigo.setText(self._plano.codigo)
        self._campo_nome.setText(self._plano.nome)

        idx_tipo = self._combo_tipo.findText(self._plano.tipo)
        if idx_tipo >= 0:
            self._combo_tipo.setCurrentIndex(idx_tipo)

        self._spin_nivel.setValue(self._plano.nivel)

        if self._plano.pai_id is not None:
            idx_pai = self._combo_pai.findData(self._plano.pai_id)
            if idx_pai >= 0:
                self._combo_pai.setCurrentIndex(idx_pai)

    def _atualizar_opcoes_pai(self) -> None:
        escritorio_id = self._combo_escritorio.currentData()
        self._combo_pai.clear()
        self._combo_pai.addItem("Nenhum (conta raiz)", None)
        if escritorio_id is None:
            return

        try:
            contas = self._listar.execute(
                escritorio_id=escritorio_id, skip=0, limit=500
            )
        except Exception:
            return

        for conta in contas:
            if self._editando and self._plano is not None and conta.id == self._plano.id:
                continue
            self._combo_pai.addItem(f"{conta.codigo} - {conta.nome}", conta.id)

    def _salvar(self) -> None:
        escritorio_id = self._combo_escritorio.currentData()
        codigo = self._campo_codigo.text().strip()
        nome = self._campo_nome.text().strip()
        tipo = self._combo_tipo.currentText()
        nivel = self._spin_nivel.value()
        pai_id = self._combo_pai.currentData()

        if not codigo:
            QMessageBox.warning(
                self, "Campo obrigatorio", "O codigo nao pode ser vazio."
            )
            return
        if not nome:
            QMessageBox.warning(
                self, "Campo obrigatorio", "O nome nao pode ser vazio."
            )
            return

        try:
            if self._editando and self._plano is not None:
                dto_editar = EditarPlanoContaDTO(
                    id=self._plano.id,
                    escritorio_id=escritorio_id,
                    codigo=codigo,
                    nome=nome,
                    tipo=tipo,
                    nivel=nivel,
                    pai_id=pai_id,
                )
                self._editar.execute(dto_editar)
                QMessageBox.information(
                    self, "Sucesso", "Conta do plano atualizada com sucesso."
                )
            else:
                dto_criar = CadastrarPlanoContaDTO(
                    escritorio_id=escritorio_id,
                    codigo=codigo,
                    nome=nome,
                    tipo=tipo,
                    nivel=nivel,
                    pai_id=pai_id,
                )
                self._criar.execute(dto_criar)
                QMessageBox.information(self, "Sucesso", "Conta do plano criada com sucesso.")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Erro", str(e))
