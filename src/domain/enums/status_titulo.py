"""Enum de status de título financeiro."""

from __future__ import annotations

from enum import StrEnum


class StatusTitulo(StrEnum):
    """Status do título financeiro."""

    ABERTO = "ABERTO"
    PAGO = "PAGO"
    CANCELADO = "CANCELADO"
