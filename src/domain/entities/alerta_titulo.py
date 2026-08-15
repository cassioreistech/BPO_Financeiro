"""Entidades de leitura para alertas de titulos.

Essas estruturas sao usadas apenas para exposicao de dados no dashboard
de alertas, sem alterar a entidade principal Titulo.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import StrEnum

from domain.enums.status_titulo import StatusTitulo


class NivelUrgencia(StrEnum):
    """Niveis de urgencia para alertas de titulos."""

    CRITICO = "CRITICO"
    ALTO = "ALTO"
    MEDIO = "MEDIO"
    INFORMATIVO = "INFORMATIVO"


@dataclass(frozen=True)
class AlertaTitulo:
    """Item de alerta de titulo em aberto.

    Atributos:
        titulo_id: identificador do titulo.
        empresa_id: identificador da empresa (pode ser None).
        empresa_nome: nome fantasia ou razao social da empresa.
        descricao: descricao do titulo.
        categoria: categoria do titulo.
        numero_documento: numero do documento, se houver.
        valor: valor original do titulo.
        data_vencimento: data de vencimento.
        status: status do titulo (sempre ABERTO nos alertas).
        urgencia: nivel de urgencia calculado.
    """

    titulo_id: int
    empresa_id: int | None
    empresa_nome: str
    descricao: str
    categoria: str
    numero_documento: str | None
    valor: Decimal
    data_vencimento: date
    status: StatusTitulo
    urgencia: NivelUrgencia


@dataclass(frozen=True)
class GrupoAlertasTitulos:
    """Grupo de alertas com totalizadores."""

    urgencia: NivelUrgencia
    quantidade: int
    valor_total: Decimal
    itens: list[AlertaTitulo]


@dataclass(frozen=True)
class ResumoAlertasTitulos:
    """Resumo completo dos alertas de titulos."""

    vencidos: GrupoAlertasTitulos
    vence_hoje: GrupoAlertasTitulos
    vence_amanha: GrupoAlertasTitulos
    semana: GrupoAlertasTitulos
    total_quantidade: int
    total_valor: Decimal
