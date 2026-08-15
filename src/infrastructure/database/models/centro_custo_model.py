"""Modelo ORM da entidade CentroCusto."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database import Base


class CentroCustoModel(Base):
    """Persistencia do centro de custo na tabela ``centros_custo``."""

    __tablename__ = "centros_custo"

    id: Mapped[int] = mapped_column(primary_key=True)
    empresa_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("empresas.id"), nullable=False
    )
    codigo: Mapped[str] = mapped_column(String(50), nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
