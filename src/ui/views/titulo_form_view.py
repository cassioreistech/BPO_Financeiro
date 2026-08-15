"""Formulario de cadastro/edicao de Titulo."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import cast

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from application.dto.titulo_dto import (
    CadastrarTituloDTO,
    EditarTituloDTO,
    TituloResponseDTO,
)
from application.use_cases.titulo_use_cases import (
    CadastrarTituloUseCase,
    EditarTituloUseCase,
)
from domain.enums.tipo_titulo import TipoTitulo


class TituloFormView(QDialog):
    """Formulario modal para criar ou editar um titulo financeiro."""

    TIPOS = [t.value for t in TipoTitulo]

    def __init__(
        self,
        criar_use_case: CadastrarTituloUseCase,
        editar_use_case: EditarTituloUseCase,
        opcoes_escritorio: list[tuple[int, str]],
        opcoes_empresa: list[tuple[int, str]],
        opcoes_plano_conta: list[tuple[int, str]],
        opcoes_centro_custo: list[tuple[int, str]],
        escritorio_id: int | None = None,
        parent: QWidget | None = None,
        titulo: TituloResponseDTO | None = None,
    ) -> None:
        super().__init__(parent)
        self._criar = criar_use_case
        self._editar = editar_use_case
        self._opcoes_escritorio = opcoes_escritorio
        self._opcoes_empresa = opcoes_empresa
        self._opcoes_plano_conta = opcoes_plano_conta
        self._opcoes_centro_custo = opcoes_centro_custo
        self._titulo = titulo
        self._editando = titulo is not None

        self._configurar_janela()
        self._montar_formulario()
        self._preencher_se_edicao()
        self._selecionar_escritorio_inicial(escritorio_id)

    def _configurar_janela(self) -> None:
        titulo = "Editar Titulo" if self._editando else "Novo Titulo"
        self.setWindowTitle(titulo)
        self.setMinimumWidth(520)
        self.setModal(True)

    def _montar_formulario(self) -> None:
        layout = QVBoxLayout(self)

        titulo = QLabel("Editar Titulo" if self._editando else "Novo Titulo")
        titulo.setObjectName("formTitulo")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(12)

        self._combo_escritorio = QComboBox()
        for eid, nome in self._opcoes_escritorio:
            self._combo_escritorio.addItem(nome, eid)
        form.addRow("Escritorio:", self._combo_escritorio)

        self._combo_empresa = QComboBox()
        self._combo_empresa.addItem("Nenhuma", None)
        for eid, nome in self._opcoes_empresa:
            self._combo_empresa.addItem(nome, eid)
        form.addRow("Empresa:", self._combo_empresa)

        self._combo_plano_conta = QComboBox()
        for pid, nome in self._opcoes_plano_conta:
            self._combo_plano_conta.addItem(nome, pid)
        form.addRow("Plano de Conta:", self._combo_plano_conta)

        self._combo_centro_custo = QComboBox()
        self._combo_centro_custo.addItem("Nenhum", None)
        for cid, nome in self._opcoes_centro_custo:
            self._combo_centro_custo.addItem(nome, cid)
        form.addRow("Centro de Custo:", self._combo_centro_custo)

        self._campo_descricao = QLineEdit()
        self._campo_descricao.setPlaceholderText("Descricao do titulo")
        form.addRow("Descricao:*", self._campo_descricao)

        self._combo_tipo = QComboBox()
        self._combo_tipo.addItems(self.TIPOS)
        form.addRow("Tipo:*", self._combo_tipo)

        self._campo_valor = QLineEdit()
        self._campo_valor.setPlaceholderText("0,00")
        form.addRow("Valor:*", self._campo_valor)

        self._date_emissao = QDateEdit()
        self._date_emissao.setCalendarPopup(True)
        self._date_emissao.setDate(self._to_qdate(date.today()))
        form.addRow("Data Emissao:*", self._date_emissao)

        self._date_vencimento = QDateEdit()
        self._date_vencimento.setCalendarPopup(True)
        self._date_vencimento.setDate(self._to_qdate(date.today()))
        form.addRow("Data Vencimento:*", self._date_vencimento)

        self._campo_observacao = QTextEdit()
        self._campo_observacao.setMaximumHeight(80)
        self._campo_observacao.setPlaceholderText("Observacoes opcionais")
        form.addRow("Observacao:", self._campo_observacao)

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
        if self._titulo is None:
            return

        self._selecionar_por_id(self._combo_escritorio, self._titulo.escritorio_id)
        self._selecionar_por_id(self._combo_empresa, self._titulo.empresa_id)
        self._selecionar_por_id(
            self._combo_plano_conta, self._titulo.plano_conta_id
        )
        self._selecionar_por_id(
            self._combo_centro_custo, self._titulo.centro_custo_id
        )

        self._campo_descricao.setText(self._titulo.descricao)

        idx_tipo = self._combo_tipo.findText(self._titulo.tipo)
        if idx_tipo >= 0:
            self._combo_tipo.setCurrentIndex(idx_tipo)

        self._campo_valor.setText(self._formatar_valor(self._titulo.valor))
        self._date_emissao.setDate(self._to_qdate(self._titulo.data_emissao))
        self._date_vencimento.setDate(self._to_qdate(self._titulo.data_vencimento))
        if self._titulo.observacao:
            self._campo_observacao.setPlainText(self._titulo.observacao)

    @staticmethod
    def _to_qdate(data: date) -> QDate:
        return QDate(data.year, data.month, data.day)

    @staticmethod
    def _selecionar_por_id(combo: QComboBox, id_: int | None) -> None:
        if id_ is None:
            return
        idx = combo.findData(id_)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    @staticmethod
    def _formatar_valor(valor: Decimal) -> str:
        return f"{valor:.2f}".replace(".", ",")

    def _selecionar_escritorio_inicial(self, escritorio_id: int | None) -> None:
        if escritorio_id is None:
            return
        idx = self._combo_escritorio.findData(escritorio_id)
        if idx >= 0:
            self._combo_escritorio.setCurrentIndex(idx)

    def _salvar(self) -> None:
        escritorio_id = self._combo_escritorio.currentData()
        empresa_id = self._combo_empresa.currentData()
        plano_conta_id = self._combo_plano_conta.currentData()
        centro_custo_id = self._combo_centro_custo.currentData()
        descricao = self._campo_descricao.text().strip()
        tipo = self._combo_tipo.currentText()
        valor_texto = self._campo_valor.text().strip().replace(",", ".")
        data_emissao = cast(date, self._date_emissao.date().toPython())
        data_vencimento = cast(date, self._date_vencimento.date().toPython())
        observacao = self._campo_observacao.toPlainText().strip() or None

        if not descricao:
            QMessageBox.warning(
                self, "Campo obrigatorio", "A descricao nao pode ser vazia."
            )
            return

        try:
            valor = Decimal(valor_texto)
        except (InvalidOperation, ValueError):
            QMessageBox.warning(
                self, "Valor invalido", "Informe um valor numerico valido."
            )
            return

        try:
            if self._editando and self._titulo is not None:
                dto_editar = EditarTituloDTO(
                    id=self._titulo.id,
                    escritorio_id=escritorio_id,
                    empresa_id=empresa_id,
                    plano_conta_id=plano_conta_id,
                    centro_custo_id=centro_custo_id,
                    descricao=descricao,
                    tipo=tipo,
                    valor=valor,
                    data_emissao=data_emissao,
                    data_vencimento=data_vencimento,
                    observacao=observacao,
                )
                self._editar.execute(dto_editar)
                QMessageBox.information(
                    self, "Sucesso", "Titulo atualizado com sucesso."
                )
            else:
                dto_criar = CadastrarTituloDTO(
                    escritorio_id=escritorio_id,
                    empresa_id=empresa_id,
                    plano_conta_id=plano_conta_id,
                    centro_custo_id=centro_custo_id,
                    descricao=descricao,
                    tipo=tipo,
                    valor=valor,
                    data_emissao=data_emissao,
                    data_vencimento=data_vencimento,
                    observacao=observacao,
                )
                self._criar.execute(dto_criar)
                QMessageBox.information(
                    self, "Sucesso", "Titulo criado com sucesso."
                )
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Erro", str(e))
