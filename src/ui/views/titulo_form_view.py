"""Formulario de cadastro/edicao de Titulo."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import cast

from dateutil.relativedelta import relativedelta
from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
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
from domain.enums.categoria_titulo import CategoriaTitulo
from domain.enums.tipo_titulo import TipoTitulo
from ui.views.status_formatter import formatar_status_titulo


class TituloFormView(QDialog):
    """Formulario modal para criar ou editar um titulo financeiro."""

    TIPOS = [t.value for t in TipoTitulo]
    CATEGORIAS = [c.value for c in CategoriaTitulo]

    def __init__(
        self,
        criar_use_case: CadastrarTituloUseCase,
        editar_use_case: EditarTituloUseCase,
        opcoes_escritorio: list[tuple[int, str]],
        opcoes_empresa: list[tuple[int, str, int]],
        plano_conta_id: int,
        empresa_id: int | None = None,
        contas_por_id: dict[int, str] | None = None,
        parent: QWidget | None = None,
        titulo: TituloResponseDTO | None = None,
    ) -> None:
        super().__init__(parent)
        self._criar = criar_use_case
        self._editar = editar_use_case
        self._opcoes_escritorio = opcoes_escritorio
        self._opcoes_empresa = opcoes_empresa
        self._mapa_empresa_escritorio = {
            eid: esc_id for eid, _, esc_id in opcoes_empresa
        }
        self._plano_conta_id = plano_conta_id
        self._titulo = titulo
        self._editando = titulo is not None
        self._contas_por_id = contas_por_id or {}
        self._somente_leitura = (
            self._editando and self._titulo is not None
            and self._titulo.status == "PAGO"
        )

        self._configurar_janela()
        self._montar_formulario()
        self._preencher_se_edicao()
        self._selecionar_escritorio_inicial(empresa_id)
        if self._somente_leitura:
            self._configurar_somente_leitura()

    def _configurar_janela(self) -> None:
        if self._somente_leitura:
            titulo = "Visualizar Titulo"
        elif self._editando:
            titulo = "Editar Titulo"
        else:
            titulo = "Novo Titulo"
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

        self._combo_empresa = QComboBox()
        self._combo_empresa.addItem("Selecione...", None)
        for eid, nome, _ in self._opcoes_empresa:
            self._combo_empresa.addItem(nome, eid)
        self._combo_empresa.currentIndexChanged.connect(
            self._empresa_alterada
        )
        form.addRow("Empresa:*", self._combo_empresa)

        self._combo_categoria = QComboBox()
        self._combo_categoria.addItems(self.CATEGORIAS)
        form.addRow("Categoria:*", self._combo_categoria)

        self._campo_numero_documento = QLineEdit()
        self._campo_numero_documento.setPlaceholderText(
            "Numero do boleto, nota fiscal etc."
        )
        form.addRow("No. Documento:", self._campo_numero_documento)

        self._campo_codigo_barras = QLineEdit()
        self._campo_codigo_barras.setPlaceholderText(
            "Codigo de barras do boleto"
        )
        form.addRow("Cod. Barras:", self._campo_codigo_barras)

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

        # Secao de replicacao (apenas para novo titulo)
        self._check_replicar = QCheckBox("Replicar lancamento mensal")
        self._check_replicar.setCursor(Qt.CursorShape.PointingHandCursor)
        form.addRow("", self._check_replicar)

        replica_layout = QHBoxLayout()
        replica_layout.setSpacing(8)
        lbl_vezes = QLabel("Vezes:")
        self._spin_vezes = QSpinBox()
        self._spin_vezes.setRange(2, 60)
        self._spin_vezes.setValue(12)
        self._spin_vezes.setSuffix("x")
        self._spin_vezes.setMinimumWidth(80)
        self._spin_vezes.setEnabled(False)
        replica_layout.addWidget(lbl_vezes)
        replica_layout.addWidget(self._spin_vezes)
        replica_layout.addStretch()
        form.addRow("", replica_layout)

        self._check_replicar.toggled.connect(self._spin_vezes.setEnabled)

        # Secao de dados da quitacao (somente leitura)
        self._secao_quitacao = QWidget()
        form_quitacao = QFormLayout(self._secao_quitacao)
        form_quitacao.setSpacing(12)
        form_quitacao.setContentsMargins(0, 16, 0, 0)

        self._label_status = QLabel()
        self._label_status.setStyleSheet("font-weight: bold;")
        form_quitacao.addRow("Status:", self._label_status)

        self._label_data_quitacao = QLabel()
        form_quitacao.addRow("Data Quitacao:", self._label_data_quitacao)

        self._label_valor_pago = QLabel()
        form_quitacao.addRow("Valor Pago:", self._label_valor_pago)

        self._label_conta_bancaria = QLabel()
        form_quitacao.addRow("Conta Bancaria:", self._label_conta_bancaria)

        self._label_forma_pagamento = QLabel()
        form_quitacao.addRow("Forma Pagamento:", self._label_forma_pagamento)

        self._label_observacao_quitacao = QLabel()
        self._label_observacao_quitacao.setWordWrap(True)
        form_quitacao.addRow(
            "Observacao Quitacao:", self._label_observacao_quitacao
        )

        layout.addLayout(form)
        layout.addWidget(self._secao_quitacao)

        botoes = QHBoxLayout()
        botoes.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btnCancelar")
        btn_cancelar.clicked.connect(self.reject)
        botoes.addWidget(btn_cancelar)

        self._btn_salvar = QPushButton("Salvar")
        self._btn_salvar.setObjectName("btnSalvar")
        self._btn_salvar.setDefault(True)
        self._btn_salvar.clicked.connect(self._salvar)
        botoes.addWidget(self._btn_salvar)

        layout.addLayout(botoes)

    def _preencher_se_edicao(self) -> None:
        if self._titulo is None:
            self._secao_quitacao.setVisible(False)
            return

        self._check_replicar.setVisible(False)
        self._spin_vezes.setVisible(False)
        self._check_replicar.setChecked(False)

        self._selecionar_por_id(self._combo_empresa, self._titulo.empresa_id)

        idx_categoria = self._combo_categoria.findText(self._titulo.categoria)
        if idx_categoria >= 0:
            self._combo_categoria.setCurrentIndex(idx_categoria)

        if self._titulo.numero_documento:
            self._campo_numero_documento.setText(self._titulo.numero_documento)

        if self._titulo.codigo_barras:
            self._campo_codigo_barras.setText(self._titulo.codigo_barras)

        self._campo_descricao.setText(self._titulo.descricao)

        idx_tipo = self._combo_tipo.findText(self._titulo.tipo)
        if idx_tipo >= 0:
            self._combo_tipo.setCurrentIndex(idx_tipo)

        self._campo_valor.setText(self._formatar_valor(self._titulo.valor))
        self._date_emissao.setDate(self._to_qdate(self._titulo.data_emissao))
        self._date_vencimento.setDate(self._to_qdate(self._titulo.data_vencimento))
        if self._titulo.observacao:
            self._campo_observacao.setPlainText(self._titulo.observacao)

        if self._titulo.status == "PAGO":
            self._preencher_quitacao()
        else:
            self._secao_quitacao.setVisible(False)

    def _preencher_quitacao(self) -> None:
        """Preenche os labels da secao de quitacao somente leitura."""
        if self._titulo is None:
            return

        self._label_status.setText(
            formatar_status_titulo(self._titulo.status, self._titulo.data_vencimento)
        )

        data_quitacao = self._titulo.data_quitacao
        self._label_data_quitacao.setText(
            data_quitacao.strftime("%d/%m/%Y")
            if data_quitacao is not None
            else "—"
        )

        valor_pago = self._titulo.valor_pago
        self._label_valor_pago.setText(
            self._formatar_valor(valor_pago) if valor_pago is not None else "—"
        )

        conta_id = self._titulo.conta_bancaria_id
        self._label_conta_bancaria.setText(
            self._contas_por_id.get(conta_id, "—")
            if conta_id is not None
            else "—"
        )

        self._label_forma_pagamento.setText(self._titulo.forma_pagamento)

        self._label_observacao_quitacao.setText(
            self._titulo.observacao_quitacao or "—"
        )

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

    def _configurar_somente_leitura(self) -> None:
        """Bloqueia edicao de titulo quitado e ajusta botoes."""
        campos = [
            self._combo_escritorio,
            self._combo_empresa,
            self._combo_categoria,
            self._campo_numero_documento,
            self._campo_codigo_barras,
            self._campo_descricao,
            self._combo_tipo,
            self._campo_valor,
            self._date_emissao,
            self._date_vencimento,
            self._campo_observacao,
        ]
        for campo in campos:
            campo.setEnabled(False)

        self._btn_salvar.setText("Fechar")
        self._btn_salvar.clicked.disconnect(self._salvar)
        self._btn_salvar.clicked.connect(self.accept)

    def _selecionar_escritorio_inicial(self, empresa_id: int | None) -> None:
        if empresa_id is not None:
            self._selecionar_por_id(self._combo_empresa, empresa_id)
        self._empresa_alterada()

    def _empresa_alterada(self) -> None:
        empresa_id = self._combo_empresa.currentData()
        if empresa_id is not None:
            escritorio_id = self._mapa_empresa_escritorio.get(empresa_id)
            self._selecionar_por_id(self._combo_escritorio, escritorio_id)
        else:
            self._combo_escritorio.setCurrentIndex(0)

    def _salvar(self) -> None:
        escritorio_id = self._combo_escritorio.currentData()
        empresa_id = self._combo_empresa.currentData()
        categoria = self._combo_categoria.currentText()
        numero_documento = self._campo_numero_documento.text().strip() or None
        codigo_barras = self._campo_codigo_barras.text().strip() or None
        descricao = self._campo_descricao.text().strip()
        tipo = self._combo_tipo.currentText()
        valor_texto = self._campo_valor.text().strip().replace(",", ".")
        data_emissao = cast(date, self._date_emissao.date().toPython())
        data_vencimento = cast(date, self._date_vencimento.date().toPython())
        observacao = self._campo_observacao.toPlainText().strip() or None

        if empresa_id is None:
            QMessageBox.warning(
                self, "Campo obrigatorio", "Selecione uma empresa."
            )
            return
        if escritorio_id is None or escritorio_id <= 0:
            QMessageBox.warning(
                self, "Campo obrigatorio", "Empresa sem escritorio vinculado."
            )
            return
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
                    plano_conta_id=self._plano_conta_id,
                    centro_custo_id=None,
                    numero_documento=numero_documento,
                    codigo_barras=codigo_barras,
                    categoria=categoria,
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
                replicar = self._check_replicar.isChecked()
                vezes = self._spin_vezes.value() if replicar else 1

                for i in range(vezes):
                    venc = data_vencimento + relativedelta(months=i)
                    desc = descricao
                    if vezes > 1:
                        seq = f" ({i + 1:02d}/{vezes:02d})"
                        desc = f"{descricao}{seq}"

                    dto_criar = CadastrarTituloDTO(
                        escritorio_id=escritorio_id,
                        empresa_id=empresa_id,
                        plano_conta_id=self._plano_conta_id,
                        centro_custo_id=None,
                        numero_documento=numero_documento,
                        codigo_barras=codigo_barras,
                        categoria=categoria,
                        descricao=desc,
                        tipo=tipo,
                        valor=valor,
                        data_emissao=data_emissao,
                        data_vencimento=venc,
                        observacao=observacao,
                    )
                    self._criar.execute(dto_criar)

                if vezes > 1:
                    QMessageBox.information(
                        self,
                        "Sucesso",
                        f"{vezes} titulos criados com sucesso.",
                    )
                else:
                    QMessageBox.information(
                        self, "Sucesso", "Titulo criado com sucesso."
                    )
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Erro", str(e))
