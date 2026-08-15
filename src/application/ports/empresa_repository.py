"""Port (interface) para persistencia de Empresa."""

from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.empresa import Empresa


class EmpresaRepository(ABC):
    """Interface abstrata para repositorio de empresas.

    Implementacoes concretas serao criadas na camada de infraestrutura.
    """

    @abstractmethod
    def create(self, empresa: Empresa) -> Empresa:
        """Cria uma nova empresa."""

    @abstractmethod
    def get_by_id(self, id: int) -> Empresa | None:
        """Busca empresa por ID."""

    @abstractmethod
    def get_by_cnpj(self, cnpj: str) -> Empresa | None:
        """Busca empresa por CNPJ (somente digitos)."""

    @abstractmethod
    def update(self, empresa: Empresa) -> Empresa:
        """Atualiza uma empresa existente."""

    @abstractmethod
    def delete(self, id: int) -> None:
        """Remove uma empresa por ID."""

    @abstractmethod
    def list_all(
        self,
        escritorio_id: int | None = None,
        contador_id: int | None = None,
        ativo: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Empresa]:
        """Lista empresas com filtros e paginacao."""
