"""Formulario de cadastro/edicao de CentroCusto."""

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

from application.dto.centro_custo_dto import (
    CadastrarCentroCustoDTO,
    CentroCustoResponseDTO,
    EditarCentroCustoDTO,
)
from application.use_cases.centro_custo_use_cases import (
    CadastrarCentroCustoUseCase,
    EditarCentroCustoUseCase,
)


class CentroCustoFormView(QDialog):
    """Formulario modal para criar ou editar um centro de custo."""

    def __init__(
        self,
        criar_use_case: CadastrarCentroCustoUseCase,
        editar_use_case: EditarCentroCustoUseCase,
        opcoes_empresa: list[tuple[int, str]],
        empresa_id: int | None = None,
        parent: QWidget | None = None,
        centro: CentroCustoResponseDTO | None = None,
    ) -> None:
        super().__init__(parent)
        self._criar = criar_use_case
        self._editar = editar_use_case
        self._opcoes_empresa = opcoes_empresa
        self._centro = centro
        self._editando = centro is not None

        self._configurar_janela()
        self._montar_formulario()
        self._preencher_se_edicao()
        self._selecionar_empresa_inicial(empresa_id)

    def _selecionar_empresa_inicial(self, empresa_id: int | None) -> None:
        if empresa_id is None:
            return
        idx = self._combo_empresa.findData(empresa_id)
        if idx >= 0:
            self._combo_empresa.setCurrentIndex(idx)

    def _configurar_janela(self) -> None:
        titulo = "Editar Centro de Custo" if self._editando else "Novo Centro de Custo"
        self.setWindowTitle(titulo)
        self.setMinimumWidth(450)
        self.setModal(True)

    def _montar_formulario(self) -> None:
        layout = QVBoxLayout(self)

        titulo = QLabel(
            "Editar Centro de Custo" if self._editando else "Novo Centro de Custo"
        )
        titulo.setObjectName("formTitulo")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(12)

        self._combo_empresa = QComboBox()
        for eid, nome in self._opcoes_empresa:
            self._combo_empresa.addItem(nome, eid)
        form.addRow("Empresa:", self._combo_empresa)

        self._campo_codigo = QLineEdit()
        self._campo_codigo.setPlaceholderText("Ex: CC001")
        form.addRow("Codigo:", self._campo_codigo)

        self._campo_nome = QLineEdit()
        self._campo_nome.setPlaceholderText("Nome do centro de custo")
        form.addRow("Nome:", self._campo_nome)

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
        if self._centro is None:
            return

        idx_emp = self._combo_empresa.findData(self._centro.empresa_id)
        if idx_emp >= 0:
            self._combo_empresa.setCurrentIndex(idx_emp)

        self._campo_codigo.setText(self._centro.codigo)
        self._campo_nome.setText(self._centro.nome)

    def _salvar(self) -> None:
        empresa_id = self._combo_empresa.currentData()
        codigo = self._campo_codigo.text().strip()
        nome = self._campo_nome.text().strip()

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
            if self._editando and self._centro is not None:
                dto_editar = EditarCentroCustoDTO(
                    id=self._centro.id,
                    empresa_id=empresa_id,
                    codigo=codigo,
                    nome=nome,
                )
                self._editar.execute(dto_editar)
                QMessageBox.information(
                    self, "Sucesso", "Centro de custo atualizado com sucesso."
                )
            else:
                dto_criar = CadastrarCentroCustoDTO(
                    empresa_id=empresa_id,
                    codigo=codigo,
                    nome=nome,
                )
                self._criar.execute(dto_criar)
                QMessageBox.information(self, "Sucesso", "Centro de custo criado com sucesso.")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Erro", str(e))
