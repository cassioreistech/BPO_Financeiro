"""DTOs para a entidade Titulo."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class CadastrarTituloDTO:
    """DTO para cadastro de titulo financeiro."""

    escritorio_id: int
    plano_conta_id: int
    descricao: str
    tipo: str
    valor: Decimal
    data_emissao: date
    data_vencimento: date
    empresa_id: int | None = None
    centro_custo_id: int | None = None
    observacao: str | None = None


@dataclass(frozen=True)
class EditarTituloDTO:
    """DTO para edicao de titulo financeiro."""

    id: int
    escritorio_id: int
    plano_conta_id: int
    descricao: str
    tipo: str
    valor: Decimal
    data_emissao: date
    data_vencimento: date
    empresa_id: int | None = None
    centro_custo_id: int | None = None
    observacao: str | None = None


@dataclass(frozen=True)
class TituloResponseDTO:
    """DTO de resposta para titulo financeiro."""

    id: int
    escritorio_id: int
    empresa_id: int | None
    plano_conta_id: int
    centro_custo_id: int | None
    descricao: str
    tipo: str
    status: str
    valor: Decimal
    data_emissao: date
    data_vencimento: date
    data_quitacao: date | None
    observacao: str | None
