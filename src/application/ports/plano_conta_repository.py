"""Port (interface) para persistencia de PlanoConta."""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.plano_conta import PlanoConta


class PlanoContaRepository(ABC):
    """Interface abstrata para repositorio de plano de contas."""

    @abstractmethod
    def create(self, plano: PlanoConta) -> PlanoConta:
        """Cria uma nova conta no plano."""

    @abstractmethod
    def get_by_id(self, id: int) -> PlanoConta | None:
        """Busca conta por ID."""

    @abstractmethod
    def update(self, plano: PlanoConta) -> PlanoConta:
        """Atualiza uma conta existente."""

    @abstractmethod
    def delete(self, id: int) -> None:
        """Remove uma conta por ID."""

    @abstractmethod
    def list_by_escritorio(
        self, escritorio_id: int, skip: int = 0, limit: int = 100
    ) -> list[PlanoConta]:
        """Lista contas de um escritorio."""

    @abstractmethod
    def get_by_codigo(
        self, escritorio_id: int, codigo: str
    ) -> PlanoConta | None:
        """Busca conta por codigo dentro de um escritorio."""
