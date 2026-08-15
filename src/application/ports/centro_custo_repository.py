"""Port (interface) para persistencia de CentroCusto."""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.centro_custo import CentroCusto


class CentroCustoRepository(ABC):
    """Interface abstrata para repositorio de centros de custo."""

    @abstractmethod
    def create(self, centro: CentroCusto) -> CentroCusto:
        """Cria um novo centro de custo."""

    @abstractmethod
    def get_by_id(self, id: int) -> CentroCusto | None:
        """Busca centro de custo por ID."""

    @abstractmethod
    def update(self, centro: CentroCusto) -> CentroCusto:
        """Atualiza um centro de custo existente."""

    @abstractmethod
    def delete(self, id: int) -> None:
        """Remove um centro de custo por ID."""

    @abstractmethod
    def list_by_empresa(
        self,
        empresa_id: int,
        ativo: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CentroCusto]:
        """Lista centros de custo de uma empresa."""

    @abstractmethod
    def get_by_codigo(
        self, empresa_id: int, codigo: str
    ) -> CentroCusto | None:
        """Busca centro de custo por codigo dentro de uma empresa."""
