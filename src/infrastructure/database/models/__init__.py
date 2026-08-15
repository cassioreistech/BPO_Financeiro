"""Models ORM da camada de persistencia."""

from __future__ import annotations

from infrastructure.database.models.empresa_model import EmpresaModel
from infrastructure.database.models.escritorio_model import EscritorioModel

__all__ = ["EscritorioModel", "EmpresaModel"]
