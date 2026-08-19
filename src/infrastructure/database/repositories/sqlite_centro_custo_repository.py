"""Repository concreto de CentroCusto persistido em SQLite via SQLAlchemy."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from application.ports.centro_custo_repository import CentroCustoRepository
from domain.entities.centro_custo import CentroCusto
from infrastructure.database.models.centro_custo_model import CentroCustoModel


def _para_model(centro: CentroCusto) -> CentroCustoModel:
    """Converte entidade CentroCusto para o model ORM."""
    return CentroCustoModel(
        id=centro.id,
        empresa_id=centro.empresa_id,
        codigo=centro.codigo,
        nome=centro.nome,
        ativo=centro.ativo,
    )


def _para_entidade(model: CentroCustoModel) -> CentroCusto:
    """Converte model ORM para a entidade CentroCusto."""
    return CentroCusto(
        id=model.id,
        empresa_id=model.empresa_id,
        codigo=model.codigo,
        nome=model.nome,
        ativo=model.ativo,
    )


class SQLiteCentroCustoRepository(CentroCustoRepository):
    """Repositorio de centros de custo sobre banco SQLite."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create(self, centro: CentroCusto) -> CentroCusto:
        with self._session_factory() as session:
            model = _para_model(centro)
            session.add(model)
            session.commit()
            session.refresh(model)
            return _para_entidade(model)

    def get_by_id(self, id: int) -> CentroCusto | None:
        with self._session_factory() as session:
            model = session.get(CentroCustoModel, id)
            return _para_entidade(model) if model is not None else None

    def update(self, centro: CentroCusto) -> CentroCusto:
        if centro.id is None:
            raise ValueError("ID do centro de custo nao pode ser None para atualizacao.")

        with self._session_factory() as session:
            model = session.get(CentroCustoModel, centro.id)
            if model is None:
                raise ValueError(
                    f"Centro de custo com ID {centro.id} não encontrado para atualizacao."
                )

            model.empresa_id = centro.empresa_id
            model.codigo = centro.codigo
            model.nome = centro.nome
            model.ativo = centro.ativo

            session.commit()
            session.refresh(model)
            return _para_entidade(model)

    def delete(self, id: int) -> None:
        with self._session_factory() as session:
            model = session.get(CentroCustoModel, id)
            if model is not None:
                session.delete(model)
                session.commit()

    def list_by_empresa(
        self,
        empresa_id: int,
        ativo: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[CentroCusto]:
        with self._session_factory() as session:
            stmt = select(CentroCustoModel).where(
                CentroCustoModel.empresa_id == empresa_id
            )
            if ativo is not None:
                stmt = stmt.where(CentroCustoModel.ativo == ativo)
            stmt = stmt.order_by(CentroCustoModel.codigo).offset(skip).limit(limit)
            models = session.scalars(stmt).all()
            return [_para_entidade(m) for m in models]

    def get_by_codigo(
        self, empresa_id: int, codigo: str
    ) -> CentroCusto | None:
        with self._session_factory() as session:
            stmt = select(CentroCustoModel).where(
                CentroCustoModel.empresa_id == empresa_id,
                CentroCustoModel.codigo == codigo,
            )
            model = session.scalars(stmt).first()
            return _para_entidade(model) if model is not None else None
