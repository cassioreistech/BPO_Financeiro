"""Repository concreto de Empresa persistido em SQLite via SQLAlchemy."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from application.ports.empresa_repository import EmpresaRepository
from domain.entities.empresa import Empresa
from domain.enums.regime_tributario import RegimeTributario
from domain.enums.status_empresa import StatusEmpresa
from domain.value_objects.cnpj import CNPJ
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone
from infrastructure.database.models.empresa_model import EmpresaModel


def _para_model(empresa: Empresa) -> EmpresaModel:
    """Converte entidade Empresa para o model ORM."""
    return EmpresaModel(
        id=empresa.id,
        escritorio_id=empresa.escritorio_id,
        contador_id=empresa.contador_id,
        cnpj=empresa.cnpj.valor,
        razao_social=empresa.razao_social,
        nome_fantasia=empresa.nome_fantasia,
        regime_tributario=empresa.regime_tributario.value,
        email_financeiro=str(empresa.email_financeiro) if empresa.email_financeiro else None,
        telefone_financeiro=str(empresa.telefone_financeiro)
        if empresa.telefone_financeiro
        else None,
        ativo=empresa.ativo == StatusEmpresa.ATIVA,
    )


def _para_entidade(model: EmpresaModel) -> Empresa:
    """Converte model ORM para a entidade Empresa."""
    return Empresa(
        id=model.id,
        escritorio_id=model.escritorio_id,
        contador_id=model.contador_id,
        cnpj=CNPJ(model.cnpj),
        razao_social=model.razao_social,
        nome_fantasia=model.nome_fantasia,
        regime_tributario=RegimeTributario(model.regime_tributario),
        email_financeiro=Email(model.email_financeiro) if model.email_financeiro else None,
        telefone_financeiro=Telefone(model.telefone_financeiro)
        if model.telefone_financeiro
        else None,
        ativo=StatusEmpresa.ATIVA if model.ativo else StatusEmpresa.INATIVA,
    )


class SQLiteEmpresaRepository(EmpresaRepository):
    """Repositorio de empresas sobre banco SQLite.

    Cada operacao abre e fecha a propria sessao, mantendo o ciclo de vida
    previsivel e isolado para a camada de application.
    """

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create(self, empresa: Empresa) -> Empresa:
        with self._session_factory() as session:
            model = _para_model(empresa)
            session.add(model)
            session.commit()
            session.refresh(model)
            return _para_entidade(model)

    def get_by_id(self, id: int) -> Empresa | None:
        with self._session_factory() as session:
            model = session.get(EmpresaModel, id)
            return _para_entidade(model) if model is not None else None

    def get_by_cnpj(self, cnpj: str) -> Empresa | None:
        with self._session_factory() as session:
            stmt = select(EmpresaModel).where(EmpresaModel.cnpj == cnpj)
            model = session.scalars(stmt).first()
            return _para_entidade(model) if model is not None else None

    def update(self, empresa: Empresa) -> Empresa:
        if empresa.id is None:
            raise ValueError("ID da empresa nao pode ser None para atualizacao.")

        with self._session_factory() as session:
            model = session.get(EmpresaModel, empresa.id)
            if model is None:
                raise ValueError(
                    f"Empresa com ID {empresa.id} nao encontrada para atualizacao."
                )

            model.escritorio_id = empresa.escritorio_id
            model.contador_id = empresa.contador_id
            model.cnpj = empresa.cnpj.valor
            model.razao_social = empresa.razao_social
            model.nome_fantasia = empresa.nome_fantasia
            model.regime_tributario = empresa.regime_tributario.value
            model.email_financeiro = (
                str(empresa.email_financeiro) if empresa.email_financeiro else None
            )
            model.telefone_financeiro = (
                str(empresa.telefone_financeiro) if empresa.telefone_financeiro else None
            )
            model.ativo = empresa.ativo == StatusEmpresa.ATIVA

            session.commit()
            session.refresh(model)
            return _para_entidade(model)

    def delete(self, id: int) -> None:
        with self._session_factory() as session:
            model = session.get(EmpresaModel, id)
            if model is not None:
                session.delete(model)
                session.commit()

    def list_all(
        self,
        escritorio_id: int | None = None,
        contador_id: int | None = None,
        ativo: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Empresa]:
        with self._session_factory() as session:
            stmt = select(EmpresaModel).order_by(EmpresaModel.id)
            if escritorio_id is not None:
                stmt = stmt.where(EmpresaModel.escritorio_id == escritorio_id)
            if contador_id is not None:
                stmt = stmt.where(EmpresaModel.contador_id == contador_id)
            if ativo is not None:
                stmt = stmt.where(EmpresaModel.ativo == ativo)

            stmt = stmt.offset(skip).limit(limit)
            models = session.scalars(stmt).all()
            return [_para_entidade(m) for m in models]
