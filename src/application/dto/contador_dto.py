"""DTOs para a entidade Contador."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CadastrarContadorDTO:
    """DTO para cadastro de contador."""

    escritorio_id: int
    nome: str
    crc: str | None = None
    email: str | None = None
    telefone: str | None = None


@dataclass(frozen=True)
class EditarContadorDTO:
    """DTO para edicao de contador."""

    id: int
    escritorio_id: int
    nome: str
    crc: str | None = None
    email: str | None = None
    telefone: str | None = None


@dataclass(frozen=True)
class ContadorResponseDTO:
    """DTO de resposta para contador."""

    id: int
    escritorio_id: int
    nome: str
    crc: str | None = None
    email: str | None = None
    telefone: str | None = None
