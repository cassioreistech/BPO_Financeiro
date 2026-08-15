"""Enum de status da empresa."""

from enum import StrEnum


class StatusEmpresa(StrEnum):
    """Status operacional da empresa no sistema."""

    ATIVA = "ATIVA"
    INATIVA = "INATIVA"
