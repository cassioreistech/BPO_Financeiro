"""Dialogo de quitacao de titulo."""

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
    QVBoxLayout,
    QWidget,
)

from application.dto.titulo_dto import TituloResponseDTO
from domain.enums.forma_pagamento import FormaPagamento


class QuitacaoDialog(QDialog):
    """Dialogo para informar dados da quitacao de um titulo."""

    FORMAS_PAGAMENTO = [f.value for f in FormaPagamento]

    def __init__(
        self,
        titulo: TituloResponseDTO,
        opcoes_conta_bancaria: list[tuple[int, str]],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._titulo = titulo
        self._opcoes_conta_bancaria = opcoes_conta_bancaria
        self._configurar_janela()
        self._montar_formulario()
        self._preencher_padrao()

    def _configurar_janela(self) -> None:
        self.setWindowTitle("Quitar Titulo")
        self.setMinimumWidth(420)
        self.setModal(True)

    def _montar_formulario(self) -> None:
        layout = QVBoxLayout(self)

        titulo = QLabel(f"Quitar: {self._titulo.descricao}")
        titulo.setObjectName("formTitulo")
        layout.addWidget(titulo)

        info = QLabel(
            f"Valor original: {self._formatar_valor(self._titulo.valor)} | "
            f"Vencimento: {self._titulo.data_vencimento.strftime('%d/%m/%Y')}"
        )
        layout.addWidget(info)

        form = QFormLayout()
        form.setSpacing(12)

        self._date_quitacao = QDateEdit()
        self._date_quitacao.setCalendarPopup(True)
        self._date_quitacao.setDate(self._to_qdate(date.today()))
        form.addRow("Data Quitacao:*", self._date_quitacao)

        self._campo_valor_pago = QLineEdit()
        self._campo_valor_pago.setPlaceholderText("0,00")
        form.addRow("Valor Pago:*", self._campo_valor_pago)

        self._combo_conta_bancaria = QComboBox()
        self._combo_conta_bancaria.addItem("Nenhuma", None)
        for cid, nome in self._opcoes_conta_bancaria:
            self._combo_conta_bancaria.addItem(nome, cid)
        form.addRow("Conta Bancaria:", self._combo_conta_bancaria)

        self._combo_forma_pagamento = QComboBox()
        self._combo_forma_pagamento.addItems(self.FORMAS_PAGAMENTO)
        form.addRow("Forma Pagamento:*", self._combo_forma_pagamento)

        layout.addLayout(form)

        botoes = QHBoxLayout()
        botoes.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btnCancelar")
        btn_cancelar.clicked.connect(self.reject)
        botoes.addWidget(btn_cancelar)

        btn_salvar = QPushButton("Quitar")
        btn_salvar.setObjectName("btnSalvar")
        btn_salvar.setDefault(True)
        btn_salvar.clicked.connect(self._confirmar)
        botoes.addWidget(btn_salvar)

        layout.addLayout(botoes)

    def _preencher_padrao(self) -> None:
        self._campo_valor_pago.setText(self._formatar_valor(self._titulo.valor))
        if self._titulo.conta_bancaria_id is not None:
            self._selecionar_por_id(
                self._combo_conta_bancaria, self._titulo.conta_bancaria_id
            )
        if self._titulo.forma_pagamento:
            idx = self._combo_forma_pagamento.findText(
                self._titulo.forma_pagamento
            )
            if idx >= 0:
                self._combo_forma_pagamento.setCurrentIndex(idx)

    @staticmethod
    def _to_qdate(data: date) -> QDate:
        return QDate(data.year, data.month, data.day)

    @staticmethod
    def _selecionar_por_id(combo: QComboBox, id_: int) -> None:
        idx = combo.findData(id_)
        if idx >= 0:
            combo.setCurrentIndex(idx)

    @staticmethod
    def _formatar_valor(valor: Decimal) -> str:
        return f"{valor:.2f}".replace(".", ",")

    def obter_dados(self) -> tuple[date, Decimal, int | None, str]:
        """Retorna os dados informados pelo usuario."""
        data_quitacao = cast(date, self._date_quitacao.date().toPython())
        valor_texto = self._campo_valor_pago.text().strip().replace(",", ".")
        valor_pago = Decimal(valor_texto)
        conta_bancaria_id = self._combo_conta_bancaria.currentData()
        forma_pagamento = self._combo_forma_pagamento.currentText()
        return data_quitacao, valor_pago, conta_bancaria_id, forma_pagamento

    def _confirmar(self) -> None:
        valor_texto = self._campo_valor_pago.text().strip().replace(",", ".")
        if not valor_texto:
            QMessageBox.warning(
                self, "Campo obrigatorio", "Informe o valor pago."
            )
            return
        try:
            Decimal(valor_texto)
        except (InvalidOperation, ValueError):
            QMessageBox.warning(
                self, "Valor invalido", "Informe um valor numerico valido."
            )
            return
        self.accept()
