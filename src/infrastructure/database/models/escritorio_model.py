"""Modelo ORM da entidade Escritorio."""

from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database import Base


class EscritorioModel(Base):
    """Persistencia do escritorio contabil na tabela ``escritorios``."""

    __tablename__ = "escritorios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    cnpj_cpf: Mapped[str] = mapped_column(String(14), nullable=False, unique=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefone: Mapped[str | None] = mapped_column(String(20), nullable=True)
