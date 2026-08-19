"""Repository concreto de PlanoConta persistido em SQLite via SQLAlchemy."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from application.ports.plano_conta_repository import PlanoContaRepository
from domain.entities.plano_conta import PlanoConta
from domain.enums.tipo_plano_conta import TipoPlanoConta
from infrastructure.database.models.plano_conta_model import PlanoContaModel


def _para_model(plano: PlanoConta) -> PlanoContaModel:
    """Converte entidade PlanoConta para o model ORM."""
    return PlanoContaModel(
        id=plano.id,
        escritorio_id=plano.escritorio_id,
        codigo=plano.codigo,
        nome=plano.nome,
        tipo=plano.tipo.value,
        nivel=plano.nivel,
        pai_id=plano.pai_id,
    )


def _para_entidade(model: PlanoContaModel) -> PlanoConta:
    """Converte model ORM para a entidade PlanoConta."""
    return PlanoConta(
        id=model.id,
        escritorio_id=model.escritorio_id,
        codigo=model.codigo,
        nome=model.nome,
        tipo=TipoPlanoConta(model.tipo),
        nivel=model.nivel,
        pai_id=model.pai_id,
    )


class SQLitePlanoContaRepository(PlanoContaRepository):
    """Repositorio de plano de contas sobre banco SQLite."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create(self, plano: PlanoConta) -> PlanoConta:
        with self._session_factory() as session:
            model = _para_model(plano)
            session.add(model)
            session.commit()
            session.refresh(model)
            return _para_entidade(model)

    def get_by_id(self, id: int) -> PlanoConta | None:
        with self._session_factory() as session:
            model = session.get(PlanoContaModel, id)
            return _para_entidade(model) if model is not None else None

    def update(self, plano: PlanoConta) -> PlanoConta:
        if plano.id is None:
            raise ValueError("ID do plano de conta nao pode ser None para atualizacao.")

        with self._session_factory() as session:
            model = session.get(PlanoContaModel, plano.id)
            if model is None:
                raise ValueError(
                    f"Plano de conta com ID {plano.id} não encontrado para atualizacao."
                )

            model.escritorio_id = plano.escritorio_id
            model.codigo = plano.codigo
            model.nome = plano.nome
            model.tipo = plano.tipo.value
            model.nivel = plano.nivel
            model.pai_id = plano.pai_id

            session.commit()
            session.refresh(model)
            return _para_entidade(model)

    def delete(self, id: int) -> None:
        with self._session_factory() as session:
            model = session.get(PlanoContaModel, id)
            if model is not None:
                session.delete(model)
                session.commit()

    def list_by_escritorio(
        self, escritorio_id: int, skip: int = 0, limit: int = 100
    ) -> list[PlanoConta]:
        with self._session_factory() as session:
            stmt = (
                select(PlanoContaModel)
                .where(PlanoContaModel.escritorio_id == escritorio_id)
                .order_by(PlanoContaModel.codigo)
                .offset(skip)
                .limit(limit)
            )
            models = session.scalars(stmt).all()
            return [_para_entidade(m) for m in models]

    def get_by_codigo(
        self, escritorio_id: int, codigo: str
    ) -> PlanoConta | None:
        with self._session_factory() as session:
            stmt = select(PlanoContaModel).where(
                PlanoContaModel.escritorio_id == escritorio_id,
                PlanoContaModel.codigo == codigo,
            )
            model = session.scalars(stmt).first()
            return _para_entidade(model) if model is not None else None
