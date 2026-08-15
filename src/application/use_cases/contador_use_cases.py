"""Use cases para a entidade Contador."""

from __future__ import annotations

from application.dto.contador_dto import (
    CadastrarContadorDTO,
    ContadorResponseDTO,
    EditarContadorDTO,
)
from application.ports.contador_repository import ContadorRepository
from domain.entities.contador import Contador
from domain.value_objects.crc import CRC
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone


def _para_response_dto(cont: Contador) -> ContadorResponseDTO:
    """Converte entidade Contador para ResponseDTO."""
    return ContadorResponseDTO(
        id=cont.id if cont.id is not None else 0,
        escritorio_id=cont.escritorio_id,
        nome=cont.nome,
        crc=str(cont.crc) if cont.crc else None,
        email=str(cont.email) if cont.email else None,
        telefone=str(cont.telefone) if cont.telefone else None,
    )


class CadastrarContadorUseCase:
    """Use case para cadastro de contador."""

    def __init__(self, repository: ContadorRepository) -> None:
        self._repository = repository

    def execute(self, dto: CadastrarContadorDTO) -> ContadorResponseDTO:
        """Executa o cadastro de um contador.

        Raises:
            ValueError: se dados invalidos.
        """
        if not dto.nome or not dto.nome.strip():
            raise ValueError("Nome do contador nao pode ser vazio.")
        if dto.escritorio_id <= 0:
            raise ValueError("Escritorio ID deve ser um numero positivo.")

        crc = CRC(dto.crc) if dto.crc else None
        email = Email(dto.email) if dto.email else None
        telefone = Telefone(dto.telefone) if dto.telefone else None

        contador = Contador(
            escritorio_id=dto.escritorio_id,
            nome=dto.nome.strip(),
            crc=crc,
            email=email,
            telefone=telefone,
        )

        salvo = self._repository.create(contador)
        return _para_response_dto(salvo)


class EditarContadorUseCase:
    """Use case para edicao de contador."""

    def __init__(self, repository: ContadorRepository) -> None:
        self._repository = repository

    def execute(self, dto: EditarContadorDTO) -> ContadorResponseDTO:
        """Executa a edicao de um contador.

        Raises:
            ValueError: se contador nao existe ou dados invalidos.
        """
        existente = self._repository.get_by_id(dto.id)
        if existente is None:
            raise ValueError(f"Contador com ID {dto.id} nao encontrado.")

        if not dto.nome or not dto.nome.strip():
            raise ValueError("Nome do contador nao pode ser vazio.")

        crc = CRC(dto.crc) if dto.crc else None
        email = Email(dto.email) if dto.email else None
        telefone = Telefone(dto.telefone) if dto.telefone else None

        contador = Contador(
            id=dto.id,
            escritorio_id=dto.escritorio_id,
            nome=dto.nome.strip(),
            crc=crc,
            email=email,
            telefone=telefone,
        )

        salvo = self._repository.update(contador)
        return _para_response_dto(salvo)


class ListarContadoresUseCase:
    """Use case para listagem de contadores."""

    def __init__(self, repository: ContadorRepository) -> None:
        self._repository = repository

    def execute(
        self, escritorio_id: int | None = None, skip: int = 0, limit: int = 100
    ) -> list[ContadorResponseDTO]:
        """Lista contadores paginados."""
        contadores = self._repository.list_all(
            escritorio_id=escritorio_id, skip=skip, limit=limit
        )
        return [_para_response_dto(c) for c in contadores]


class ObterContadorUseCase:
    """Use case para obter contador por ID."""

    def __init__(self, repository: ContadorRepository) -> None:
        self._repository = repository

    def execute(self, id: int) -> ContadorResponseDTO:
        """Obtem contador por ID.

        Raises:
            ValueError: se contador nao existe.
        """
        contador = self._repository.get_by_id(id)
        if contador is None:
            raise ValueError(f"Contador com ID {id} nao encontrado.")
        return _para_response_dto(contador)


class ExcluirContadorUseCase:
    """Use case para exclusao de contador."""

    def __init__(self, repository: ContadorRepository) -> None:
        self._repository = repository

    def execute(self, id: int) -> None:
        """Exclui um contador por ID.

        Raises:
            ValueError: se contador nao existe.
        """
        existente = self._repository.get_by_id(id)
        if existente is None:
            raise ValueError(f"Contador com ID {id} nao encontrado.")
        self._repository.delete(id)
