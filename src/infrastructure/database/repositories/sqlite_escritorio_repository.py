"""Repository concreto de Escritorio persistido em SQLite via SQLAlchemy."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from application.ports.escritorio_repository import EscritorioRepository
from domain.entities.escritorio import Escritorio
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone
from infrastructure.database.models.escritorio_model import EscritorioModel


def _para_model(escritorio: Escritorio) -> EscritorioModel:
    """Converte entidade Escritorio para o model ORM."""
    return EscritorioModel(
        id=escritorio.id,
        nome=escritorio.nome,
        cnpj_cpf=escritorio.cnpj_cpf,
        email=str(escritorio.email) if escritorio.email else None,
        telefone=str(escritorio.telefone) if escritorio.telefone else None,
    )


def _para_entidade(model: EscritorioModel) -> Escritorio:
    """Converte model ORM para a entidade Escritorio."""
    return Escritorio(
        id=model.id,
        nome=model.nome,
        cnpj_cpf=model.cnpj_cpf,
        email=Email(model.email) if model.email else None,
        telefone=Telefone(model.telefone) if model.telefone else None,
    )


class SQLiteEscritorioRepository(EscritorioRepository):
    """Repositorio de escritorios sobre banco SQLite.

    Cada operacao abre e fecha a propria sessao, mantendo o ciclo de vida
    previsivel e isolado para a camada de application.
    """

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create(self, escritorio: Escritorio) -> Escritorio:
        with self._session_factory() as session:
            model = _para_model(escritorio)
            session.add(model)
            session.commit()
            session.refresh(model)
            return _para_entidade(model)

    def get_by_id(self, id: int) -> Escritorio | None:
        with self._session_factory() as session:
            model = session.get(EscritorioModel, id)
            return _para_entidade(model) if model is not None else None

    def get_by_cnpj(self, cnpj: str) -> Escritorio | None:
        with self._session_factory() as session:
            stmt = select(EscritorioModel).where(EscritorioModel.cnpj_cpf == cnpj)
            model = session.scalars(stmt).first()
            return _para_entidade(model) if model is not None else None

    def update(self, escritorio: Escritorio) -> Escritorio:
        if escritorio.id is None:
            raise ValueError("ID do escritorio nao pode ser None para atualizacao.")

        with self._session_factory() as session:
            model = session.get(EscritorioModel, escritorio.id)
            if model is None:
                raise ValueError(
                    f"Escritorio com ID {escritorio.id} não encontrado para atualizacao."
                )

            model.nome = escritorio.nome
            model.cnpj_cpf = escritorio.cnpj_cpf
            model.email = str(escritorio.email) if escritorio.email else None
            model.telefone = str(escritorio.telefone) if escritorio.telefone else None

            session.commit()
            session.refresh(model)
            return _para_entidade(model)

    def delete(self, id: int) -> None:
        with self._session_factory() as session:
            model = session.get(EscritorioModel, id)
            if model is not None:
                session.delete(model)
                session.commit()

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Escritorio]:
        with self._session_factory() as session:
            stmt = select(EscritorioModel).order_by(EscritorioModel.id).offset(skip).limit(limit)
            models = session.scalars(stmt).all()
            return [_para_entidade(m) for m in models]
