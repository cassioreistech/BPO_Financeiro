"""Repository concreto de ContaBancaria persistido em SQLite via SQLAlchemy."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from application.ports.conta_bancaria_repository import ContaBancariaRepository
from domain.entities.conta_bancaria import ContaBancaria
from domain.enums.tipo_conta_bancaria import TipoContaBancaria
from domain.value_objects.banco_codigo import BancoCodigo
from infrastructure.database.models.conta_bancaria_model import ContaBancariaModel


def _para_model(conta: ContaBancaria) -> ContaBancariaModel:
    """Converte entidade ContaBancaria para o model ORM."""
    return ContaBancariaModel(
        id=conta.id,
        empresa_id=conta.empresa_id,
        banco_nome=conta.banco_nome,
        banco_codigo=str(conta.banco_codigo) if conta.banco_codigo else None,
        agencia=conta.agencia,
        conta=conta.conta,
        tipo=conta.tipo.value,
        descricao=conta.descricao,
        ativo=conta.ativo,
    )


def _para_entidade(model: ContaBancariaModel) -> ContaBancaria:
    """Converte model ORM para a entidade ContaBancaria."""
    return ContaBancaria(
        id=model.id,
        empresa_id=model.empresa_id,
        banco_nome=model.banco_nome,
        banco_codigo=BancoCodigo(model.banco_codigo) if model.banco_codigo else None,
        agencia=model.agencia,
        conta=model.conta,
        tipo=TipoContaBancaria(model.tipo),
        descricao=model.descricao,
        ativo=model.ativo,
    )


class SQLiteContaBancariaRepository(ContaBancariaRepository):
    """Repositorio de contas bancarias sobre banco SQLite."""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create(self, conta: ContaBancaria) -> ContaBancaria:
        with self._session_factory() as session:
            model = _para_model(conta)
            session.add(model)
            session.commit()
            session.refresh(model)
            return _para_entidade(model)

    def get_by_id(self, id: int) -> ContaBancaria | None:
        with self._session_factory() as session:
            model = session.get(ContaBancariaModel, id)
            return _para_entidade(model) if model is not None else None

    def update(self, conta: ContaBancaria) -> ContaBancaria:
        if conta.id is None:
            raise ValueError("ID da conta bancaria nao pode ser None para atualizacao.")

        with self._session_factory() as session:
            model = session.get(ContaBancariaModel, conta.id)
            if model is None:
                raise ValueError(
                    f"Conta bancaria com ID {conta.id} não encontrada para atualizacao."
                )

            model.empresa_id = conta.empresa_id
            model.banco_nome = conta.banco_nome
            model.banco_codigo = str(conta.banco_codigo) if conta.banco_codigo else None
            model.agencia = conta.agencia
            model.conta = conta.conta
            model.tipo = conta.tipo.value
            model.descricao = conta.descricao
            model.ativo = conta.ativo

            session.commit()
            session.refresh(model)
            return _para_entidade(model)

    def delete(self, id: int) -> None:
        with self._session_factory() as session:
            model = session.get(ContaBancariaModel, id)
            if model is not None:
                session.delete(model)
                session.commit()

    def list_all(
        self, empresa_id: int | None = None, skip: int = 0, limit: int = 100
    ) -> list[ContaBancaria]:
        with self._session_factory() as session:
            stmt = select(ContaBancariaModel)
            if empresa_id is not None:
                stmt = stmt.where(ContaBancariaModel.empresa_id == empresa_id)
            stmt = stmt.order_by(ContaBancariaModel.id).offset(skip).limit(limit)
            models = session.scalars(stmt).all()
            return [_para_entidade(m) for m in models]
