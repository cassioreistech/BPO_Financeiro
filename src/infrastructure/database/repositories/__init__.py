"""Repositories concretos da camada de persistencia."""

from __future__ import annotations

from infrastructure.database.repositories.sqlite_empresa_repository import (
    SQLiteEmpresaRepository,
)
from infrastructure.database.repositories.sqlite_escritorio_repository import (
    SQLiteEscritorioRepository,
)

__all__ = ["SQLiteEscritorioRepository", "SQLiteEmpresaRepository"]
