"""Situacoes de vencimento para filtros rapidos de titulos."""

from __future__ import annotations

from enum import StrEnum


class SituacaoVencimento(StrEnum):
    """Filtros rapidos por situacao de vencimento."""

    VENCIDOS = "VENCIDOS"
    HOJE = "HOJE"
    AMANHA = "AMANHA"
    PROXIMA_SEMANA = "PROXIMA_SEMANA"
