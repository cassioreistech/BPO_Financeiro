"""Modelo ORM da entidade ContaBancaria."""

from __future__ import annotations

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database import Base


class ContaBancariaModel(Base):
    """Persistencia da conta bancaria na tabela ``contas_bancarias``."""

    __tablename__ = "contas_bancarias"

    __table_args__ = (
        CheckConstraint(
            "tipo IN ('CORRENTE', 'POUPANCA', 'OUTRO')",
            name="ck_contas_bancarias_tipo",
        ),
        UniqueConstraint(
            "empresa_id", "banco_codigo", "agencia", "conta",
            name="uq_contas_bancarias_dados_unicos",
        ),
        Index(
            "ix_contas_bancarias_empresa_ativo",
            "empresa_id",
            "ativo",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    empresa_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("empresas.id", ondelete="CASCADE"), nullable=False
    )
    banco_nome: Mapped[str] = mapped_column(String(100), nullable=False)
    banco_codigo: Mapped[str | None] = mapped_column(String(3), nullable=True)
    agencia: Mapped[str] = mapped_column(String(20), nullable=False)
    conta: Mapped[str] = mapped_column(String(30), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
