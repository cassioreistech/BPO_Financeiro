"""Port (interface) para persistencia de Contador."""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.contador import Contador


class ContadorRepository(ABC):
    """Interface abstrata para repositorio de contadores."""

    @abstractmethod
    def create(self, contador: Contador) -> Contador:
        """Cria um novo contador."""

    @abstractmethod
    def get_by_id(self, id: int) -> Contador | None:
        """Busca contador por ID."""

    @abstractmethod
    def update(self, contador: Contador) -> Contador:
        """Atualiza um contador existente."""

    @abstractmethod
    def delete(self, id: int) -> None:
        """Remove um contador por ID."""

    @abstractmethod
    def list_all(
        self, escritorio_id: int | None = None, skip: int = 0, limit: int = 100
    ) -> list[Contador]:
        """Lista contadores com paginacao."""
