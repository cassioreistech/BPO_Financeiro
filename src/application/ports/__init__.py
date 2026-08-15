"""Ports (interfaces) da camada de aplicacao."""

from application.ports.empresa_repository import EmpresaRepository
from application.ports.escritorio_repository import EscritorioRepository

__all__ = ["EmpresaRepository", "EscritorioRepository"]
