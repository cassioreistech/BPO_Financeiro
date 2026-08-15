"""Port (interface) para persistencia de Titulo."""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal

from domain.entities.titulo import Titulo
from domain.enums.status_titulo import StatusTitulo
from domain.enums.tipo_titulo import TipoTitulo


class TituloRepository(ABC):
    """Interface abstrata para repositorio de titulos financeiros."""

    @abstractmethod
    def create(self, titulo: Titulo) -> Titulo:
        """Cria um novo titulo."""

    @abstractmethod
    def get_by_id(self, id: int) -> Titulo | None:
        """Busca titulo por ID."""

    @abstractmethod
    def update(self, titulo: Titulo) -> Titulo:
        """Atualiza um titulo existente."""

    @abstractmethod
    def delete(self, id: int) -> None:
        """Remove um titulo por ID."""

    @abstractmethod
    def list_by_escritorio(
        self,
        escritorio_id: int,
        empresa_id: int | None = None,
        tipo: TipoTitulo | None = None,
        status: StatusTitulo | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Titulo]:
        """Lista titulos de um escritorio com filtros opcionais."""

    @abstractmethod
    def total_por_status(
        self,
        escritorio_id: int,
        status: StatusTitulo,
        tipo: TipoTitulo | None = None,
    ) -> Decimal:
        """Retorna a soma dos valores dos titulos com o status informado."""
