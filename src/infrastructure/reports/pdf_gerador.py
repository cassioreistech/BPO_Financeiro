"""Gerador de relatorios em PDF para titulos financeiros.

Relatorio de Titulos usa ReportLab (via PDFReportGenerator).
Fluxo de Caixa e Projecao Financeira usam fpdf.
"""

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
from infrastructure.reports.pdf_report_generator import PDFReportGenerator, _formatar_moeda


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
    return _formatar_moeda(valor)


def gerar_relatorio_titulos(
    dados: RelatorioTitulosDTO,
    caminho: Path,
    titulo_relatorio: str = "Relatorio de Titulos",
    data_inicio: date | None = None,
    data_fim: date | None = None,
    empresa_nome: str | None = None,
    empresa_cnpj: str | None = None,
    escritorio_nome: str | None = None,
    escritorio_cnpj: str | None = None,
) -> Path:
    """Gera PDF profissional com a listagem de titulos e totais.

    Usa ReportLab via PDFReportGenerator para layout profissional
    com design tokens, tabelas zebradas e cabecalho com info grid.

    Args:
        dados: Dados do relatorio.
        caminho: Caminho onde o PDF sera salvo.
        titulo_relatorio: Titulo exibido no PDF.
        data_inicio: Data inicial do filtro.
        data_fim: Data final do filtro.
        empresa_nome: Nome fantasia ou razao social da empresa.
        empresa_cnpj: CNPJ da empresa.
        escritorio_nome: Nome do escritorio.
        escritorio_cnpj: CNPJ/CPF do escritorio.

    Returns:
        Caminho do PDF gerado.
    """
    # Subtitulo com periodo
    subtitulo = "Sistema BPO Financeiro"
    if data_inicio and data_fim:
        subtitulo = f"Periodo: {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"

    # Info grid do cabecalho
    info_grid: list[list[str]] = []
    if empresa_nome:
        info_grid.append(["Empresa", empresa_nome])
    if empresa_cnpj:
        info_grid.append(["CNPJ", empresa_cnpj])
    if escritorio_nome:
        info_grid.append(["Escritorio", escritorio_nome])
    if escritorio_cnpj:
        info_grid.append(["Doc. Escritorio", escritorio_cnpj])
    if data_inicio and data_fim:
        periodo = f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
        info_grid.append(["Periodo", periodo])

    # Tabela de resumo financeiro
    resumo_dados = [
        [
            _formatar_moeda(dados.total_receber),
            _formatar_moeda(dados.total_pagar),
            _formatar_moeda(dados.total_recebido),
            _formatar_moeda(dados.total_pago),
        ]
    ]

    # Tabela de titulos
    titulos_linhas: list[list[str]] = []
    for t in dados.titulos:
        venc = t.data_vencimento.strftime("%d/%m/%Y")
        descricao = t.descricao[:50]
        categoria = t.categoria.value if hasattr(t.categoria, "value") else str(t.categoria)
        tipo = t.tipo.value if hasattr(t.tipo, "value") else str(t.tipo)
        status = t.status.value if hasattr(t.status, "value") else str(t.status)
        valor = _formatar_moeda(t.valor)
        valor_pago = _formatar_moeda(t.valor_pago) if t.valor_pago is not None else "--"
        titulos_linhas.append([venc, descricao, categoria, tipo, status, valor, valor_pago])

    # Montar dados para o gerador
    dados_relatorio = {
        "info_grid": info_grid,
        "tabelas": [
            {
                "titulo": "RESUMO FINANCEIRO",
                "colunas": ["A Receber", "A Pagar", "Recebido", "Pago"],
                "dados": resumo_dados,
                "larguras": [0.25, 0.25, 0.25, 0.25],
                "titulo_centralizado": True,
                "coluna_colorida": None,
            },
            {
                "titulo": "TITULOS",
                "colunas": [
                    "Venc.", "Descricao", "Categoria",
                    "Tipo", "Status", "Valor", "Valor Pago",
                ],
                "dados": titulos_linhas,
                "larguras": [0.12, 0.30, 0.13, 0.10, 0.10, 0.13, 0.12],
                "titulo_centralizado": True,
                "coluna_colorida": 5,
            },
        ],
    }

    # Gerar PDF
    generator = PDFReportGenerator()
    generator.generate(
        titulo=titulo_relatorio.upper(),
        subtitulo=subtitulo,
        dados=dados_relatorio,
        output_dir=caminho.parent,
        filename=caminho.name,
    )

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
