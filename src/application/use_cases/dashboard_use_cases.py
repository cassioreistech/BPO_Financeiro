"""Use cases para dashboard financeiro."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from application.ports.titulo_repository import TituloRepository
from domain.enums.status_titulo import StatusTitulo
from domain.enums.tipo_titulo import TipoTitulo


@dataclass(frozen=True)
class ResumoFinanceiroDTO:
    """DTO com indicadores financeiros de um escritorio."""

    a_receber: Decimal
    a_pagar: Decimal
    recebido: Decimal
    pago: Decimal
    vencido_receber: Decimal
    vencido_pagar: Decimal


class ResumoFinanceiroUseCase:
    """Use case que calcula totais financeiros para o dashboard."""

    def __init__(self, repository: TituloRepository) -> None:
        self._repository = repository

    def execute(self, escritorio_id: int, empresa_id: int | None = None) -> ResumoFinanceiroDTO:
        """Calcula os totais financeiros de um escritorio, opcionalmente filtrado por empresa.

        Raises:
            ValueError: se escritorio_id invalido.
        """
        if escritorio_id <= 0:
            raise ValueError("Escritorio ID deve ser um numero positivo.")

        def total(status: StatusTitulo, tipo: TipoTitulo) -> Decimal:
            if empresa_id is not None:
                titulos = self._repository.list_by_escritorio(
                    escritorio_id=escritorio_id,
                    empresa_id=empresa_id,
                    status=status,
                    tipo=tipo,
                    skip=0,
                    limit=10000,
                )
                return sum((t.valor for t in titulos), Decimal("0"))
            return self._repository.total_por_status(
                escritorio_id=escritorio_id, status=status, tipo=tipo
            )

        a_receber = total(StatusTitulo.ABERTO, TipoTitulo.RECEBER)
        a_pagar = total(StatusTitulo.ABERTO, TipoTitulo.PAGAR)
        recebido = total(StatusTitulo.PAGO, TipoTitulo.RECEBER)
        pago = total(StatusTitulo.PAGO, TipoTitulo.PAGAR)

        hoje = date.today()
        if empresa_id is not None:
            titulos_abertos = self._repository.list_by_escritorio(
                escritorio_id=escritorio_id,
                empresa_id=empresa_id,
                status=StatusTitulo.ABERTO,
                skip=0,
                limit=10000,
            )
        else:
            titulos_abertos = self._repository.list_by_escritorio(
                escritorio_id=escritorio_id,
                status=StatusTitulo.ABERTO,
                skip=0,
                limit=10000,
            )
        vencido_receber = Decimal("0")
        vencido_pagar = Decimal("0")
        for t in titulos_abertos:
            if t.data_vencimento < hoje:
                if t.tipo == TipoTitulo.RECEBER:
                    vencido_receber += t.valor
                else:
                    vencido_pagar += t.valor

        return ResumoFinanceiroDTO(
            a_receber=a_receber,
            a_pagar=a_pagar,
            recebido=recebido,
            pago=pago,
            vencido_receber=vencido_receber,
            vencido_pagar=vencido_pagar,
        )
