"""DTOs para a entidade Titulo."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class FiltroTitulosDTO:
    """DTO para filtragem avancada de titulos."""

    empresa_id: int | None = None
    texto: str | None = None
    categoria: str | None = None
    tipo: str | None = None
    status: str | None = None
    data_vencimento_inicio: date | None = None
    data_vencimento_fim: date | None = None
    situacao_vencimento: str | None = None


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
    numero_documento: str | None = None
    codigo_barras: str | None = None
    categoria: str = "OUTRO"
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
    numero_documento: str | None = None
    codigo_barras: str | None = None
    categoria: str = "OUTRO"
    observacao: str | None = None


@dataclass(frozen=True)
class QuitarTituloDTO:
    """DTO para quitacao de titulo financeiro."""

    id: int
    data_quitacao: date
    valor_pago: Decimal
    conta_bancaria_id: int | None = None
    forma_pagamento: str = "OUTRO"
    observacao_quitacao: str | None = None
    empresa_id: int | None = None


@dataclass(frozen=True)
class TituloResponseDTO:
    """DTO de resposta para titulo financeiro."""

    id: int
    escritorio_id: int
    empresa_id: int | None
    plano_conta_id: int
    centro_custo_id: int | None
    numero_documento: str | None
    codigo_barras: str | None
    categoria: str
    descricao: str
    tipo: str
    status: str
    valor: Decimal
    valor_pago: Decimal | None
    data_emissao: date
    data_vencimento: date
    data_quitacao: date | None
    conta_bancaria_id: int | None
    forma_pagamento: str
    observacao: str | None
    observacao_quitacao: str | None
