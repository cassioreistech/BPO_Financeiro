"""Port (interface) para persistencia de Escritorio."""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.escritorio import Escritorio


class EscritorioRepository(ABC):
    """Interface abstrata para repositorio de escritorios.

    Implementacoes concretas serao criadas na camada de infraestrutura.
    """

    @abstractmethod
    def create(self, escritorio: Escritorio) -> Escritorio:
        """Cria um novo escritorio."""

    @abstractmethod
    def get_by_id(self, id: int) -> Escritorio | None:
        """Busca escritorio por ID."""

    @abstractmethod
    def get_by_cnpj(self, cnpj: str) -> Escritorio | None:
        """Busca escritorio por CNPJ/CPF (somente digitos)."""

    @abstractmethod
    def update(self, escritorio: Escritorio) -> Escritorio:
        """Atualiza um escritorio existente."""

    @abstractmethod
    def delete(self, id: int) -> None:
        """Remove um escritorio por ID."""

    @abstractmethod
    def list_all(self, skip: int = 0, limit: int = 100) -> list[Escritorio]:
        """Lista escritorios com paginacao."""
