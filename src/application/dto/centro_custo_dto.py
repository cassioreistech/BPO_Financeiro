"""DTOs para a entidade CentroCusto."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CadastrarCentroCustoDTO:
    """DTO para cadastro de centro de custo."""

    empresa_id: int
    codigo: str
    nome: str


@dataclass(frozen=True)
class EditarCentroCustoDTO:
    """DTO para edicao de centro de custo."""

    id: int
    empresa_id: int
    codigo: str
    nome: str


@dataclass(frozen=True)
class CentroCustoResponseDTO:
    """DTO de resposta para centro de custo."""

    id: int
    empresa_id: int
    codigo: str
    nome: str
    ativo: bool
