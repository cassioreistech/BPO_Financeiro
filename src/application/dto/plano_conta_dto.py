"""DTOs para a entidade PlanoConta."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CadastrarPlanoContaDTO:
    """DTO para cadastro de plano de conta."""

    escritorio_id: int
    codigo: str
    nome: str
    tipo: str
    nivel: int = 1
    pai_id: int | None = None


@dataclass(frozen=True)
class EditarPlanoContaDTO:
    """DTO para edicao de plano de conta."""

    id: int
    escritorio_id: int
    codigo: str
    nome: str
    tipo: str
    nivel: int = 1
    pai_id: int | None = None


@dataclass(frozen=True)
class PlanoContaResponseDTO:
    """DTO de resposta para plano de conta."""

    id: int
    escritorio_id: int
    codigo: str
    nome: str
    tipo: str
    nivel: int
    pai_id: int | None = None
