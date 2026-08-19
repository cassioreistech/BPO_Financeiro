"""Gerador de relatorios PDF profissionais com ReportLab.

Baseado no template pdf_generator_template.py com design tokens,
fontes Arial, tabelas zebradas, cabecalho com info grid e rodape.
"""

from __future__ import annotations

import os
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ============================================
# DESIGN TOKENS
# ============================================

CORES: dict[str, Any] = {
    "primaria": colors.HexColor("#1B2A4A"),
    "secundaria": colors.HexColor("#6B7280"),
    "sucesso": colors.HexColor("#16A34A"),
    "perigo": colors.HexColor("#DC2626"),
    "fundo_claro": colors.HexColor("#F9FAFB"),
    "borda": colors.HexColor("#E5E7EB"),
    "texto_escuro": colors.HexColor("#000000"),
    "texto_cinza": colors.HexColor("#6B7280"),
    "branco": colors.white,
    "azul_1": colors.HexColor("#2563EB"),
    "azul_2": colors.HexColor("#3B82F6"),
    "vermelho": colors.HexColor("#DC2626"),
    "verde": colors.HexColor("#16A34A"),
}

FONTES: dict[str, int | float] = {
    "tamanho_titulo": 20,
    "tamanho_subtitulo": 16,
    "tamanho_secao": 12,
    "tamanho_texto": 9,
    "tamanho_tabela": 8.5,
    "tamanho_rodape": 8,
}

ESPACAMENTO: dict[str, int] = {
    "secao_antes": 12,
    "secao_depois": 6,
    "tabela_antes": 8,
    "tabela_depois": 8,
}

MARGENS: dict[str, float] = {
    "esquerda": 1.5 * cm,
    "direita": 1.5 * cm,
    "cima": 1.5 * cm,
    "baixo": 1.8 * cm,
}

LARGURA_UTIL: float = A4[0] - MARGENS["esquerda"] - MARGENS["direita"]


# ============================================
# CANVAS CUSTOMIZADO
# ============================================


class SimpleCanvas(Canvas):
    """Canvas com rodape (linha divisoria + numero de pagina)."""

    def showPage(self) -> None:
        self._draw_footer()
        super().showPage()

    def _draw_footer(self) -> None:
        """Desenha linha do rodape e numero da pagina."""
        self.saveState()
        self.setStrokeColor(CORES["borda"])
        self.setLineWidth(0.5)
        self.line(
            MARGENS["esquerda"],
            1.2 * cm,
            A4[0] - MARGENS["direita"],
            1.2 * cm,
        )
        self.setFont("Helvetica", FONTES["tamanho_rodape"])  # type: ignore[arg-type]
        self.setFillColor(CORES["texto_cinza"])
        self.drawCentredString(
            A4[0] / 2,
            0.7 * cm,
            f"Pagina {self._pageNumber}",
        )
        self.restoreState()


# ============================================
# UTILITARIOS
# ============================================


def registrar_fontes() -> tuple[str, str]:
    """Registra fontes TrueType. Retorna (fonte_normal, fonte_bold).

    Tenta Arial, Verdana, DejaVu. Fallback para Helvetica.
    """
    caminhos_fontes = [
        ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
        ("C:/Windows/Fonts/verdana.ttf", "C:/Windows/Fonts/verdanab.ttf"),
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ),
    ]

    for caminho_normal, caminho_bold in caminhos_fontes:
        if os.path.exists(caminho_normal):
            try:
                pdfmetrics.registerFont(TTFont("FonteNormal", caminho_normal))
                if os.path.exists(caminho_bold):
                    pdfmetrics.registerFont(TTFont("FonteBold", caminho_bold))
                else:
                    pdfmetrics.registerFont(TTFont("FonteBold", caminho_normal))
                return "FonteNormal", "FonteBold"
            except Exception:
                continue

    return "Helvetica", "Helvetica-Bold"


def criar_estilos(fonte_normal: str, fonte_bold: str) -> dict[str, ParagraphStyle]:
    """Cria estilos de paragrafo para o relatorio."""
    base = getSampleStyleSheet()

    return {
        "Titulo": ParagraphStyle(
            name="Titulo",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=FONTES["tamanho_titulo"],  # type: ignore[arg-type]
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "Subtitulo": ParagraphStyle(
            name="Subtitulo",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=FONTES["tamanho_subtitulo"],  # type: ignore[arg-type]
            alignment=TA_CENTER,
            spaceAfter=10,
            textColor=CORES["primaria"],
        ),
        "Emissao": ParagraphStyle(
            name="Emissao",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=8,
            spaceBefore=4,
            textColor=CORES["texto_cinza"],
        ),
        "Secao": ParagraphStyle(
            name="Secao",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=FONTES["tamanho_secao"],  # type: ignore[arg-type]
            spaceBefore=ESPACAMENTO["secao_antes"],
            spaceAfter=ESPACAMENTO["secao_depois"],
            textColor=CORES["primaria"],
        ),
        "SecaoCentralizada": ParagraphStyle(
            name="SecaoCentralizada",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=FONTES["tamanho_secao"],  # type: ignore[arg-type]
            alignment=TA_CENTER,
            spaceBefore=ESPACAMENTO["secao_antes"],
            spaceAfter=ESPACAMENTO["secao_depois"],
            textColor=CORES["primaria"],
        ),
        "Texto": ParagraphStyle(
            name="Texto",
            parent=base["Normal"],
            fontName=fonte_normal,
            fontSize=FONTES["tamanho_texto"],  # type: ignore[arg-type]
        ),
        "TabelaCabecalho": ParagraphStyle(
            name="TabelaCabecalho",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=FONTES["tamanho_tabela"],  # type: ignore[arg-type]
            textColor=CORES["branco"],
            alignment=TA_CENTER,
        ),
        "TabelaTexto": ParagraphStyle(
            name="TabelaTexto",
            parent=base["Normal"],
            fontName=fonte_normal,
            fontSize=FONTES["tamanho_tabela"],  # type: ignore[arg-type]
        ),
        "TabelaTextoDireita": ParagraphStyle(
            name="TabelaTextoDireita",
            parent=base["Normal"],
            fontName=fonte_normal,
            fontSize=FONTES["tamanho_tabela"],  # type: ignore[arg-type]
            alignment=TA_RIGHT,
        ),
        "TabelaValorColorido": ParagraphStyle(
            name="TabelaValorColorido",
            parent=base["Normal"],
            fontName=fonte_bold,
            fontSize=11,
            textColor=CORES["azul_1"],
            alignment=TA_CENTER,
        ),
    }


def _texto(valor: object, padrao: str = "") -> str:
    """Retorna string segura, tratando None."""
    return padrao if valor is None else str(valor)


def _formatar_data(valor: object) -> str:
    """Formata data para dd/mm/aaaa."""
    if not valor:
        return ""
    if hasattr(valor, "strftime"):
        return valor.strftime("%d/%m/%Y")
    return str(valor)


def _formatar_moeda(valor: Decimal | float | None) -> str:
    """Formata valor monetario para R$ 1.234,56."""
    if valor is None:
        valor = 0.0
    fmt = f"{float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {fmt}"


# ============================================
# COMPONENTES DE LAYOUT
# ============================================


def build_cabecalho(
    titulo: str,
    subtitulo: str,
    data_emissao: str | None = None,
    info_grid: list[list[str]] | None = None,
    estilos: dict[str, ParagraphStyle] | None = None,
    fonte_bold: str | None = None,
    base: Any = None,
) -> list:
    """Construi cabecalho com titulo, subtitulo e informacoes.

    Args:
        titulo: Titulo principal.
        subtitulo: Subtitulo ou nome do projeto.
        data_emissao: Data de emissao (default: hoje).
        info_grid: Lista de listas com informacoes [[label, valor], ...].
        estilos: Dicionario de estilos.
        fonte_bold: Nome da fonte em negrito.
    """
    elementos: list = []

    if data_emissao is None:
        data_emissao = datetime.now().strftime("%d/%m/%Y")

    elementos.append(Paragraph(titulo, estilos["Titulo"]))
    elementos.append(Paragraph(subtitulo, estilos["Subtitulo"]))
    elementos.append(Paragraph(f"Data de emissao: {data_emissao}", estilos["Emissao"]))
    elementos.append(Spacer(1, 10))

    if info_grid:
        info_data = [
            [
                Paragraph(str(label).upper(), estilos["Texto"]),
                Paragraph(
                    str(valor).upper(),
                    ParagraphStyle(
                        name="InfoValor",
                        parent=base["Normal"],
                        fontName=fonte_bold,
                        fontSize=10,
                        textColor=CORES["primaria"],
                    ),
                ),
            ]
            for label, valor in info_grid
        ]

        info_table = Table(info_data, colWidths=[LARGURA_UTIL / 4] * 2)
        info_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, CORES["borda"]),
                    ("BACKGROUND", (0, 0), (-1, -1), CORES["fundo_claro"]),
                ]
            )
        )
        elementos.append(info_table)
        elementos.append(Spacer(1, 10))

    return elementos


def build_tabela(
    titulo: str,
    colunas: list[str],
    dados: list[list[str]],
    estilos: dict[str, ParagraphStyle],
    fonte_normal: str,
    fonte_bold: str,
    larguras_colunas: list[float] | None = None,
    cabecalho_maiusculo: bool = True,
    titulo_centralizado: bool = False,
    estilo_valor_col: int | None = None,
) -> list:
    """Construi tabela padrao com cabecalho colorido.

    Args:
        titulo: Titulo da secao.
        colunas: Lista de colunas.
        dados: Lista de linhas [[col1, col2, ...], ...].
        estilos: Dicionario de estilos.
        fonte_normal: Nome da fonte normal.
        fonte_bold: Nome da fonte bold.
        larguras_colunas: Larguras relativas (ex: [0.2, 0.5, 0.3]).
        cabecalho_maiusculo: Se True, colunas em maiusculas.
        titulo_centralizado: Se True, centraliza titulo.
        estilo_valor_col: Indice da coluna com estilo colorido.
    """
    elementos: list = []

    if titulo_centralizado:
        elementos.append(Paragraph(titulo, estilos["SecaoCentralizada"]))
    else:
        elementos.append(Paragraph(titulo, estilos["Secao"]))

    if not dados:
        return elementos

    colunas_formatadas = [c.upper() for c in colunas] if cabecalho_maiusculo else colunas
    cabecalho = [Paragraph(col, estilos["TabelaCabecalho"]) for col in colunas_formatadas]

    dados_formatados: list = []
    for linha in dados:
        linha_formatada: list = []
        for col_idx, valor in enumerate(linha):
            if estilo_valor_col is not None and col_idx == estilo_valor_col:
                linha_formatada.append(Paragraph(valor, estilos["TabelaValorColorido"]))
            else:
                linha_formatada.append(Paragraph(valor, estilos["TabelaTexto"]))
        dados_formatados.append(linha_formatada)

    tabela_dados = [cabecalho] + dados_formatados

    if larguras_colunas:
        larguras = [
            w if isinstance(w, (int, float)) and w > 1 else LARGURA_UTIL * w
            for w in larguras_colunas
        ]
    else:
        larguras = [LARGURA_UTIL / len(colunas)] * len(colunas)

    table = Table(tabela_dados, colWidths=larguras, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), CORES["primaria"]),
                ("TEXTCOLOR", (0, 0), (-1, 0), CORES["branco"]),
                ("FONTNAME", (0, 0), (-1, 0), fonte_bold),
                ("FONTSIZE", (0, 0), (-1, -1), FONTES["tamanho_tabela"]),
                ("GRID", (0, 0), (-1, -1), 0.5, CORES["borda"]),
                ("PADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ]
        )
    )

    for i in range(len(dados_formatados)):
        if (i + 1) % 2 == 0:
            table.setStyle(
                TableStyle([("BACKGROUND", (0, i + 1), (-1, i + 1), CORES["fundo_claro"])])
            )

    elementos.append(table)
    elementos.append(Spacer(1, ESPACAMENTO["tabela_depois"]))

    return elementos


def build_assinatura(
    responsavel: str,
    cargo_ou_cnpj: str | None = None,
    espacamento: int = 20,
) -> list:
    """Construi bloco de assinatura.

    Args:
        responsavel: Nome do responsavel.
        cargo_ou_cnpj: Cargo ou CNPJ.
        espacamento: Espacamento antes da assinatura (default: 20).
    """
    elementos: list = []

    if not responsavel:
        return elementos

    elementos.append(Spacer(1, espacamento))

    elementos.append(
        HRFlowable(
            width=LARGURA_UTIL * 0.5,
            thickness=1,
            color=CORES["texto_escuro"],
            spaceAfter=4,
        )
    )

    assinatura_style = ParagraphStyle(
        name="Assinatura",
        parent=getSampleStyleSheet()["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        alignment=TA_CENTER,
    )
    elementos.append(Paragraph(responsavel, assinatura_style))

    if cargo_ou_cnpj:
        cargo_style = ParagraphStyle(
            name="AssinaturaCargo",
            parent=getSampleStyleSheet()["Normal"],
            fontName="Helvetica",
            fontSize=9,
            textColor=CORES["texto_cinza"],
            alignment=TA_CENTER,
        )
        elementos.append(Paragraph(cargo_ou_cnpj, cargo_style))

    return elementos


# ============================================
# GERADOR PRINCIPAL
# ============================================


class PDFReportGenerator:
    """Gerador de relatorios PDF profissionais.

    Exemplo::

        generator = PDFReportGenerator()
        pdf_path = generator.generate(
            titulo="RELATORIO DE TITULOS",
            subtitulo="Empresa X",
            dados={
                "info_grid": [["Empresa", "X"], ["CNPJ", "00.000.000/0001-00"]],
                "tabelas": [
                    {
                        "titulo": "TITULOS",
                        "colunas": ["Venc.", "Descricao", "Valor"],
                        "dados": [["01/01/2026", "Boleto", "R$ 1.000,00"]],
                    }
                ],
            },
            output_dir=Path.home() / "Downloads",
        )
    """

    def generate(
        self,
        titulo: str,
        subtitulo: str,
        dados: dict[str, Any],
        output_dir: Path,
        filename: str | None = None,
    ) -> Path:
        """Gera relatorio PDF.

        Args:
            titulo: Titulo principal.
            subtitulo: Subtitulo.
            dados: Dados do relatorio (info_grid, tabelas, responsavel, cnpj).
            output_dir: Diretorio de saida.
            filename: Nome do arquivo (opcional).

        Returns:
            Path do PDF gerado.
        """
        output_dir.mkdir(exist_ok=True, parents=True)

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relatorio_{timestamp}.pdf"

        filepath = output_dir / filename

        fonte_normal, fonte_bold = registrar_fontes()
        base = getSampleStyleSheet()
        estilos = criar_estilos(fonte_normal, fonte_bold)

        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            leftMargin=MARGENS["esquerda"],
            rightMargin=MARGENS["direita"],
            topMargin=MARGENS["cima"],
            bottomMargin=MARGENS["baixo"],
        )

        elementos: list = []

        elementos.extend(
            build_cabecalho(
                titulo=titulo,
                subtitulo=subtitulo,
                info_grid=dados.get("info_grid"),
                estilos=estilos,
                fonte_bold=fonte_bold,
                base=base,
            )
        )

        for tabela_config in dados.get("tabelas", []):
            elementos.extend(
                build_tabela(
                    titulo=tabela_config.get("titulo", "DADOS"),
                    colunas=tabela_config.get("colunas", []),
                    dados=tabela_config.get("dados", []),
                    estilos=estilos,
                    fonte_normal=fonte_normal,
                    fonte_bold=fonte_bold,
                    larguras_colunas=tabela_config.get("larguras"),
                    cabecalho_maiusculo=tabela_config.get("maiusculo", True),
                    titulo_centralizado=tabela_config.get("titulo_centralizado", False),
                    estilo_valor_col=tabela_config.get("coluna_colorida"),
                )
            )

        if dados.get("responsavel"):
            elementos.extend(
                build_assinatura(
                    responsavel=dados["responsavel"],
                    cargo_ou_cnpj=dados.get("cnpj"),
                    espacamento=dados.get("espacamento_assinatura", 20),
                )
            )

        doc.build(elementos, canvasmaker=SimpleCanvas)

        print(f"[PDF] Gerado: {filepath}")

        return filepath
