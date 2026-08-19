"""Repository concreto de Contador persistido em SQLite via SQLAlchemy."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from application.ports.contador_repository import ContadorRepository
from domain.entities.contador import Contador
from domain.value_objects.crc import CRC
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone
from infrastructure.database.models.contador_model import ContadorModel


def _para_model(contador: Contador) -> ContadorModel:
    """Converte entidade Contador para o model ORM."""
    return ContadorModel(
        id=contador.id,
        escritorio_id=contador.escritorio_id,
        nome=contador.nome,
        crc=str(contador.crc) if contador.crc else None,
        email=str(contador.email) if contador.email else None,
        telefone=str(contador.telefone) if contador.telefone else None,
    )


def _para_entidade(model: ContadorModel) -> Contador:
    """Converte model ORM para a entidade Contador."""
    return Contador(
        id=model.id,
        escritorio_id=model.escritorio_id,
        nome=model.nome,
        crc=CRC(model.crc) if model.crc else None,
        email=Email(model.email) if model.email else None,
        telefone=Telefone(model.telefone) if model.telefone else None,
    )


class SQLiteContadorRepository(ContadorRepository):
    """Repositorio de contadores sobre banco SQLite."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create(self, contador: Contador) -> Contador:
        with self._session_factory() as session:
            model = _para_model(contador)
            session.add(model)
            session.commit()
            session.refresh(model)
            return _para_entidade(model)

    def get_by_id(self, id: int) -> Contador | None:
        with self._session_factory() as session:
            model = session.get(ContadorModel, id)
            return _para_entidade(model) if model is not None else None

    def update(self, contador: Contador) -> Contador:
        if contador.id is None:
            raise ValueError("ID do contador nao pode ser None para atualizacao.")

        with self._session_factory() as session:
            model = session.get(ContadorModel, contador.id)
            if model is None:
                raise ValueError(
                    f"Contador com ID {contador.id} não encontrado para atualizacao."
                )

            model.escritorio_id = contador.escritorio_id
            model.nome = contador.nome
            model.crc = str(contador.crc) if contador.crc else None
            model.email = str(contador.email) if contador.email else None
            model.telefone = str(contador.telefone) if contador.telefone else None

            session.commit()
            session.refresh(model)
            return _para_entidade(model)

    def delete(self, id: int) -> None:
        with self._session_factory() as session:
            model = session.get(ContadorModel, id)
            if model is not None:
                session.delete(model)
                session.commit()

    def list_all(
        self, escritorio_id: int | None = None, skip: int = 0, limit: int = 100
    ) -> list[Contador]:
        with self._session_factory() as session:
            stmt = select(ContadorModel)
            if escritorio_id is not None:
                stmt = stmt.where(ContadorModel.escritorio_id == escritorio_id)
            stmt = stmt.order_by(ContadorModel.id).offset(skip).limit(limit)
            models = session.scalars(stmt).all()
            return [_para_entidade(m) for m in models]
