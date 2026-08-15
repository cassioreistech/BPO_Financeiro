"""Repository concreto de Titulo persistido em SQLite via SQLAlchemy."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from application.ports.titulo_repository import TituloRepository
from domain.entities.titulo import Titulo
from domain.enums.status_titulo import StatusTitulo
from domain.enums.tipo_titulo import TipoTitulo
from infrastructure.database.models.titulo_model import TituloModel


def _para_model(titulo: Titulo) -> TituloModel:
    """Converte entidade Titulo para o model ORM."""
    return TituloModel(
        id=titulo.id,
        escritorio_id=titulo.escritorio_id,
        empresa_id=titulo.empresa_id,
        plano_conta_id=titulo.plano_conta_id,
        centro_custo_id=titulo.centro_custo_id,
        descricao=titulo.descricao,
        tipo=titulo.tipo.value,
        status=titulo.status.value,
        valor=titulo.valor,
        data_emissao=titulo.data_emissao,
        data_vencimento=titulo.data_vencimento,
        data_quitacao=titulo.data_quitacao,
        observacao=titulo.observacao,
    )


def _para_entidade(model: TituloModel) -> Titulo:
    """Converte model ORM para a entidade Titulo."""
    return Titulo(
        id=model.id,
        escritorio_id=model.escritorio_id,
        empresa_id=model.empresa_id,
        plano_conta_id=model.plano_conta_id,
        centro_custo_id=model.centro_custo_id,
        descricao=model.descricao,
        tipo=TipoTitulo(model.tipo),
        status=StatusTitulo(model.status),
        valor=model.valor,
        data_emissao=model.data_emissao,
        data_vencimento=model.data_vencimento,
        data_quitacao=model.data_quitacao,
        observacao=model.observacao,
    )


class SQLiteTituloRepository(TituloRepository):
    """Repositorio de titulos financeiros sobre banco SQLite."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create(self, titulo: Titulo) -> Titulo:
        with self._session_factory() as session:
            model = _para_model(titulo)
            session.add(model)
            session.commit()
            session.refresh(model)
            return _para_entidade(model)

    def get_by_id(self, id: int) -> Titulo | None:
        with self._session_factory() as session:
            model = session.get(TituloModel, id)
            return _para_entidade(model) if model is not None else None

    def update(self, titulo: Titulo) -> Titulo:
        if titulo.id is None:
            raise ValueError("ID do titulo nao pode ser None para atualizacao.")

        with self._session_factory() as session:
            model = session.get(TituloModel, titulo.id)
            if model is None:
                raise ValueError(
                    f"Titulo com ID {titulo.id} nao encontrado para atualizacao."
                )

            model.escritorio_id = titulo.escritorio_id
            model.empresa_id = titulo.empresa_id
            model.plano_conta_id = titulo.plano_conta_id
            model.centro_custo_id = titulo.centro_custo_id
            model.descricao = titulo.descricao
            model.tipo = titulo.tipo.value
            model.status = titulo.status.value
            model.valor = titulo.valor
            model.data_emissao = titulo.data_emissao
            model.data_vencimento = titulo.data_vencimento
            model.data_quitacao = titulo.data_quitacao
            model.observacao = titulo.observacao

            session.commit()
            session.refresh(model)
            return _para_entidade(model)

    def delete(self, id: int) -> None:
        with self._session_factory() as session:
            model = session.get(TituloModel, id)
            if model is not None:
                session.delete(model)
                session.commit()

    def list_by_escritorio(
        self,
        escritorio_id: int,
        empresa_id: int | None = None,
        tipo: TipoTitulo | None = None,
        status: StatusTitulo | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Titulo]:
        with self._session_factory() as session:
            stmt = select(TituloModel).where(
                TituloModel.escritorio_id == escritorio_id
            )
            if empresa_id is not None:
                stmt = stmt.where(TituloModel.empresa_id == empresa_id)
            if tipo is not None:
                stmt = stmt.where(TituloModel.tipo == tipo.value)
            if status is not None:
                stmt = stmt.where(TituloModel.status == status.value)
            stmt = (
                stmt.order_by(TituloModel.data_vencimento, TituloModel.descricao)
                .offset(skip)
                .limit(limit)
            )
            models = session.scalars(stmt).all()
            return [_para_entidade(m) for m in models]

    def total_por_status(
        self,
        escritorio_id: int,
        status: StatusTitulo,
        tipo: TipoTitulo | None = None,
    ) -> Decimal:
        with self._session_factory() as session:
            stmt = select(func.coalesce(func.sum(TituloModel.valor), Decimal("0"))).where(
                TituloModel.escritorio_id == escritorio_id,
                TituloModel.status == status.value,
            )
            if tipo is not None:
                stmt = stmt.where(TituloModel.tipo == tipo.value)
            resultado = session.scalar(stmt)
            return Decimal(resultado) if resultado is not None else Decimal("0")
