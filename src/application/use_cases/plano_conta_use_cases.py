"""Use cases para a entidade PlanoConta."""

from __future__ import annotations

from application.dto.plano_conta_dto import (
    CadastrarPlanoContaDTO,
    EditarPlanoContaDTO,
    PlanoContaResponseDTO,
)
from application.ports.plano_conta_repository import PlanoContaRepository
from domain.entities.plano_conta import PlanoConta
from domain.enums.tipo_plano_conta import TipoPlanoConta


def _para_response_dto(plano: PlanoConta) -> PlanoContaResponseDTO:
    """Converte entidade PlanoConta para ResponseDTO."""
    return PlanoContaResponseDTO(
        id=plano.id if plano.id is not None else 0,
        escritorio_id=plano.escritorio_id,
        codigo=plano.codigo,
        nome=plano.nome,
        tipo=plano.tipo.value,
        nivel=plano.nivel,
        pai_id=plano.pai_id,
    )


class GarantirContaPadraoUseCase:
    """Garante a existencia de uma conta padrao em cada escritorio.

    Utilizado para lancamentos simplificados, onde o usuario nao escolhe
    uma conta do plano de contas manualmente.
    """

    CODIGO_PADRAO = "0.00"
    NOME_PADRAO = "Lancamentos diversos"
    TIPO_PADRAO = TipoPlanoConta.OUTRO.value

    def __init__(self, repository: PlanoContaRepository) -> None:
        self._repository = repository

    def execute(self, escritorio_id: int) -> int:
        """Retorna o ID da conta padrao do escritorio, criando se necessario.

        Raises:
            ValueError: se escritorio_id invalido.
            RuntimeError: se a conta nao puder ser criada.
        """
        if escritorio_id <= 0:
            raise ValueError("Escritorio ID deve ser um numero positivo.")

        existente = self._repository.get_by_codigo(
            escritorio_id, self.CODIGO_PADRAO
        )
        if existente is not None and existente.id is not None:
            return existente.id

        plano = PlanoConta(
            escritorio_id=escritorio_id,
            codigo=self.CODIGO_PADRAO,
            nome=self.NOME_PADRAO,
            tipo=TipoPlanoConta(self.TIPO_PADRAO),
        )
        criado = self._repository.create(plano)
        if criado.id is None:
            raise RuntimeError("Falha ao criar conta padrao do escritorio.")
        return criado.id


class CadastrarPlanoContaUseCase:
    """Use case para cadastro de conta no plano."""

    def __init__(self, repository: PlanoContaRepository) -> None:
        self._repository = repository

    def execute(self, dto: CadastrarPlanoContaDTO) -> PlanoContaResponseDTO:
        """Executa o cadastro de uma conta.

        Raises:
            ValueError: se dados invalidos ou codigo duplicado.
        """
        if not dto.codigo or not dto.codigo.strip():
            raise ValueError("Codigo da conta não pode ser vazio.")
        if not dto.nome or not dto.nome.strip():
            raise ValueError("Nome da conta não pode ser vazio.")
        if dto.escritorio_id <= 0:
            raise ValueError("Escritorio ID deve ser um numero positivo.")

        existente = self._repository.get_by_codigo(dto.escritorio_id, dto.codigo)
        if existente is not None:
            raise ValueError(
                f"Ja existe conta com codigo '{dto.codigo}' neste escritorio."
            )

        try:
            tipo = TipoPlanoConta(dto.tipo)
        except ValueError:
            tipos_validos = [t.value for t in TipoPlanoConta]
            raise ValueError(
                f"Tipo de conta invalido: '{dto.tipo}'. "
                f"Valores aceitos: {tipos_validos}."
            ) from None

        plano = PlanoConta(
            escritorio_id=dto.escritorio_id,
            codigo=dto.codigo.strip(),
            nome=dto.nome.strip(),
            tipo=tipo,
            nivel=dto.nivel,
            pai_id=dto.pai_id,
        )

        salvo = self._repository.create(plano)
        return _para_response_dto(salvo)


class EditarPlanoContaUseCase:
    """Use case para edicao de conta no plano."""

    def __init__(self, repository: PlanoContaRepository) -> None:
        self._repository = repository

    def execute(self, dto: EditarPlanoContaDTO) -> PlanoContaResponseDTO:
        """Executa a edicao de uma conta.

        Raises:
            ValueError: se conta não existe ou dados invalidos.
        """
        existente = self._repository.get_by_id(dto.id)
        if existente is None:
            raise ValueError(f"Conta com ID {dto.id} não encontrada.")

        if not dto.codigo or not dto.codigo.strip():
            raise ValueError("Codigo da conta não pode ser vazio.")
        if not dto.nome or not dto.nome.strip():
            raise ValueError("Nome da conta não pode ser vazio.")

        conflito = self._repository.get_by_codigo(dto.escritorio_id, dto.codigo)
        if conflito is not None and conflito.id != dto.id:
            raise ValueError(
                f"Ja existe conta com codigo '{dto.codigo}' neste escritorio."
            )

        try:
            tipo = TipoPlanoConta(dto.tipo)
        except ValueError:
            tipos_validos = [t.value for t in TipoPlanoConta]
            raise ValueError(
                f"Tipo de conta invalido: '{dto.tipo}'. "
                f"Valores aceitos: {tipos_validos}."
            ) from None

        plano = PlanoConta(
            id=dto.id,
            escritorio_id=dto.escritorio_id,
            codigo=dto.codigo.strip(),
            nome=dto.nome.strip(),
            tipo=tipo,
            nivel=dto.nivel,
            pai_id=dto.pai_id,
        )

        salvo = self._repository.update(plano)
        return _para_response_dto(salvo)


class ListarPlanoContaUseCase:
    """Use case para listagem de contas do plano."""

    def __init__(self, repository: PlanoContaRepository) -> None:
        self._repository = repository

    def execute(
        self, escritorio_id: int, skip: int = 0, limit: int = 100
    ) -> list[PlanoContaResponseDTO]:
        """Lista contas de um escritorio."""
        contas = self._repository.list_by_escritorio(
            escritorio_id=escritorio_id, skip=skip, limit=limit
        )
        return [_para_response_dto(c) for c in contas]


class ObterPlanoContaUseCase:
    """Use case para obter conta por ID."""

    def __init__(self, repository: PlanoContaRepository) -> None:
        self._repository = repository

    def execute(self, id: int) -> PlanoContaResponseDTO:
        """Obtem conta por ID.

        Raises:
            ValueError: se conta não existe.
        """
        plano = self._repository.get_by_id(id)
        if plano is None:
            raise ValueError(f"Conta com ID {id} não encontrada.")
        return _para_response_dto(plano)


class RemoverPlanoContaUseCase:
    """Use case para remocao de conta do plano."""

    def __init__(self, repository: PlanoContaRepository) -> None:
        self._repository = repository

    def execute(self, id: int) -> None:
        """Remove uma conta por ID.

        Raises:
            ValueError: se conta não existe.
        """
        existente = self._repository.get_by_id(id)
        if existente is None:
            raise ValueError(f"Conta com ID {id} não encontrada.")
        self._repository.delete(id)
