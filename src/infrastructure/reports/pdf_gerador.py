"""Gerador de relatorios em PDF para titulos financeiros."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from fpdf import FPDF

from application.use_cases.relatorio_titulos_use_cases import (
    ItemFluxoCaixaDTO,
    ProjecaoFinanceiraDTO,
    RelatorioTitulosDTO,
)


class _PDF(FPDF):
    """PDF customizado com cabecalho e rodape."""

    def header(self) -> None:
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Sistema BPO Financeiro", align="L", ln=True)
        self.ln(2)

    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}", align="C")


def _formatar_valor(valor: Decimal) -> str:
    return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def gerar_relatorio_titulos(
    dados: RelatorioTitulosDTO,
    caminho: Path,
    titulo_relatorio: str = "Relatorio de Titulos",
    data_inicio: date | None = None,
    data_fim: date | None = None,
) -> Path:
    """Gera PDF com a listagem de titulos e totais.

    Args:
        dados: Dados do relatorio.
        caminho: Caminho onde o PDF sera salvo.
        titulo_relatorio: Titulo exibido no PDF.
        data_inicio: Data inicial do filtro.
        data_fim: Data final do filtro.

    Returns:
        Caminho do PDF gerado.
    """
    pdf = _PDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, titulo_relatorio, align="C", ln=True)
    pdf.set_font("Arial", "", 10)

    if data_inicio and data_fim:
        pdf.cell(
            0,
            8,
            f"Periodo: {data_inicio.strftime('%d/%m/%Y')} a "
            f"{data_fim.strftime('%d/%m/%Y')}",
            align="C",
            ln=True,
        )
    pdf.ln(5)

    # Totais
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Resumo", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Total a receber: {_formatar_valor(dados.total_receber)}", ln=True)
    pdf.cell(0, 6, f"Total a pagar: {_formatar_valor(dados.total_pagar)}", ln=True)
    pdf.cell(0, 6, f"Total recebido: {_formatar_valor(dados.total_recebido)}", ln=True)
    pdf.cell(0, 6, f"Total pago: {_formatar_valor(dados.total_pago)}", ln=True)
    pdf.ln(5)

    # Tabela
    pdf.set_font("Arial", "B", 9)
    colunas = ["Venc.", "Descricao", "Tipo", "Status", "Valor", "Valor Pago"]
    larguras = [22, 75, 22, 22, 28, 28]
    for col, lar in zip(colunas, larguras, strict=True):
        pdf.cell(lar, 8, col, border=1, align="C")
    pdf.ln()

    pdf.set_font("Arial", "", 8)
    for t in dados.titulos:
        valor = _formatar_valor(t.valor)
        valor_pago = (
            _formatar_valor(t.valor_pago)
            if t.valor_pago is not None
            else "—"
        )
        venc = t.data_vencimento.strftime("%d/%m/%Y")
        descricao = t.descricao[:40]
        pdf.cell(22, 6, venc, border=1, align="C")
        pdf.cell(75, 6, descricao, border=1)
        pdf.cell(22, 6, t.tipo, border=1, align="C")
        pdf.cell(22, 6, t.status, border=1, align="C")
        pdf.cell(28, 6, valor, border=1, align="R")
        pdf.cell(28, 6, valor_pago, border=1, align="R")
        pdf.ln()

    caminho.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(caminho))
    return caminho


def gerar_fluxo_caixa(
    itens: list[ItemFluxoCaixaDTO],
    caminho: Path,
    data_inicio: date,
    data_fim: date,
) -> Path:
    """Gera PDF com o fluxo de caixa do periodo.

    Args:
        itens: Lista de itens de fluxo de caixa.
        caminho: Caminho onde o PDF sera salvo.
        data_inicio: Data inicial do periodo.
        data_fim: Data final do periodo.

    Returns:
        Caminho do PDF gerado.
    """
    pdf = _PDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Fluxo de Caixa", align="C", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(
        0,
        8,
        f"Periodo: {data_inicio.strftime('%d/%m/%Y')} a "
        f"{data_fim.strftime('%d/%m/%Y')}",
        align="C",
        ln=True,
    )
    pdf.ln(5)

    pdf.set_font("Arial", "B", 9)
    colunas = ["Data", "Entradas", "Saidas", "Saldo do Dia"]
    larguras = [35, 45, 45, 45]
    for col, lar in zip(colunas, larguras, strict=True):
        pdf.cell(lar, 8, col, border=1, align="C")
    pdf.ln()

    pdf.set_font("Arial", "", 9)
    for item in itens:
        pdf.cell(35, 6, item.data.strftime("%d/%m/%Y"), border=1, align="C")
        pdf.cell(45, 6, _formatar_valor(item.entradas), border=1, align="R")
        pdf.cell(45, 6, _formatar_valor(item.saidas), border=1, align="R")
        pdf.cell(45, 6, _formatar_valor(item.saldo_dia), border=1, align="R")
        pdf.ln()

    caminho.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(caminho))
    return caminho


def gerar_projecao_financeira(
    itens: list[ProjecaoFinanceiraDTO],
    caminho: Path,
    data_inicio: date,
    data_fim: date,
    saldo_inicial: Decimal = Decimal("0"),
) -> Path:
    """Gera PDF com a projecao financeira do periodo.

    Args:
        itens: Lista de projecoes diarias.
        caminho: Caminho onde o PDF sera salvo.
        data_inicio: Data inicial do periodo.
        data_fim: Data final do periodo.
        saldo_inicial: Saldo inicial informado.

    Returns:
        Caminho do PDF gerado.
    """
    pdf = _PDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Projecao Financeira", align="C", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(
        0,
        8,
        f"Periodo: {data_inicio.strftime('%d/%m/%Y')} a "
        f"{data_fim.strftime('%d/%m/%Y')}",
        align="C",
        ln=True,
    )
    pdf.cell(
        0,
        6,
        f"Saldo inicial: {_formatar_valor(saldo_inicial)}",
        align="C",
        ln=True,
    )
    pdf.ln(5)

    pdf.set_font("Arial", "B", 9)
    colunas = ["Data", "Saldo Acumulado"]
    larguras = [50, 60]
    for col, lar in zip(colunas, larguras, strict=True):
        pdf.cell(lar, 8, col, border=1, align="C")
    pdf.ln()

    pdf.set_font("Arial", "", 9)
    for item in itens:
        pdf.cell(50, 6, item.data.strftime("%d/%m/%Y"), border=1, align="C")
        pdf.cell(60, 6, _formatar_valor(item.saldo_acumulado), border=1, align="R")
        pdf.ln()

    caminho.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(caminho))
    return caminho
