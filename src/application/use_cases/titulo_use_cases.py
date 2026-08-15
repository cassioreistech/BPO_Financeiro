"""Use cases para a entidade Titulo."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from application.dto.titulo_dto import (
    CadastrarTituloDTO,
    EditarTituloDTO,
    TituloResponseDTO,
)
from application.ports.titulo_repository import TituloRepository
from domain.entities.titulo import Titulo
from domain.enums.status_titulo import StatusTitulo
from domain.enums.tipo_titulo import TipoTitulo


def _para_response_dto(titulo: Titulo) -> TituloResponseDTO:
    """Converte entidade Titulo para ResponseDTO."""
    return TituloResponseDTO(
        id=titulo.id if titulo.id is not None else 0,
        escritorio_id=titulo.escritorio_id,
        empresa_id=titulo.empresa_id,
        plano_conta_id=titulo.plano_conta_id,
        centro_custo_id=titulo.centro_custo_id,
        descricao=titulo.descricao,
        tipo=titulo.tipo.value,
        status=titulo.status.value,
        valor=titulo.valor,
        data_emissao=titulo.data_emissao,
        data_vencimento=titulo.data_vencimento,
        data_quitacao=titulo.data_quitacao,
        observacao=titulo.observacao,
    )


def _validar_dto(dto: CadastrarTituloDTO | EditarTituloDTO) -> None:
    """Valida campos comuns dos DTOs de titulo."""
    if dto.escritorio_id <= 0:
        raise ValueError("Escritorio ID deve ser um numero positivo.")
    if dto.plano_conta_id <= 0:
        raise ValueError("Plano de Conta ID deve ser um numero positivo.")
    if dto.empresa_id is not None and dto.empresa_id <= 0:
        raise ValueError("Empresa ID deve ser um numero positivo.")
    if dto.centro_custo_id is not None and dto.centro_custo_id <= 0:
        raise ValueError("Centro de Custo ID deve ser um numero positivo.")
    if not dto.descricao or not dto.descricao.strip():
        raise ValueError("Descricao do titulo nao pode ser vazia.")
    if dto.valor <= Decimal("0"):
        raise ValueError("Valor do titulo deve ser maior que zero.")
    if dto.data_vencimento < dto.data_emissao:
        raise ValueError(
            "Data de vencimento nao pode ser anterior a data de emissao."
        )


def _parse_tipo(tipo_str: str) -> TipoTitulo:
    """Converte string para TipoTitulo."""
    try:
        return TipoTitulo(tipo_str)
    except ValueError:
        tipos_validos = [t.value for t in TipoTitulo]
        raise ValueError(
            f"Tipo de titulo invalido: '{tipo_str}'. "
            f"Valores aceitos: {tipos_validos}."
        ) from None


class CadastrarTituloUseCase:
    """Use case para cadastro de titulo financeiro."""

    def __init__(self, repository: TituloRepository) -> None:
        self._repository = repository

    def execute(self, dto: CadastrarTituloDTO) -> TituloResponseDTO:
        """Executa o cadastro de um titulo.

        Raises:
            ValueError: se dados invalidos.
        """
        _validar_dto(dto)
        tipo = _parse_tipo(dto.tipo)

        titulo = Titulo(
            escritorio_id=dto.escritorio_id,
            empresa_id=dto.empresa_id,
            plano_conta_id=dto.plano_conta_id,
            centro_custo_id=dto.centro_custo_id,
            descricao=dto.descricao.strip(),
            tipo=tipo,
            status=StatusTitulo.ABERTO,
            valor=dto.valor,
            data_emissao=dto.data_emissao,
            data_vencimento=dto.data_vencimento,
            observacao=dto.observacao.strip() if dto.observacao else None,
        )

        salvo = self._repository.create(titulo)
        return _para_response_dto(salvo)


class EditarTituloUseCase:
    """Use case para edicao de titulo financeiro."""

    def __init__(self, repository: TituloRepository) -> None:
        self._repository = repository

    def execute(self, dto: EditarTituloDTO) -> TituloResponseDTO:
        """Executa a edicao de um titulo.

        Raises:
            ValueError: se titulo nao existe ou dados invalidos.
        """
        existente = self._repository.get_by_id(dto.id)
        if existente is None:
            raise ValueError(f"Titulo com ID {dto.id} nao encontrado.")
        if existente.status == StatusTitulo.CANCELADO:
            raise ValueError("Nao e possivel editar um titulo cancelado.")

        _validar_dto(dto)
        tipo = _parse_tipo(dto.tipo)

        titulo = Titulo(
            id=dto.id,
            escritorio_id=dto.escritorio_id,
            empresa_id=dto.empresa_id,
            plano_conta_id=dto.plano_conta_id,
            centro_custo_id=dto.centro_custo_id,
            descricao=dto.descricao.strip(),
            tipo=tipo,
            status=existente.status,
            valor=dto.valor,
            data_emissao=dto.data_emissao,
            data_vencimento=dto.data_vencimento,
            data_quitacao=existente.data_quitacao,
            observacao=dto.observacao.strip() if dto.observacao else None,
        )

        salvo = self._repository.update(titulo)
        return _para_response_dto(salvo)


class ListarTitulosUseCase:
    """Use case para listagem de titulos financeiros."""

    def __init__(self, repository: TituloRepository) -> None:
        self._repository = repository

    def execute(
        self,
        escritorio_id: int,
        empresa_id: int | None = None,
        tipo: str | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TituloResponseDTO]:
        """Lista titulos de um escritorio com filtros opcionais."""
        tipo_enum = TipoTitulo(tipo) if tipo else None
        status_enum = StatusTitulo(status) if status else None
        titulos = self._repository.list_by_escritorio(
            escritorio_id=escritorio_id,
            empresa_id=empresa_id,
            tipo=tipo_enum,
            status=status_enum,
            skip=skip,
            limit=limit,
        )
        return [_para_response_dto(t) for t in titulos]


class ObterTituloUseCase:
    """Use case para obter titulo por ID."""

    def __init__(self, repository: TituloRepository) -> None:
        self._repository = repository

    def execute(self, id: int) -> TituloResponseDTO:
        """Obtem titulo por ID.

        Raises:
            ValueError: se titulo nao existe.
        """
        titulo = self._repository.get_by_id(id)
        if titulo is None:
            raise ValueError(f"Titulo com ID {id} nao encontrado.")
        return _para_response_dto(titulo)


class QuitarTituloUseCase:
    """Use case para quitacao de titulo."""

    def __init__(self, repository: TituloRepository) -> None:
        self._repository = repository

    def execute(self, id: int, data_quitacao: date | None = None) -> TituloResponseDTO:
        """Marca um titulo como pago.

        Raises:
            ValueError: se titulo nao existe ou ja esta cancelado.
        """
        existente = self._repository.get_by_id(id)
        if existente is None:
            raise ValueError(f"Titulo com ID {id} nao encontrado.")
        if existente.status == StatusTitulo.CANCELADO:
            raise ValueError("Nao e possivel quitar um titulo cancelado.")

        titulo = Titulo(
            id=existente.id,
            escritorio_id=existente.escritorio_id,
            empresa_id=existente.empresa_id,
            plano_conta_id=existente.plano_conta_id,
            centro_custo_id=existente.centro_custo_id,
            descricao=existente.descricao,
            tipo=existente.tipo,
            status=StatusTitulo.PAGO,
            valor=existente.valor,
            data_emissao=existente.data_emissao,
            data_vencimento=existente.data_vencimento,
            data_quitacao=data_quitacao or date.today(),
            observacao=existente.observacao,
        )

        salvo = self._repository.update(titulo)
        return _para_response_dto(salvo)


class CancelarTituloUseCase:
    """Use case para cancelamento de titulo."""

    def __init__(self, repository: TituloRepository) -> None:
        self._repository = repository

    def execute(self, id: int) -> TituloResponseDTO:
        """Marca um titulo como cancelado.

        Raises:
            ValueError: se titulo nao existe.
        """
        existente = self._repository.get_by_id(id)
        if existente is None:
            raise ValueError(f"Titulo com ID {id} nao encontrado.")

        titulo = Titulo(
            id=existente.id,
            escritorio_id=existente.escritorio_id,
            empresa_id=existente.empresa_id,
            plano_conta_id=existente.plano_conta_id,
            centro_custo_id=existente.centro_custo_id,
            descricao=existente.descricao,
            tipo=existente.tipo,
            status=StatusTitulo.CANCELADO,
            valor=existente.valor,
            data_emissao=existente.data_emissao,
            data_vencimento=existente.data_vencimento,
            data_quitacao=None,
            observacao=existente.observacao,
        )

        salvo = self._repository.update(titulo)
        return _para_response_dto(salvo)


class RemoverTituloUseCase:
    """Use case para remocao de titulo."""

    def __init__(self, repository: TituloRepository) -> None:
        self._repository = repository

    def execute(self, id: int) -> None:
        """Remove um titulo por ID.

        Raises:
            ValueError: se titulo nao existe.
        """
        existente = self._repository.get_by_id(id)
        if existente is None:
            raise ValueError(f"Titulo com ID {id} nao encontrado.")
        self._repository.delete(id)
