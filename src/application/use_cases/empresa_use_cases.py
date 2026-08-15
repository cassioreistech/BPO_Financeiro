"""Use cases para a entidade Empresa."""

from __future__ import annotations

import re

from application.dto.empresa_dto import (
    CadastrarEmpresaDTO,
    EditarEmpresaDTO,
    EmpresaResponseDTO,
)
from application.ports.empresa_repository import EmpresaRepository
from domain.entities.empresa import Empresa
from domain.enums.regime_tributario import RegimeTributario
from domain.enums.status_empresa import StatusEmpresa
from domain.value_objects.cnpj import CNPJ
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone


def _para_response_dto(emp: Empresa) -> EmpresaResponseDTO:
    """Converte entidade Empresa para ResponseDTO."""
    return EmpresaResponseDTO(
        id=emp.id if emp.id is not None else 0,
        escritorio_id=emp.escritorio_id,
        cnpj=emp.cnpj.valor,
        razao_social=emp.razao_social,
        nome_fantasia=emp.nome_fantasia,
        regime_tributario=emp.regime_tributario.value,
        ativo=emp.ativo == StatusEmpresa.ATIVA,
        contador_id=emp.contador_id,
        email_financeiro=str(emp.email_financeiro) if emp.email_financeiro else None,
        telefone_financeiro=str(emp.telefone_financeiro) if emp.telefone_financeiro else None,
    )


class CadastrarEmpresaUseCase:
    """Use case para cadastro de empresa."""

    def __init__(self, repository: EmpresaRepository) -> None:
        self._repository = repository

    def execute(self, dto: CadastrarEmpresaDTO) -> EmpresaResponseDTO:
        """Executa o cadastro de uma empresa.

        Raises:
            ValueError: se dados invalidos ou CNPJ duplicado.
        """
        if not dto.razao_social or not dto.razao_social.strip():
            raise ValueError("Razao social nao pode ser vazia.")
        if not dto.nome_fantasia or not dto.nome_fantasia.strip():
            raise ValueError("Nome fantasia nao pode ser vazio.")

        cnpj_limpo = re.sub(r"\D", "", dto.cnpj)
        existente = self._repository.get_by_cnpj(cnpj_limpo)
        if existente is not None:
            raise ValueError(f"Ja existe empresa com CNPJ '{dto.cnpj}'.")

        try:
            regime = RegimeTributario(dto.regime_tributario)
        except ValueError:
            regimes_validos = [r.value for r in RegimeTributario]
            raise ValueError(
                f"Regime tributario invalido: '{dto.regime_tributario}'. "
                f"Valores aceitos: {regimes_validos}."
            ) from None

        email = Email(dto.email_financeiro) if dto.email_financeiro else None
        telefone = Telefone(dto.telefone_financeiro) if dto.telefone_financeiro else None

        cnpj = CNPJ(cnpj_limpo)

        empresa = Empresa(
            escritorio_id=dto.escritorio_id,
            contador_id=dto.contador_id,
            cnpj=cnpj,
            razao_social=dto.razao_social.strip(),
            nome_fantasia=dto.nome_fantasia.strip(),
            regime_tributario=regime,
            email_financeiro=email,
            telefone_financeiro=telefone,
        )

        salva = self._repository.create(empresa)
        return _para_response_dto(salva)


class EditarEmpresaUseCase:
    """Use case para edicao de empresa."""

    def __init__(self, repository: EmpresaRepository) -> None:
        self._repository = repository

    def execute(self, dto: EditarEmpresaDTO) -> EmpresaResponseDTO:
        """Executa a edicao de uma empresa.

        Raises:
            ValueError: se empresa nao existe, dados invalidos ou CNPJ duplicado.
        """
        existente = self._repository.get_by_id(dto.id)
        if existente is None:
            raise ValueError(f"Empresa com ID {dto.id} nao encontrada.")

        if not dto.razao_social or not dto.razao_social.strip():
            raise ValueError("Razao social nao pode ser vazia.")
        if not dto.nome_fantasia or not dto.nome_fantasia.strip():
            raise ValueError("Nome fantasia nao pode ser vazio.")

        cnpj_limpo = re.sub(r"\D", "", dto.cnpj)
        conflito = self._repository.get_by_cnpj(cnpj_limpo)
        if conflito is not None and conflito.id != dto.id:
            raise ValueError(f"Ja existe empresa com CNPJ '{dto.cnpj}'.")

        try:
            regime = RegimeTributario(dto.regime_tributario)
        except ValueError:
            regimes_validos = [r.value for r in RegimeTributario]
            raise ValueError(
                f"Regime tributario invalido: '{dto.regime_tributario}'. "
                f"Valores aceitos: {regimes_validos}."
            ) from None

        email = Email(dto.email_financeiro) if dto.email_financeiro else None
        telefone = Telefone(dto.telefone_financeiro) if dto.telefone_financeiro else None

        cnpj = CNPJ(cnpj_limpo)

        empresa = Empresa(
            id=dto.id,
            escritorio_id=dto.escritorio_id,
            contador_id=dto.contador_id,
            cnpj=cnpj,
            razao_social=dto.razao_social.strip(),
            nome_fantasia=dto.nome_fantasia.strip(),
            regime_tributario=regime,
            email_financeiro=email,
            telefone_financeiro=telefone,
            ativo=existente.ativo,
        )

        salva = self._repository.update(empresa)
        return _para_response_dto(salva)


class DesativarEmpresaUseCase:
    """Use case para desativacao de empresa (soft delete)."""

    def __init__(self, repository: EmpresaRepository) -> None:
        self._repository = repository

    def execute(self, id: int) -> EmpresaResponseDTO:
        """Desativa uma empresa (marca como INATIVA).

        Raises:
            ValueError: se empresa nao existe.
        """
        existente = self._repository.get_by_id(id)
        if existente is None:
            raise ValueError(f"Empresa com ID {id} nao encontrada.")

        empresa = Empresa(
            id=existente.id,
            escritorio_id=existente.escritorio_id,
            contador_id=existente.contador_id,
            cnpj=existente.cnpj,
            razao_social=existente.razao_social,
            nome_fantasia=existente.nome_fantasia,
            regime_tributario=existente.regime_tributario,
            email_financeiro=existente.email_financeiro,
            telefone_financeiro=existente.telefone_financeiro,
            ativo=StatusEmpresa.INATIVA,
        )

        salva = self._repository.update(empresa)
        return _para_response_dto(salva)


class ListarEmpresasUseCase:
    """Use case para listagem de empresas."""

    def __init__(self, repository: EmpresaRepository) -> None:
        self._repository = repository

    def execute(
        self,
        escritorio_id: int | None = None,
        contador_id: int | None = None,
        ativo: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[EmpresaResponseDTO]:
        """Lista empresas com filtros e paginacao."""
        empresas = self._repository.list_all(
            escritorio_id=escritorio_id,
            contador_id=contador_id,
            ativo=ativo,
            skip=skip,
            limit=limit,
        )
        return [_para_response_dto(e) for e in empresas]


class ObterEmpresaUseCase:
    """Use case para obter empresa por ID."""

    def __init__(self, repository: EmpresaRepository) -> None:
        self._repository = repository

    def execute(self, id: int) -> EmpresaResponseDTO:
        """Obtem empresa por ID.

        Raises:
            ValueError: se empresa nao existe.
        """
        empresa = self._repository.get_by_id(id)
        if empresa is None:
            raise ValueError(f"Empresa com ID {id} nao encontrada.")
        return _para_response_dto(empresa)
