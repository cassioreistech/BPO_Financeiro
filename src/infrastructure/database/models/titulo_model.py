"""Modelo ORM da entidade Titulo."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database import Base


class TituloModel(Base):
    """Persistencia do titulo financeiro na tabela ``titulos``."""

    __tablename__ = "titulos"

    __table_args__ = (
        CheckConstraint(
            "tipo IN ('PAGAR', 'RECEBER')",
            name="ck_titulos_tipo",
        ),
        CheckConstraint(
            "status IN ('ABERTO', 'PAGO', 'CANCELADO')",
            name="ck_titulos_status",
        ),
        CheckConstraint(
            "categoria IN ('BOLETO', 'IMPOSTO', 'SALARIO', 'VENDA', "
            "'SERVICO', 'OUTRO')",
            name="ck_titulos_categoria",
        ),
        CheckConstraint(
            "forma_pagamento IN ('DINHEIRO', 'PIX', 'BOLETO', "
            "'TRANSFERENCIA', 'CARTAO_CREDITO', 'CARTAO_DEBITO', "
            "'CHEQUE', 'OUTRO')",
            name="ck_titulos_forma_pagamento",
        ),
        CheckConstraint("valor > 0", name="ck_titulos_valor_maior_zero"),
        CheckConstraint(
            "valor_pago IS NULL OR valor_pago >= 0",
            name="ck_titulos_valor_pago",
        ),
        CheckConstraint(
            "data_vencimento >= data_emissao",
            name="ck_titulos_data_vencimento",
        ),
        CheckConstraint(
            "data_quitacao IS NULL OR data_quitacao >= data_emissao",
            name="ck_titulos_data_quitacao",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    escritorio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("escritorios.id", ondelete="RESTRICT"), nullable=False
    )
    empresa_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("empresas.id", ondelete="SET NULL"), nullable=True
    )
    plano_conta_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("plano_contas.id", ondelete="RESTRICT"),
        nullable=False,
    )
    centro_custo_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("centros_custo.id", ondelete="SET NULL"),
        nullable=True,
    )
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(15), nullable=False, default="ABERTO")
    valor: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False
    )
    data_emissao: Mapped[date] = mapped_column(Date, nullable=False)
    data_vencimento: Mapped[date] = mapped_column(Date, nullable=False)
    data_quitacao: Mapped[date | None] = mapped_column(Date, nullable=True)
    observacao: Mapped[str | None] = mapped_column(String(500), nullable=True)
    numero_documento: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    codigo_barras: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    categoria: Mapped[str] = mapped_column(
        String(20), nullable=False, default="OUTRO"
    )
    valor_pago: Mapped[Decimal | None] = mapped_column(
        Numeric(15, 2), nullable=True
    )
    conta_bancaria_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("contas_bancarias.id", ondelete="SET NULL"),
        nullable=True,
    )
    forma_pagamento: Mapped[str] = mapped_column(
        String(20), nullable=False, default="OUTRO"
    )
    observacao_quitacao: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    emitente: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
