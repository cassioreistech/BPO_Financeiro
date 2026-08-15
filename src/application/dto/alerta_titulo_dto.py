"""DTOs para alertas de titulos."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class FiltroAlertasTitulosDTO:
    """Filtro para consulta de alertas de titulos."""

    empresa_id: int | None = None
    data_referencia: date | None = None
    incluir_vencidos: bool = True


@dataclass(frozen=True)
class ItemAlertaTituloResponseDTO:
    """Item de resposta para um alerta de titulo."""

    titulo_id: int
    empresa_id: int | None
    empresa_nome: str
    descricao: str
    categoria: str
    numero_documento: str | None
    valor: Decimal
    data_vencimento: date
    status: str
    urgencia: str


@dataclass(frozen=True)
class GrupoAlertaTituloResponseDTO:
    """Grupo de alertas com totalizadores."""

    urgencia: str
    quantidade: int
    valor_total: Decimal
    itens: list[ItemAlertaTituloResponseDTO]


@dataclass(frozen=True)
class DashboardAlertasTitulosResponseDTO:
    """Resposta completa do dashboard de alertas de titulos."""

    vencidos: GrupoAlertaTituloResponseDTO
    vence_hoje: GrupoAlertaTituloResponseDTO
    vence_amanha: GrupoAlertaTituloResponseDTO
    semana: GrupoAlertaTituloResponseDTO
    total_quantidade: int
    total_valor: Decimal
