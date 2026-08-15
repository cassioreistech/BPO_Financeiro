"""DTOs para a entidade Escritorio."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CriarEscritorioDTO:
    """DTO para criacao de escritorio."""

    nome: str
    cnpj_cpf: str
    email: str | None = None
    telefone: str | None = None


@dataclass(frozen=True)
class EditarEscritorioDTO:
    """DTO para edicao de escritorio."""

    id: int
    nome: str
    cnpj_cpf: str
    email: str | None = None
    telefone: str | None = None


@dataclass(frozen=True)
class EscritorioResponseDTO:
    """DTO de resposta para escritorio."""

    id: int
    nome: str
    cnpj_cpf: str
    email: str | None = None
    telefone: str | None = None
