"""Enum de tipo de título financeiro."""

from __future__ import annotations

from enum import StrEnum


class TipoTitulo(StrEnum):
    """Tipo do título financeiro."""

    PAGAR = "PAGAR"
    RECEBER = "RECEBER"
