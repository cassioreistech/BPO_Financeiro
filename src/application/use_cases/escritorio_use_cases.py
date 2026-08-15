"""Use cases para a entidade Escritorio."""

from __future__ import annotations

import re

from application.dto.escritorio_dto import (
    CriarEscritorioDTO,
    EditarEscritorioDTO,
    EscritorioResponseDTO,
)
from application.ports.escritorio_repository import EscritorioRepository
from domain.entities.escritorio import Escritorio
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone


def _para_response_dto(esc: Escritorio) -> EscritorioResponseDTO:
    """Converte entidade Escritorio para ResponseDTO."""
    return EscritorioResponseDTO(
        id=esc.id if esc.id is not None else 0,
        nome=esc.nome,
        cnpj_cpf=esc.cnpj_cpf,
        email=str(esc.email) if esc.email else None,
        telefone=str(esc.telefone) if esc.telefone else None,
    )


class CriarEscritorioUseCase:
    """Use case para criacao de escritorio."""

    def __init__(self, repository: EscritorioRepository) -> None:
        self._repository = repository

    def execute(self, dto: CriarEscritorioDTO) -> EscritorioResponseDTO:
        """Executa a criacao de um escritorio.

        Raises:
            ValueError: se nome vazio ou cnpj_cpf duplicado.
        """
        if not dto.nome or not dto.nome.strip():
            raise ValueError("Nome do escritorio nao pode ser vazio.")

        cnpj_cpf_limpo = re.sub(r"\D", "", dto.cnpj_cpf)
        existente = self._repository.get_by_cnpj(cnpj_cpf_limpo)
        if existente is not None:
            raise ValueError(
                f"Ja existe escritorio com CNPJ/CPF '{dto.cnpj_cpf}'."
            )

        email = Email(dto.email) if dto.email else None
        telefone = Telefone(dto.telefone) if dto.telefone else None

        escritorio = Escritorio(
            nome=dto.nome.strip(),
            cnpj_cpf=cnpj_cpf_limpo,
            email=email,
            telefone=telefone,
        )

        salvo = self._repository.create(escritorio)
        return _para_response_dto(salvo)


class EditarEscritorioUseCase:
    """Use case para edicao de escritorio."""

    def __init__(self, repository: EscritorioRepository) -> None:
        self._repository = repository

    def execute(self, dto: EditarEscritorioDTO) -> EscritorioResponseDTO:
        """Executa a edicao de um escritorio.

        Raises:
            ValueError: se escritorio nao existe, nome vazio ou cnpj_cpf duplicado.
        """
        existente = self._repository.get_by_id(dto.id)
        if existente is None:
            raise ValueError(f"Escritorio com ID {dto.id} nao encontrado.")

        if not dto.nome or not dto.nome.strip():
            raise ValueError("Nome do escritorio nao pode ser vazio.")

        cnpj_cpf_limpo = re.sub(r"\D", "", dto.cnpj_cpf)
        conflito = self._repository.get_by_cnpj(cnpj_cpf_limpo)
        if conflito is not None and conflito.id != dto.id:
            raise ValueError(
                f"Ja existe escritorio com CNPJ/CPF '{dto.cnpj_cpf}'."
            )

        email = Email(dto.email) if dto.email else None
        telefone = Telefone(dto.telefone) if dto.telefone else None

        escritorio = Escritorio(
            id=dto.id,
            nome=dto.nome.strip(),
            cnpj_cpf=cnpj_cpf_limpo,
            email=email,
            telefone=telefone,
        )

        salvo = self._repository.update(escritorio)
        return _para_response_dto(salvo)


class ListarEscritoriosUseCase:
    """Use case para listagem de escritorios."""

    def __init__(self, repository: EscritorioRepository) -> None:
        self._repository = repository

    def execute(self, skip: int = 0, limit: int = 100) -> list[EscritorioResponseDTO]:
        """Lista escritorios paginados."""
        escritorios = self._repository.list_all(skip=skip, limit=limit)
        return [_para_response_dto(e) for e in escritorios]


class ObterEscritorioUseCase:
    """Use case para obter escritorio por ID."""

    def __init__(self, repository: EscritorioRepository) -> None:
        self._repository = repository

    def execute(self, id: int) -> EscritorioResponseDTO:
        """Obtem escritorio por ID.

        Raises:
            ValueError: se escritorio nao existe.
        """
        escritorio = self._repository.get_by_id(id)
        if escritorio is None:
            raise ValueError(f"Escritorio com ID {id} nao encontrado.")
        return _para_response_dto(escritorio)


class ExcluirEscritorioUseCase:
    """Use case para exclusao de escritorio."""

    def __init__(self, repository: EscritorioRepository) -> None:
        self._repository = repository

    def execute(self, id: int) -> None:
        """Exclui um escritorio por ID.

        Raises:
            ValueError: se escritorio nao existe.
        """
        existente = self._repository.get_by_id(id)
        if existente is None:
            raise ValueError(f"Escritorio com ID {id} nao encontrado.")
        self._repository.delete(id)
