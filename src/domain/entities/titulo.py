"""Entidade Titulo — contas a pagar e a receber."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from domain.enums.categoria_titulo import CategoriaTitulo
from domain.enums.forma_pagamento import FormaPagamento
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
        numero_documento: numero do boleto, nota fiscal etc. (opcional)
        codigo_barras: codigo de barras do boleto (opcional)
        categoria: categoria simplificada do titulo
        descricao: descricao do titulo
        tipo: PAGAR ou RECEBER
        status: ABERTO, PAGO ou CANCELADO
        valor: valor monetario original do titulo
        valor_pago: valor efetivamente pago/recebido na quitacao
        data_emissao: data de emissao
        data_vencimento: data de vencimento
        data_quitacao: data de quitacao (None se nao quitado)
        conta_bancaria_id: conta bancaria utilizada na quitacao (opcional)
        forma_pagamento: forma de pagamento/recebimento da quitacao
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
    numero_documento: str | None = None
    codigo_barras: str | None = None
    categoria: CategoriaTitulo = CategoriaTitulo.OUTRO
    valor_pago: Decimal | None = None
    data_quitacao: date | None = None
    conta_bancaria_id: int | None = None
    forma_pagamento: FormaPagamento = FormaPagamento.OUTRO
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
        if self.valor_pago is not None and self.valor_pago < Decimal("0"):
            raise ValueError("Valor pago nao pode ser negativo.")
        if self.conta_bancaria_id is not None and self.conta_bancaria_id <= 0:
            raise ValueError("Conta bancaria ID deve ser um numero positivo.")

        object.__setattr__(self, "descricao", self.descricao.strip())
        if self.numero_documento:
            object.__setattr__(
                self, "numero_documento", self.numero_documento.strip() or None
            )
        if self.codigo_barras:
            object.__setattr__(
                self, "codigo_barras", self.codigo_barras.strip() or None
            )
        if self.observacao:
            object.__setattr__(self, "observacao", self.observacao.strip() or None)
