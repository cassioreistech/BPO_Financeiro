"""Enum de regime tributario da empresa."""

from enum import StrEnum


class RegimeTributario(StrEnum):
    """Regime tributario ao qual a empresa esta submetida."""

    SIMPLES = "SIMPLES"
    LUCRO_PRESUMIDO = "LUCRO_PRESUMIDO"
    LUCRO_REAL = "LUCRO_REAL"
    MEI = "MEI"
