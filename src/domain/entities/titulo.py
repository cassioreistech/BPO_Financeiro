"""Entidade Titulo — contas a pagar e a receber."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from domain.enums.status_titulo import StatusTitulo
from domain.enums.tipo_titulo import TipoTitulo


@dataclass
class Titulo:
    """Título financeiro vinculado a um escritório.

    Atributos:
        id: identificador unico (None antes de persistir)
        escritorio_id: FK para o escritorio
        empresa_id: FK para a empresa (opcional)
        plano_conta_id: FK para o plano de contas
        centro_custo_id: FK para o centro de custo (opcional)
        descricao: descricao do titulo
        tipo: PAGAR ou RECEBER
        status: ABERTO, PAGO ou CANCELADO
        valor: valor monetario do titulo
        data_emissao: data de emissao
        data_vencimento: data de vencimento
        data_quitacao: data de quitacao (None se nao quitado)
        observacao: observacoes extras (opcional)
    """

    escritorio_id: int
    plano_conta_id: int
    descricao: str
    tipo: TipoTitulo
    status: StatusTitulo
    valor: Decimal
    data_emissao: date
    data_vencimento: date
    id: int | None = None
    empresa_id: int | None = None
    centro_custo_id: int | None = None
    data_quitacao: date | None = None
    observacao: str | None = None

    def __post_init__(self) -> None:
        if self.escritorio_id <= 0:
            raise ValueError("Escritorio ID deve ser um numero positivo.")
        if self.plano_conta_id <= 0:
            raise ValueError("Plano de Conta ID deve ser um numero positivo.")
        if self.empresa_id is not None and self.empresa_id <= 0:
            raise ValueError("Empresa ID deve ser um numero positivo.")
        if self.centro_custo_id is not None and self.centro_custo_id <= 0:
            raise ValueError("Centro de Custo ID deve ser um numero positivo.")
        if not self.descricao or not self.descricao.strip():
            raise ValueError("Descricao do titulo nao pode ser vazia.")
        if self.valor <= Decimal("0"):
            raise ValueError("Valor do titulo deve ser maior que zero.")
        if self.data_vencimento < self.data_emissao:
            raise ValueError("Data de vencimento nao pode ser anterior a data de emissao.")

        object.__setattr__(self, "descricao", self.descricao.strip())
        if self.observacao:
            object.__setattr__(self, "observacao", self.observacao.strip() or None)
