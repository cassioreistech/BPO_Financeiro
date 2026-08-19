"""Use cases para a entidade CentroCusto."""

from __future__ import annotations

from application.dto.centro_custo_dto import (
    CadastrarCentroCustoDTO,
    CentroCustoResponseDTO,
    EditarCentroCustoDTO,
)
from application.ports.centro_custo_repository import CentroCustoRepository
from domain.entities.centro_custo import CentroCusto


def _para_response_dto(centro: CentroCusto) -> CentroCustoResponseDTO:
    """Converte entidade CentroCusto para ResponseDTO."""
    return CentroCustoResponseDTO(
        id=centro.id if centro.id is not None else 0,
        empresa_id=centro.empresa_id,
        codigo=centro.codigo,
        nome=centro.nome,
        ativo=centro.ativo,
    )


class CadastrarCentroCustoUseCase:
    """Use case para cadastro de centro de custo."""

    def __init__(self, repository: CentroCustoRepository) -> None:
        self._repository = repository

    def execute(self, dto: CadastrarCentroCustoDTO) -> CentroCustoResponseDTO:
        """Executa o cadastro de um centro de custo.

        Raises:
            ValueError: se dados invalidos ou codigo duplicado.
        """
        if not dto.codigo or not dto.codigo.strip():
            raise ValueError("Codigo do centro de custo não pode ser vazio.")
        if not dto.nome or not dto.nome.strip():
            raise ValueError("Nome do centro de custo não pode ser vazio.")
        if dto.empresa_id <= 0:
            raise ValueError("Empresa ID deve ser um numero positivo.")

        existente = self._repository.get_by_codigo(dto.empresa_id, dto.codigo)
        if existente is not None:
            raise ValueError(
                f"Ja existe centro de custo com codigo '{dto.codigo}' nesta empresa."
            )

        centro = CentroCusto(
            empresa_id=dto.empresa_id,
            codigo=dto.codigo.strip(),
            nome=dto.nome.strip(),
        )

        salvo = self._repository.create(centro)
        return _para_response_dto(salvo)


class EditarCentroCustoUseCase:
    """Use case para edicao de centro de custo."""

    def __init__(self, repository: CentroCustoRepository) -> None:
        self._repository = repository

    def execute(self, dto: EditarCentroCustoDTO) -> CentroCustoResponseDTO:
        """Executa a edicao de um centro de custo.

        Raises:
            ValueError: se centro não existe ou dados invalidos.
        """
        existente = self._repository.get_by_id(dto.id)
        if existente is None:
            raise ValueError(f"Centro de custo com ID {dto.id} não encontrado.")

        if not dto.codigo or not dto.codigo.strip():
            raise ValueError("Codigo do centro de custo não pode ser vazio.")
        if not dto.nome or not dto.nome.strip():
            raise ValueError("Nome do centro de custo não pode ser vazio.")

        conflito = self._repository.get_by_codigo(dto.empresa_id, dto.codigo)
        if conflito is not None and conflito.id != dto.id:
            raise ValueError(
                f"Ja existe centro de custo com codigo '{dto.codigo}' nesta empresa."
            )

        centro = CentroCusto(
            id=dto.id,
            empresa_id=dto.empresa_id,
            codigo=dto.codigo.strip(),
            nome=dto.nome.strip(),
            ativo=existente.ativo,
        )

        salvo = self._repository.update(centro)
        return _para_response_dto(salvo)


class ListarCentroCustoUseCase:
    """Use case para listagem de centros de custo."""

    def __init__(self, repository: CentroCustoRepository) -> None:
        self._repository = repository

    def execute(
        self,
        empresa_id: int,
        ativo: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CentroCustoResponseDTO]:
        """Lista centros de custo de uma empresa."""
        centros = self._repository.list_by_empresa(
            empresa_id=empresa_id, ativo=ativo, skip=skip, limit=limit
        )
        return [_para_response_dto(c) for c in centros]


class ObterCentroCustoUseCase:
    """Use case para obter centro de custo por ID."""

    def __init__(self, repository: CentroCustoRepository) -> None:
        self._repository = repository

    def execute(self, id: int) -> CentroCustoResponseDTO:
        """Obtem centro de custo por ID.

        Raises:
            ValueError: se centro não existe.
        """
        centro = self._repository.get_by_id(id)
        if centro is None:
            raise ValueError(f"Centro de custo com ID {id} não encontrado.")
        return _para_response_dto(centro)


class DesativarCentroCustoUseCase:
    """Use case para desativacao de centro de custo (soft delete)."""

    def __init__(self, repository: CentroCustoRepository) -> None:
        self._repository = repository

    def execute(self, id: int) -> CentroCustoResponseDTO:
        """Desativa um centro de custo.

        Raises:
            ValueError: se centro não existe.
        """
        existente = self._repository.get_by_id(id)
        if existente is None:
            raise ValueError(f"Centro de custo com ID {id} não encontrado.")

        centro = CentroCusto(
            id=existente.id,
            empresa_id=existente.empresa_id,
            codigo=existente.codigo,
            nome=existente.nome,
            ativo=False,
        )

        salvo = self._repository.update(centro)
        return _para_response_dto(salvo)
