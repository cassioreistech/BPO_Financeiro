"""Modelo ORM da entidade Empresa."""

from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database import Base


class EmpresaModel(Base):
    """Persistencia da empresa cliente na tabela ``empresas``."""

    __tablename__ = "empresas"

    id: Mapped[int] = mapped_column(primary_key=True)
    escritorio_id: Mapped[int] = mapped_column(
        ForeignKey("escritorios.id"),
        nullable=False,
    )
    contador_id: Mapped[int | None] = mapped_column(nullable=True)
    cnpj: Mapped[str] = mapped_column(String(14), nullable=False, unique=True)
    razao_social: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_fantasia: Mapped[str] = mapped_column(String(255), nullable=False)
    regime_tributario: Mapped[str] = mapped_column(String(20), nullable=False)
    email_financeiro: Mapped[str | None] = mapped_column(String(255), nullable=True)
    telefone_financeiro: Mapped[str | None] = mapped_column(String(20), nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
