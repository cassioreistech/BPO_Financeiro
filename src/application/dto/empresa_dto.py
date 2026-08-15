"""DTOs para a entidade Empresa."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CadastrarEmpresaDTO:
    """DTO para cadastro de empresa."""

    escritorio_id: int
    cnpj: str
    razao_social: str
    nome_fantasia: str
    regime_tributario: str
    contador_id: int | None = None
    email_financeiro: str | None = None
    telefone_financeiro: str | None = None


@dataclass(frozen=True)
class EditarEmpresaDTO:
    """DTO para edicao de empresa."""

    id: int
    escritorio_id: int
    cnpj: str
    razao_social: str
    nome_fantasia: str
    regime_tributario: str
    contador_id: int | None = None
    email_financeiro: str | None = None
    telefone_financeiro: str | None = None


@dataclass(frozen=True)
class EmpresaResponseDTO:
    """DTO de resposta para empresa."""

    id: int
    escritorio_id: int
    cnpj: str
    razao_social: str
    nome_fantasia: str
    regime_tributario: str
    ativo: bool
    contador_id: int | None = None
    email_financeiro: str | None = None
    telefone_financeiro: str | None = None
