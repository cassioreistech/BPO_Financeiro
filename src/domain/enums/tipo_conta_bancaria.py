"""Enum de tipo de conta bancaria."""

from enum import StrEnum


class TipoContaBancaria(StrEnum):
    """Tipo de conta bancaria da empresa."""

    CORRENTE = "CORRENTE"
    POUPANCA = "POUPANCA"
    OUTRO = "OUTRO"
