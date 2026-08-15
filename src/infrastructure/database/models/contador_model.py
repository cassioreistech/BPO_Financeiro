"""Modelo ORM da entidade Contador."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database import Base


class ContadorModel(Base):
    """Persistencia do contador na tabela ``contadores``."""

    __tablename__ = "contadores"

    id: Mapped[int] = mapped_column(primary_key=True)
    escritorio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("escritorios.id"), nullable=False
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    crc: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
