"""Infraestrutura de banco de dados (SQLite via SQLAlchemy 2.x)."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
DATABASE_PATH = DATA_DIR / "bpo.db"

engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base declarativa para as entidades do dominio."""


def init_db() -> None:
    """Garante o diretorio de dados e cria o schema conhecido pelos models."""
    # Importacao registra os models no metadata do Base antes do create_all.
    from infrastructure.database.models import (  # noqa: F401
        ContaBancariaModel,
        ContadorModel,
        EmpresaModel,
        EscritorioModel,
    )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
