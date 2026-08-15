"""Use cases para dashboard financeiro."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from application.ports.titulo_repository import TituloRepository
from domain.entities.titulo import Titulo
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
    total_mes_receber: Decimal
    total_mes_pagar: Decimal


@dataclass(frozen=True)
class ResumoCategoriaDTO:
    """DTO com totais por categoria."""

    categoria: str
    total: Decimal


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
        inicio_mes = date(hoje.year, hoje.month, 1)
        fim_mes = self._ultimo_dia_mes(hoje)

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
        total_mes_receber = Decimal("0")
        total_mes_pagar = Decimal("0")
        for t in titulos_abertos:
            if t.data_vencimento < hoje:
                if t.tipo == TipoTitulo.RECEBER:
                    vencido_receber += t.valor
                else:
                    vencido_pagar += t.valor
            if inicio_mes <= t.data_vencimento <= fim_mes:
                if t.tipo == TipoTitulo.RECEBER:
                    total_mes_receber += t.valor
                else:
                    total_mes_pagar += t.valor

        return ResumoFinanceiroDTO(
            a_receber=a_receber,
            a_pagar=a_pagar,
            recebido=recebido,
            pago=pago,
            vencido_receber=vencido_receber,
            vencido_pagar=vencido_pagar,
            total_mes_receber=total_mes_receber,
            total_mes_pagar=total_mes_pagar,
        )

    def resumo_por_categoria(
        self, escritorio_id: int, empresa_id: int | None = None
    ) -> list[ResumoCategoriaDTO]:
        """Retorna o total em aberto por categoria.

        Raises:
            ValueError: se escritorio_id invalido.
        """
        if escritorio_id <= 0:
            raise ValueError("Escritorio ID deve ser um numero positivo.")

        if empresa_id is not None:
            titulos = self._repository.list_by_escritorio(
                escritorio_id=escritorio_id,
                empresa_id=empresa_id,
                status=StatusTitulo.ABERTO,
                skip=0,
                limit=10000,
            )
        else:
            titulos = self._repository.list_by_escritorio(
                escritorio_id=escritorio_id,
                status=StatusTitulo.ABERTO,
                skip=0,
                limit=10000,
            )

        totais: dict[str, Decimal] = {}
        for t in titulos:
            cat = t.categoria.value
            totais[cat] = totais.get(cat, Decimal("0")) + t.valor

        return [
            ResumoCategoriaDTO(categoria=cat, total=total)
            for cat, total in sorted(totais.items(), key=lambda x: x[1], reverse=True)
        ]

    def titulos_vencidos(
        self,
        escritorio_id: int,
        empresa_id: int | None = None,
        limite: int = 10,
    ) -> list[Titulo]:
        """Retorna os titulos abertos vencidos ordenados por data de vencimento.

        Raises:
            ValueError: se escritorio_id invalido.
        """
        if escritorio_id <= 0:
            raise ValueError("Escritorio ID deve ser um numero positivo.")

        if empresa_id is not None:
            titulos = self._repository.list_by_escritorio(
                escritorio_id=escritorio_id,
                empresa_id=empresa_id,
                status=StatusTitulo.ABERTO,
                skip=0,
                limit=10000,
            )
        else:
            titulos = self._repository.list_by_escritorio(
                escritorio_id=escritorio_id,
                status=StatusTitulo.ABERTO,
                skip=0,
                limit=10000,
            )

        hoje = date.today()
        vencidos = [t for t in titulos if t.data_vencimento < hoje]
        return sorted(vencidos, key=lambda t: t.data_vencimento)[:limite]

    @staticmethod
    def _ultimo_dia_mes(data: date) -> date:
        import calendar

        dia = calendar.monthrange(data.year, data.month)[1]
        return date(data.year, data.month, dia)
