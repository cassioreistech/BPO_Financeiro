"""Port (interface) para persistencia de ContaBancaria."""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.conta_bancaria import ContaBancaria


class ContaBancariaRepository(ABC):
    """Interface abstrata para repositorio de contas bancarias."""

    @abstractmethod
    def create(self, conta: ContaBancaria) -> ContaBancaria:
        """Cria uma nova conta bancaria."""

    @abstractmethod
    def get_by_id(self, id: int) -> ContaBancaria | None:
        """Busca conta bancaria por ID."""

    @abstractmethod
    def update(self, conta: ContaBancaria) -> ContaBancaria:
        """Atualiza uma conta bancaria existente."""

    @abstractmethod
    def delete(self, id: int) -> None:
        """Remove uma conta bancaria por ID."""

    @abstractmethod
    def list_all(
        self, empresa_id: int | None = None, skip: int = 0, limit: int = 100
    ) -> list[ContaBancaria]:
        """Lista contas bancarias com paginacao."""
