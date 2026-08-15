"""Dialogo para geracao de relatorios de titulos."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import cast

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from application.use_cases.relatorio_titulos_use_cases import (
    FluxoCaixaUseCase,
    ProjecaoFinanceiraUseCase,
    RelatorioTitulosUseCase,
)
from infrastructure.reports.pdf_gerador import (
    gerar_fluxo_caixa,
    gerar_projecao_financeira,
    gerar_relatorio_titulos,
)


class RelatorioDialog(QDialog):
    """Dialogo para escolher periodo e tipo de relatorio."""

    TIPOS = ["Relatorio de Titulos", "Fluxo de Caixa", "Projecao Financeira"]

    def __init__(
        self,
        relatorio_use_case: RelatorioTitulosUseCase,
        fluxo_caixa_use_case: FluxoCaixaUseCase,
        projecao_use_case: ProjecaoFinanceiraUseCase,
        escritorio_id: int,
        empresa_id: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._relatorio_uc = relatorio_use_case
        self._fluxo_uc = fluxo_caixa_use_case
        self._projecao_uc = projecao_use_case
        self._escritorio_id = escritorio_id
        self._empresa_id = empresa_id
        self._caminho: Path | None = None
        self._configurar_janela()
        self._montar_formulario()

    def _configurar_janela(self) -> None:
        self.setWindowTitle("Gerar Relatorio")
        self.setMinimumWidth(420)
        self.setModal(True)

    def _montar_formulario(self) -> None:
        layout = QVBoxLayout(self)

        titulo = QLabel("Gerar Relatorio")
        titulo.setObjectName("formTitulo")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.setSpacing(12)

        self._combo_tipo = QComboBox()
        self._combo_tipo.addItems(self.TIPOS)
        self._combo_tipo.currentIndexChanged.connect(self._tipo_alterado)
        form.addRow("Tipo:*", self._combo_tipo)

        self._date_inicio = QDateEdit()
        self._date_inicio.setCalendarPopup(True)
        hoje = date.today()
        primeiro_dia = date(hoje.year, hoje.month, 1)
        self._date_inicio.setDate(QDate(primeiro_dia.year, primeiro_dia.month, primeiro_dia.day))
        form.addRow("Data Inicio:*", self._date_inicio)

        self._date_fim = QDateEdit()
        self._date_fim.setCalendarPopup(True)
        self._date_fim.setDate(QDate(hoje.year, hoje.month, hoje.day))
        form.addRow("Data Fim:*", self._date_fim)

        self._campo_saldo_inicial = QLineEdit()
        self._campo_saldo_inicial.setPlaceholderText("0,00")
        self._campo_saldo_inicial.setEnabled(False)
        form.addRow("Saldo Inicial:", self._campo_saldo_inicial)

        layout.addLayout(form)

        botoes = QHBoxLayout()
        botoes.addStretch()

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setObjectName("btnCancelar")
        btn_cancelar.clicked.connect(self.reject)
        botoes.addWidget(btn_cancelar)

        btn_gerar = QPushButton("Gerar PDF")
        btn_gerar.setObjectName("btnSalvar")
        btn_gerar.setDefault(True)
        btn_gerar.clicked.connect(self._gerar)
        botoes.addWidget(btn_gerar)

        layout.addLayout(botoes)

    def _tipo_alterado(self) -> None:
        eh_projecao = self._combo_tipo.currentText() == "Projecao Financeira"
        self._campo_saldo_inicial.setEnabled(eh_projecao)

    @staticmethod
    def _to_qdate(data: date) -> QDate:
        return QDate(data.year, data.month, data.day)

    @staticmethod
    def _formatar_valor(valor: Decimal) -> str:
        return f"{valor:.2f}".replace(".", ",")

    def _parse_saldo_inicial(self) -> Decimal:
        texto = self._campo_saldo_inicial.text().strip().replace(",", ".")
        if not texto:
            return Decimal("0")
        return Decimal(texto)

    def _gerar(self) -> None:
        data_inicio = cast(date, self._date_inicio.date().toPython())
        data_fim = cast(date, self._date_fim.date().toPython())

        if data_fim < data_inicio:
            QMessageBox.warning(
                self, "Data invalida", "Data final nao pode ser anterior a inicial."
            )
            return

        tipo = self._combo_tipo.currentText()
        sufixo = tipo.lower().replace(" ", "_")
        nome_padrao = f"relatorio_{sufixo}_{data_inicio.strftime('%Y%m%d')}.pdf"
        caminho_str, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar relatorio",
            str(Path.home() / "Downloads" / nome_padrao),
            "PDF (*.pdf)",
        )
        if not caminho_str:
            return

        caminho = Path(caminho_str)
        try:
            if tipo == "Relatorio de Titulos":
                dados = self._relatorio_uc.execute(
                    escritorio_id=self._escritorio_id,
                    empresa_id=self._empresa_id,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                )
                gerar_relatorio_titulos(
                    dados=dados,
                    caminho=caminho,
                    titulo_relatorio=tipo,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                )
            elif tipo == "Fluxo de Caixa":
                itens = self._fluxo_uc.execute(
                    escritorio_id=self._escritorio_id,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    empresa_id=self._empresa_id,
                )
                gerar_fluxo_caixa(
                    itens=itens,
                    caminho=caminho,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                )
            else:
                saldo_inicial = self._parse_saldo_inicial()
                itens_projecao = self._projecao_uc.execute(
                    escritorio_id=self._escritorio_id,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    saldo_inicial=saldo_inicial,
                    empresa_id=self._empresa_id,
                )
                gerar_projecao_financeira(
                    itens=itens_projecao,
                    caminho=caminho,
                    data_inicio=data_inicio,
                    data_fim=data_fim,
                    saldo_inicial=saldo_inicial,
                )

            self._caminho = caminho
            QMessageBox.information(
                self,
                "Sucesso",
                f"Relatorio salvo em:\n{caminho}",
            )
            self.accept()
        except (ValueError, InvalidOperation) as e:
            QMessageBox.warning(self, "Erro", str(e))

    def caminho_gerado(self) -> Path | None:
        """Retorna o caminho do PDF gerado, se houver."""
        return self._caminho
