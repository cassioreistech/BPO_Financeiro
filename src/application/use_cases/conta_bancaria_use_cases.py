"""Use cases para a entidade ContaBancaria."""

from __future__ import annotations

from application.dto.conta_bancaria_dto import (
    CadastrarContaBancariaDTO,
    ContaBancariaResponseDTO,
    EditarContaBancariaDTO,
)
from application.ports.conta_bancaria_repository import ContaBancariaRepository
from domain.entities.conta_bancaria import ContaBancaria
from domain.enums.tipo_conta_bancaria import TipoContaBancaria
from domain.value_objects.banco_codigo import BancoCodigo


def _para_response_dto(conta: ContaBancaria) -> ContaBancariaResponseDTO:
    """Converte entidade ContaBancaria para ResponseDTO."""
    return ContaBancariaResponseDTO(
        id=conta.id if conta.id is not None else 0,
        empresa_id=conta.empresa_id,
        banco_nome=conta.banco_nome,
        banco_codigo=str(conta.banco_codigo) if conta.banco_codigo else "",
        agencia=conta.agencia,
        conta=conta.conta,
        tipo=conta.tipo.value,
        descricao=conta.descricao,
        ativo=conta.ativo,
    )


class CadastrarContaBancariaUseCase:
    """Use case para cadastro de conta bancaria."""

    def __init__(self, repository: ContaBancariaRepository) -> None:
        self._repository = repository

    def execute(self, dto: CadastrarContaBancariaDTO) -> ContaBancariaResponseDTO:
        """Executa o cadastro de uma conta bancaria.

        Raises:
            ValueError: se dados invalidos.
        """
        if not dto.banco_nome or not dto.banco_nome.strip():
            raise ValueError("Nome do banco não pode ser vazio.")
        if not dto.agencia or not dto.agencia.strip():
            raise ValueError("Agencia não pode ser vazia.")
        if not dto.conta or not dto.conta.strip():
            raise ValueError("Conta não pode ser vazia.")
        if not dto.descricao or not dto.descricao.strip():
            raise ValueError("Descricao não pode ser vazia.")
        if dto.empresa_id <= 0:
            raise ValueError("Empresa ID deve ser um numero positivo.")

        try:
            tipo = TipoContaBancaria(dto.tipo)
        except ValueError:
            tipos_validos = [t.value for t in TipoContaBancaria]
            raise ValueError(
                f"Tipo de conta invalido: '{dto.tipo}'. "
                f"Valores aceitos: {tipos_validos}."
            ) from None

        banco_codigo = BancoCodigo(dto.banco_codigo) if dto.banco_codigo else None

        conta = ContaBancaria(
            empresa_id=dto.empresa_id,
            banco_nome=dto.banco_nome.strip(),
            banco_codigo=banco_codigo,
            agencia=dto.agencia.strip(),
            conta=dto.conta.strip(),
            tipo=tipo,
            descricao=dto.descricao.strip(),
        )

        salva = self._repository.create(conta)
        return _para_response_dto(salva)


class EditarContaBancariaUseCase:
    """Use case para edicao de conta bancaria."""

    def __init__(self, repository: ContaBancariaRepository) -> None:
        self._repository = repository

    def execute(self, dto: EditarContaBancariaDTO) -> ContaBancariaResponseDTO:
        """Executa a edicao de uma conta bancaria.

        Raises:
            ValueError: se conta não existe ou dados invalidos.
        """
        existente = self._repository.get_by_id(dto.id)
        if existente is None:
            raise ValueError(f"Conta bancaria com ID {dto.id} não encontrada.")

        if not dto.banco_nome or not dto.banco_nome.strip():
            raise ValueError("Nome do banco não pode ser vazio.")
        if not dto.agencia or not dto.agencia.strip():
            raise ValueError("Agencia não pode ser vazia.")
        if not dto.conta or not dto.conta.strip():
            raise ValueError("Conta não pode ser vazia.")
        if not dto.descricao or not dto.descricao.strip():
            raise ValueError("Descricao não pode ser vazia.")

        try:
            tipo = TipoContaBancaria(dto.tipo)
        except ValueError:
            tipos_validos = [t.value for t in TipoContaBancaria]
            raise ValueError(
                f"Tipo de conta invalido: '{dto.tipo}'. "
                f"Valores aceitos: {tipos_validos}."
            ) from None

        banco_codigo = BancoCodigo(dto.banco_codigo) if dto.banco_codigo else None

        conta = ContaBancaria(
            id=dto.id,
            empresa_id=dto.empresa_id,
            banco_nome=dto.banco_nome.strip(),
            banco_codigo=banco_codigo,
            agencia=dto.agencia.strip(),
            conta=dto.conta.strip(),
            tipo=tipo,
            descricao=dto.descricao.strip(),
            ativo=existente.ativo,
        )

        salva = self._repository.update(conta)
        return _para_response_dto(salva)


class ListarContasBancariasUseCase:
    """Use case para listagem de contas bancarias."""

    def __init__(self, repository: ContaBancariaRepository) -> None:
        self._repository = repository

    def execute(
        self, empresa_id: int | None = None, skip: int = 0, limit: int = 100
    ) -> list[ContaBancariaResponseDTO]:
        """Lista contas bancarias paginadas."""
        contas = self._repository.list_all(
            empresa_id=empresa_id, skip=skip, limit=limit
        )
        return [_para_response_dto(c) for c in contas]


class ObterContaBancariaUseCase:
    """Use case para obter conta bancaria por ID."""

    def __init__(self, repository: ContaBancariaRepository) -> None:
        self._repository = repository

    def execute(self, id: int) -> ContaBancariaResponseDTO:
        """Obtem conta bancaria por ID.

        Raises:
            ValueError: se conta não existe.
        """
        conta = self._repository.get_by_id(id)
        if conta is None:
            raise ValueError(f"Conta bancaria com ID {id} não encontrada.")
        return _para_response_dto(conta)


class DesativarContaBancariaUseCase:
    """Use case para desativacao de conta bancaria (soft delete)."""

    def __init__(self, repository: ContaBancariaRepository) -> None:
        self._repository = repository

    def execute(self, id: int) -> ContaBancariaResponseDTO:
        """Desativa uma conta bancaria (marca como inativa).

        Raises:
            ValueError: se conta não existe.
        """
        existente = self._repository.get_by_id(id)
        if existente is None:
            raise ValueError(f"Conta bancaria com ID {id} não encontrada.")

        from domain.enums.tipo_conta_bancaria import TipoContaBancaria

        conta = ContaBancaria(
            id=existente.id,
            empresa_id=existente.empresa_id,
            banco_nome=existente.banco_nome,
            banco_codigo=existente.banco_codigo,
            agencia=existente.agencia,
            conta=existente.conta,
            tipo=TipoContaBancaria(existente.tipo.value),
            descricao=existente.descricao,
            ativo=False,
        )

        salva = self._repository.update(conta)
        return _para_response_dto(salva)
