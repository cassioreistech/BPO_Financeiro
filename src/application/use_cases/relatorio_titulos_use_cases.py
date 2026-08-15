"""Use cases para geracao de relatorios de titulos."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from application.ports.titulo_repository import TituloRepository
from domain.entities.titulo import Titulo
from domain.enums.status_titulo import StatusTitulo
from domain.enums.tipo_titulo import TipoTitulo


@dataclass(frozen=True)
class ItemFluxoCaixaDTO:
    """Item do fluxo de caixa em um dia."""

    data: date
    entradas: Decimal
    saidas: Decimal
    saldo_dia: Decimal


@dataclass(frozen=True)
class ProjecaoFinanceiraDTO:
    """Projecao de saldo acumulado dia a dia."""

    data: date
    saldo_acumulado: Decimal


@dataclass(frozen=True)
class RelatorioTitulosDTO:
    """Dados para o relatorio de titulos."""

    titulos: list[Titulo]
    total_receber: Decimal
    total_pagar: Decimal
    total_pago: Decimal
    total_recebido: Decimal


class RelatorioTitulosUseCase:
    """Use case que prepara dados para relatorios de titulos."""

    def __init__(self, repository: TituloRepository) -> None:
        self._repository = repository

    def execute(
        self,
        escritorio_id: int,
        empresa_id: int | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
    ) -> RelatorioTitulosDTO:
        """Obtem dados para o relatorio de titulos.

        Args:
            escritorio_id: ID do escritorio.
            empresa_id: filtro opcional por empresa.
            data_inicio: filtro opcional de data de vencimento inicial.
            data_fim: filtro opcional de data de vencimento final.

        Raises:
            ValueError: se escritorio_id invalido.
        """
        if escritorio_id <= 0:
            raise ValueError("Escritorio ID deve ser um numero positivo.")

        titulos = self._repository.list_by_escritorio(
            escritorio_id=escritorio_id,
            empresa_id=empresa_id,
            skip=0,
            limit=10000,
        )

        if data_inicio is not None:
            titulos = [
                t for t in titulos if t.data_vencimento >= data_inicio
            ]
        if data_fim is not None:
            titulos = [t for t in titulos if t.data_vencimento <= data_fim]

        total_receber = Decimal("0")
        total_pagar = Decimal("0")
        total_pago = Decimal("0")
        total_recebido = Decimal("0")

        for t in titulos:
            if t.tipo == TipoTitulo.RECEBER:
                if t.status == StatusTitulo.PAGO:
                    total_recebido += t.valor_pago or t.valor
                elif t.status == StatusTitulo.ABERTO:
                    total_receber += t.valor
            else:
                if t.status == StatusTitulo.PAGO:
                    total_pago += t.valor_pago or t.valor
                elif t.status == StatusTitulo.ABERTO:
                    total_pagar += t.valor

        return RelatorioTitulosDTO(
            titulos=titulos,
            total_receber=total_receber,
            total_pagar=total_pagar,
            total_pago=total_pago,
            total_recebido=total_recebido,
        )


class FluxoCaixaUseCase:
    """Use case que calcula o fluxo de caixa por dia."""

    def __init__(self, repository: TituloRepository) -> None:
        self._repository = repository

    def execute(
        self,
        escritorio_id: int,
        data_inicio: date,
        data_fim: date,
        empresa_id: int | None = None,
    ) -> list[ItemFluxoCaixaDTO]:
        """Calcula entradas e saidas por dia no periodo.

        Considera titulos pagos/recebidos ou em aberto no periodo.

        Raises:
            ValueError: se escritorio_id invalido ou data_fim anterior a data_inicio.
        """
        if escritorio_id <= 0:
            raise ValueError("Escritorio ID deve ser um numero positivo.")
        if data_fim < data_inicio:
            raise ValueError("Data final nao pode ser anterior a data inicial.")

        titulos = self._repository.list_by_escritorio(
            escritorio_id=escritorio_id,
            empresa_id=empresa_id,
            skip=0,
            limit=10000,
        )

        dias: dict[date, tuple[Decimal, Decimal]] = {}
        dia_atual = data_inicio
        while dia_atual <= data_fim:
            dias[dia_atual] = (Decimal("0"), Decimal("0"))
            dia_atual = date.fromordinal(dia_atual.toordinal() + 1)

        for t in titulos:
            if t.status == StatusTitulo.CANCELADO:
                continue
            dia = t.data_vencimento
            if not (data_inicio <= dia <= data_fim):
                continue
            entradas, saidas = dias.get(dia, (Decimal("0"), Decimal("0")))
            if t.status == StatusTitulo.PAGO:
                valor = t.valor_pago if t.valor_pago is not None else t.valor
            else:
                valor = t.valor
            if t.tipo == TipoTitulo.RECEBER:
                entradas += valor
            else:
                saidas += valor
            dias[dia] = (entradas, saidas)

        return [
            ItemFluxoCaixaDTO(
                data=d,
                entradas=e,
                saidas=s,
                saldo_dia=e - s,
            )
            for d, (e, s) in sorted(dias.items())
        ]


class ProjecaoFinanceiraUseCase:
    """Use case que projeta o saldo acumulado dia a dia."""

    def __init__(self, repository: TituloRepository) -> None:
        self._repository = repository

    def execute(
        self,
        escritorio_id: int,
        data_inicio: date,
        data_fim: date,
        saldo_inicial: Decimal = Decimal("0"),
        empresa_id: int | None = None,
    ) -> list[ProjecaoFinanceiraDTO]:
        """Projeta saldo acumulado considerando titulos em aberto e pagos.

        Raises:
            ValueError: se escritorio_id invalido ou data_fim anterior a data_inicio.
        """
        if escritorio_id <= 0:
            raise ValueError("Escritorio ID deve ser um numero positivo.")
        if data_fim < data_inicio:
            raise ValueError("Data final nao pode ser anterior a data inicial.")

        fluxo = FluxoCaixaUseCase(self._repository).execute(
            escritorio_id=escritorio_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            empresa_id=empresa_id,
        )

        saldo = saldo_inicial
        projecao: list[ProjecaoFinanceiraDTO] = []
        for item in fluxo:
            saldo += item.saldo_dia
            projecao.append(
                ProjecaoFinanceiraDTO(
                    data=item.data,
                    saldo_acumulado=saldo,
                )
            )

        return projecao
