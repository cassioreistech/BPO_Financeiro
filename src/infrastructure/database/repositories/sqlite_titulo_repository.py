"""Repository concreto de Titulo persistido em SQLite via SQLAlchemy."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
import re

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, sessionmaker

from application.dto.titulo_dto import FiltroTitulosDTO
from application.ports.titulo_repository import TituloRepository
from domain.entities.alerta_titulo import AlertaTitulo, NivelUrgencia
from domain.entities.titulo import Titulo
from domain.enums.categoria_titulo import CategoriaTitulo
from domain.enums.forma_pagamento import FormaPagamento
from domain.enums.situacao_vencimento import SituacaoVencimento
from domain.enums.status_titulo import StatusTitulo
from domain.enums.tipo_titulo import TipoTitulo
from infrastructure.database.models.empresa_model import EmpresaModel
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
        numero_documento=titulo.numero_documento,
        codigo_barras=titulo.codigo_barras,
        categoria=titulo.categoria.value,
        valor_pago=titulo.valor_pago,
        conta_bancaria_id=titulo.conta_bancaria_id,
        forma_pagamento=titulo.forma_pagamento.value,
        observacao_quitacao=titulo.observacao_quitacao,
        emitente=titulo.emitente,
    )


def _para_entidade(model: TituloModel) -> Titulo:
    """Converte model ORM para a entidade Titulo."""
    return Titulo(
        id=model.id,
        escritorio_id=model.escritorio_id,
        empresa_id=model.empresa_id,
        plano_conta_id=model.plano_conta_id,
        centro_custo_id=model.centro_custo_id,
        numero_documento=model.numero_documento,
        codigo_barras=model.codigo_barras,
        categoria=CategoriaTitulo(model.categoria),
        descricao=model.descricao,
        tipo=TipoTitulo(model.tipo),
        status=StatusTitulo(model.status),
        valor=model.valor,
        valor_pago=model.valor_pago,
        data_emissao=model.data_emissao,
        data_vencimento=model.data_vencimento,
        data_quitacao=model.data_quitacao,
        conta_bancaria_id=model.conta_bancaria_id,
        forma_pagamento=FormaPagamento(model.forma_pagamento),
        observacao=model.observacao,
        observacao_quitacao=model.observacao_quitacao,
        emitente=model.emitente,
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
            raise ValueError("ID do título não pode ser None para atualizacao.")

        with self._session_factory() as session:
            model = session.get(TituloModel, titulo.id)
            if model is None:
                raise ValueError(
                    f"Título com ID {titulo.id} não encontrado para atualizacao."
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
            model.numero_documento = titulo.numero_documento
            model.codigo_barras = titulo.codigo_barras
            model.categoria = titulo.categoria.value
            model.valor_pago = titulo.valor_pago
            model.conta_bancaria_id = titulo.conta_bancaria_id
            model.forma_pagamento = titulo.forma_pagamento.value
            model.observacao_quitacao = titulo.observacao_quitacao
            model.emitente = titulo.emitente

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

    def list_filtered(
        self,
        escritorio_id: int,
        filtro: FiltroTitulosDTO,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Titulo]:
        with self._session_factory() as session:
            stmt = select(TituloModel).where(
                TituloModel.escritorio_id == escritorio_id
            )

            if filtro.empresa_id is not None:
                stmt = stmt.where(TituloModel.empresa_id == filtro.empresa_id)

            if filtro.categoria is not None:
                stmt = stmt.where(TituloModel.categoria == filtro.categoria)

            if filtro.tipo is not None:
                stmt = stmt.where(TituloModel.tipo == filtro.tipo)

            if filtro.status is not None:
                stmt = stmt.where(TituloModel.status == filtro.status)

            if filtro.data_vencimento_inicio is not None:
                stmt = stmt.where(
                    TituloModel.data_vencimento >= filtro.data_vencimento_inicio
                )

            if filtro.data_vencimento_fim is not None:
                stmt = stmt.where(
                    TituloModel.data_vencimento <= filtro.data_vencimento_fim
                )

            if filtro.situacao_vencimento is not None:
                hoje = date.today()
                situacao = SituacaoVencimento(filtro.situacao_vencimento)
                if situacao == SituacaoVencimento.VENCIDOS:
                    stmt = stmt.where(TituloModel.data_vencimento < hoje)
                elif situacao == SituacaoVencimento.HOJE:
                    stmt = stmt.where(TituloModel.data_vencimento == hoje)
                elif situacao == SituacaoVencimento.AMANHA:
                    stmt = stmt.where(
                        TituloModel.data_vencimento == hoje + timedelta(days=1)
                    )
                elif situacao == SituacaoVencimento.PROXIMA_SEMANA:
                    stmt = stmt.where(
                        TituloModel.data_vencimento > hoje,
                        TituloModel.data_vencimento <= hoje + timedelta(days=7),
                    )

            if filtro.texto:
                termo = f"%{filtro.texto}%"
                condicoes = [
                    TituloModel.descricao.ilike(termo),
                    TituloModel.numero_documento.ilike(termo),
                    TituloModel.categoria.ilike(termo),
                    TituloModel.codigo_barras.ilike(termo),
                ]
                try:
                    id_busca = int(filtro.texto)
                    condicoes.append(TituloModel.id == id_busca)  # type: ignore[arg-type]
                except ValueError:
                    pass
                stmt = stmt.where(or_(*condicoes))

            stmt = (
                stmt.order_by(
                    TituloModel.data_vencimento,
                    TituloModel.status,
                    TituloModel.descricao,
                )
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

    def list_alertas(
        self,
        escritorio_id: int,
        empresa_id: int | None,
        data_referencia: date,
        incluir_vencidos: bool,
    ) -> list[AlertaTitulo]:
        with self._session_factory() as session:
            limite = data_referencia + timedelta(days=7)
            stmt = (
                select(
                    TituloModel.id,
                    TituloModel.empresa_id,
                    TituloModel.descricao,
                    TituloModel.categoria,
                    TituloModel.numero_documento,
                    TituloModel.valor,
                    TituloModel.data_vencimento,
                    TituloModel.status,
                    func.coalesce(
                        EmpresaModel.nome_fantasia,
                        EmpresaModel.razao_social,
                        "—",
                    ).label("empresa_nome"),
                )
                .select_from(TituloModel)
                .outerjoin(EmpresaModel, TituloModel.empresa_id == EmpresaModel.id)
                .where(
                    TituloModel.escritorio_id == escritorio_id,
                    TituloModel.status == StatusTitulo.ABERTO.value,
                    TituloModel.data_vencimento <= limite,
                )
            )

            if empresa_id is not None:
                stmt = stmt.where(TituloModel.empresa_id == empresa_id)
            if not incluir_vencidos:
                stmt = stmt.where(TituloModel.data_vencimento >= data_referencia)

            stmt = stmt.order_by(
                TituloModel.data_vencimento,
                func.coalesce(EmpresaModel.nome_fantasia, EmpresaModel.razao_social, "—"),
                TituloModel.descricao,
            )

            resultados = session.execute(stmt).all()
            return [
                AlertaTitulo(
                    titulo_id=row.id,
                    empresa_id=row.empresa_id,
                    empresa_nome=row.empresa_nome,
                    descricao=row.descricao,
                    categoria=row.categoria or "OUTRO",
                    numero_documento=row.numero_documento,
                    valor=Decimal(row.valor),
                    data_vencimento=row.data_vencimento,
                    status=StatusTitulo.ABERTO,
                    urgencia=NivelUrgencia.INFORMATIVO,
                )
                for row in resultados
            ]

    def list_parcelas_relacionadas(
        self,
        escritorio_id: int,
        empresa_id: int,
        descricao_base: str,
        primeiro_vencimento: date,
        excluir_id: int,
    ) -> list[Titulo]:
        """Busca parcelas subsequentes de uma replicação mensal."""
        with self._session_factory() as session:
            # Busca todos os títulos da mesma empresa com descrição que começa com a base
            # e vencimento >= primeiro_vencimento, exceto o próprio
            stmt = select(TituloModel).where(
                TituloModel.escritorio_id == escritorio_id,
                TituloModel.empresa_id == empresa_id,
                TituloModel.descricao.like(f"{descricao_base} %"),
                TituloModel.data_vencimento >= primeiro_vencimento,
                TituloModel.id != excluir_id,
            ).order_by(TituloModel.data_vencimento)
            
            models = session.scalars(stmt).all()
            return [_para_entidade(m) for m in models]
