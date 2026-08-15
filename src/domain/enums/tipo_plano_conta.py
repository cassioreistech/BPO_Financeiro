"""Enum de tipo de plano de conta."""

from enum import StrEnum


class TipoPlanoConta(StrEnum):
    """Tipo da conta no plano de contas."""

    RECEITA = "RECEITA"
    DESPESA = "DESPESA"
    OUTRO = "OUTRO"
