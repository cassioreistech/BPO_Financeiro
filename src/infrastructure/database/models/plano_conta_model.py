"""Modelo ORM da entidade PlanoConta."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database import Base


class PlanoContaModel(Base):
    """Persistencia do plano de conta na tabela ``plano_contas``."""

    __tablename__ = "plano_contas"

    id: Mapped[int] = mapped_column(primary_key=True)
    escritorio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("escritorios.id"), nullable=False
    )
    codigo: Mapped[str] = mapped_column(String(50), nullable=False)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    nivel: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    pai_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("plano_contas.id"), nullable=True
    )
