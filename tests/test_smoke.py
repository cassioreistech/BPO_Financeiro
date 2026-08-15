"""Testes basicos da fundacao do sistema."""

from sqlalchemy import create_engine

from infrastructure import database as db
from infrastructure.database import Base


def test_imports_das_camadas() -> None:
    """Verifica que os pacotes importam com imports flat (sem prefixo src.)."""
    import application  # noqa: F401
    import domain  # noqa: F401
    import infrastructure  # noqa: F401
    import ui  # noqa: F401


def test_base_declarativa_cria_schema_in_memory() -> None:
    """Verifica que o Base declarativo cria tabelas em banco em memoria."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    assert Base is db.Base
