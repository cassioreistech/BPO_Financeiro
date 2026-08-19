"""Utilitarios para formatacao e limpeza de CNPJ, CPF e outros campos."""

from __future__ import annotations

import re


def limpar_documento(texto: str) -> str:
    """Remove caracteres nao alfanumericos de um documento.

    Aceita letras e numeros para preparar para CNPJ alfanumerico.
    """
    return re.sub(r"[^A-Za-z0-9]", "", texto).upper()


def formatar_cnpj(texto: str) -> str:
    """Formata CNPJ (alfanumerico) no padrao XX.XXX.XXX/XXXX-XX.

    Aceita entrada com pontuacao e remove automaticamente.
    Limite de 14 caracteres alfanumericos.
    """
    digitos = limpar_documento(texto)
    if len(digitos) > 14:
        digitos = digitos[:14]

    tamanho = len(digitos)
    if tamanho <= 2:
        return digitos
    if tamanho <= 5:
        return f"{digitos[:2]}.{digitos[2:]}"
    if tamanho <= 8:
        return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:]}"
    if tamanho <= 12:
        return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:8]}/{digitos[8:]}"
    return f"{digitos[:2]}.{digitos[2:5]}.{digitos[5:8]}/{digitos[8:12]}-{digitos[12:]}"


def formatar_cpf(texto: str) -> str:
    """Formata CPF no padrao XXX.XXX.XXX-XX.

    Aceita entrada com pontuacao e remove automaticamente.
    Limite de 11 digitos.
    """
    digitos = re.sub(r"\D", "", texto)
    if len(digitos) > 11:
        digitos = digitos[:11]

    tamanho = len(digitos)
    if tamanho <= 3:
        return digitos
    if tamanho <= 6:
        return f"{digitos[:3]}.{digitos[3:]}"
    if tamanho <= 9:
        return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:]}"
    return f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"


def formatar_cnpj_cpf(texto: str) -> str:
    """Formata automaticamente como CPF (ate 11 digitos) ou CNPJ (12-14 alfanumericos)."""
    digitos = limpar_documento(texto)
    if len(digitos) <= 11:
        # CPF: apenas digitos
        apenas_digitos = re.sub(r"\D", "", texto)
        return formatar_cpf(apenas_digitos)
    return formatar_cnpj(digitos)


def formatar_telefone(texto: str) -> str:
    """Formata telefone no padrao (XX) XXXXX-XXXX ou (XX) XXXX-XXXX."""
    digitos = re.sub(r"\D", "", texto)
    if len(digitos) > 11:
        digitos = digitos[:11]

    tamanho = len(digitos)
    if tamanho <= 2:
        return f"({digitos}" if digitos else ""
    if tamanho <= 6:
        return f"({digitos[:2]}) {digitos[2:]}"
    if tamanho <= 10:
        return f"({digitos[:2]}) {digitos[2:6]}-{digitos[6:]}"
    return f"({digitos[:2]}) {digitos[2:7]}-{digitos[7:]}"


def formatar_cep(texto: str) -> str:
    """Formata CEP no padrao XXXXX-XXX."""
    digitos = re.sub(r"\D", "", texto)
    if len(digitos) > 8:
        digitos = digitos[:8]

    if len(digitos) <= 5:
        return digitos
    return f"{digitos[:5]}-{digitos[5:]}"


def aplicar_formatacao_campo(campo, funcao_formatar, texto: str) -> None:
    """Aplica formatacao em um QLineEdit preservando a posicao do cursor.

    Args:
        campo: QLineEdit a ser atualizado.
        funcao_formatar: funcao que recebe texto e retorna texto formatado.
        texto: texto atual do campo.
    """
    posicao = campo.cursorPosition()
    texto_anterior = campo.text()
    formatado = funcao_formatar(texto)

    campo.blockSignals(True)
    campo.setText(formatado)

    # Ajustar posicao do cursor
    if len(formatado) >= len(texto_anterior):
        nova_pos = posicao + (len(formatado) - len(texto_anterior))
    else:
        nova_pos = max(0, posicao - (len(texto_anterior) - len(formatado)))
    campo.setCursorPosition(min(nova_pos, len(formatado)))
    campo.blockSignals(False)
