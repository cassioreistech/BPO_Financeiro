"""Testes unitarios dos filtros avancados de titulos."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from application.dto.titulo_dto import FiltroTitulosDTO
from application.ports.titulo_repository import TituloRepository
from application.use_cases.titulo_use_cases import ListarTitulosUseCase
from domain.entities.alerta_titulo import AlertaTitulo
from domain.entities.titulo import Titulo
from domain.enums.categoria_titulo import CategoriaTitulo
from domain.enums.situacao_vencimento import SituacaoVencimento
from domain.enums.status_titulo import StatusTitulo
from domain.enums.tipo_titulo import TipoTitulo


class FakeTituloRepository(TituloRepository):
    """Repositorio fake para testes de filtros de titulos."""

    def __init__(self, titulos: list[Titulo] | None = None) -> None:
        self._titulos = titulos or []

    def create(self, titulo: Titulo) -> Titulo:
        return titulo

    def get_by_id(self, id: int) -> Titulo | None:
        return next((t for t in self._titulos if t.id == id), None)

    def update(self, titulo: Titulo) -> Titulo:
        return titulo

    def delete(self, id: int) -> None:
        return None

    def list_by_escritorio(
        self,
        escritorio_id: int,
        empresa_id: int | None = None,
        tipo: TipoTitulo | None = None,
        status: StatusTitulo | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Titulo]:
        return []

    def list_filtered(
        self,
        escritorio_id: int,
        filtro: FiltroTitulosDTO,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Titulo]:
        items = [
            t for t in self._titulos if t.escritorio_id == escritorio_id
        ]
        if filtro.empresa_id is not None:
            items = [t for t in items if t.empresa_id == filtro.empresa_id]
        if filtro.categoria is not None:
            items = [
                t for t in items if t.categoria.value == filtro.categoria
            ]
        if filtro.tipo is not None:
            items = [t for t in items if t.tipo.value == filtro.tipo]
        if filtro.status is not None:
            items = [t for t in items if t.status.value == filtro.status]
        if filtro.texto:
            termo = filtro.texto.lower()
            items = [
                t
                for t in items
                if termo in t.descricao.lower()
                or (
                    t.numero_documento is not None
                    and termo in t.numero_documento.lower()
                )
                or (
                    t.codigo_barras is not None
                    and termo in t.codigo_barras.lower()
                )
                or termo in t.categoria.value.lower()
            ]
        if filtro.data_vencimento_inicio is not None:
            items = [
                t
                for t in items
                if t.data_vencimento >= filtro.data_vencimento_inicio
            ]
        if filtro.data_vencimento_fim is not None:
            items = [
                t
                for t in items
                if t.data_vencimento <= filtro.data_vencimento_fim
            ]
        if filtro.situacao_vencimento is not None:
            hoje = date(2026, 8, 15)
            situacao = SituacaoVencimento(filtro.situacao_vencimento)
            if situacao == SituacaoVencimento.VENCIDOS:
                items = [t for t in items if t.data_vencimento < hoje]
            elif situacao == SituacaoVencimento.HOJE:
                items = [t for t in items if t.data_vencimento == hoje]
            elif situacao == SituacaoVencimento.AMANHA:
                items = [
                    t for t in items if t.data_vencimento == hoje + timedelta(days=1)
                ]
            elif situacao == SituacaoVencimento.PROXIMA_SEMANA:
                items = [
                    t
                    for t in items
                    if hoje < t.data_vencimento <= hoje + timedelta(days=7)
                ]
        return items[skip : skip + limit]

    def total_por_status(
        self,
        escritorio_id: int,
        status: StatusTitulo,
        tipo: TipoTitulo | None = None,
    ) -> Decimal:
        return Decimal("0")

    def list_alertas(
        self,
        escritorio_id: int,
        empresa_id: int | None,
        data_referencia: date,
        incluir_vencidos: bool,
    ) -> list[AlertaTitulo]:
        return []

    def list_parcelas_relacionadas(
        self,
        escritorio_id: int,
        empresa_id: int,
        descricao_base: str,
        primeiro_vencimento: date,
        excluir_id: int,
    ) -> list[Titulo]:
        return []


def _criar_titulo(
    id: int,
    descricao: str,
    tipo: TipoTitulo,
    status: StatusTitulo,
    valor: Decimal,
    vencimento: date,
    empresa_id: int = 1,
    categoria: CategoriaTitulo = CategoriaTitulo.OUTRO,
    numero_documento: str | None = None,
    codigo_barras: str | None = None,
) -> Titulo:
    return Titulo(
        id=id,
        escritorio_id=1,
        empresa_id=empresa_id,
        plano_conta_id=1,
        descricao=descricao,
        tipo=tipo,
        status=status,
        valor=valor,
        data_emissao=date(2026, 8, 1),
        data_vencimento=vencimento,
        categoria=categoria,
        numero_documento=numero_documento,
        codigo_barras=codigo_barras,
    )


@pytest.fixture
def hoje() -> date:
    return date(2026, 8, 15)


@pytest.fixture
def titulos(hoje: date) -> list[Titulo]:
    return [
        _criar_titulo(
            1, "Aluguel agosto", TipoTitulo.PAGAR, StatusTitulo.ABERTO,
            Decimal("1500.00"), hoje - timedelta(days=5),
            categoria=CategoriaTitulo.OUTRO,
            numero_documento="NF-001",
        ),
        _criar_titulo(
            2, "Servico de consultoria", TipoTitulo.RECEBER, StatusTitulo.ABERTO,
            Decimal("3000.00"), hoje,
            categoria=CategoriaTitulo.SERVICO,
            numero_documento="NF-002",
        ),
        _criar_titulo(
            3, "Material de escritorio", TipoTitulo.PAGAR, StatusTitulo.PAGO,
            Decimal("250.00"), hoje + timedelta(days=3),
            categoria=CategoriaTitulo.OUTRO,
        ),
        _criar_titulo(
            4, "Imposto municipal", TipoTitulo.PAGAR, StatusTitulo.ABERTO,
            Decimal("800.00"), hoje + timedelta(days=10),
            categoria=CategoriaTitulo.IMPOSTO,
            codigo_barras="1234567890",
        ),
        _criar_titulo(
            5, "Recebimento cliente B", TipoTitulo.RECEBER, StatusTitulo.CANCELADO,
            Decimal("1200.00"), hoje - timedelta(days=1),
            empresa_id=2,
            categoria=CategoriaTitulo.SERVICO,
        ),
    ]


@pytest.fixture
def use_case(titulos: list[Titulo]) -> ListarTitulosUseCase:
    return ListarTitulosUseCase(FakeTituloRepository(titulos))


class TestListarTitulosUseCaseFiltros:
    def test_sem_filtros_retorna_todos(
        self, use_case: ListarTitulosUseCase
    ) -> None:
        resultado = use_case.execute(escritorio_id=1)
        assert len(resultado) == 5

    def test_filtro_por_empresa(
        self, use_case: ListarTitulosUseCase
    ) -> None:
        resultado = use_case.execute(
            escritorio_id=1,
            filtro=FiltroTitulosDTO(empresa_id=1),
        )
        assert len(resultado) == 4
        assert all(t.empresa_id == 1 for t in resultado)

    def test_busca_por_descricao(
        self, use_case: ListarTitulosUseCase
    ) -> None:
        resultado = use_case.execute(
            escritorio_id=1,
            filtro=FiltroTitulosDTO(texto="aluguel"),
        )
        assert len(resultado) == 1
        assert resultado[0].descricao == "Aluguel agosto"

    def test_busca_case_insensitive(
        self, use_case: ListarTitulosUseCase
    ) -> None:
        resultado = use_case.execute(
            escritorio_id=1,
            filtro=FiltroTitulosDTO(texto="ALUGUEL"),
        )
        assert len(resultado) == 1

    def test_busca_por_numero_documento(
        self, use_case: ListarTitulosUseCase
    ) -> None:
        resultado = use_case.execute(
            escritorio_id=1,
            filtro=FiltroTitulosDTO(texto="NF-002"),
        )
        assert len(resultado) == 1
        assert resultado[0].id == 2

    def test_busca_por_categoria(
        self, use_case: ListarTitulosUseCase
    ) -> None:
        resultado = use_case.execute(
            escritorio_id=1,
            filtro=FiltroTitulosDTO(texto="TRIBUTOS"),
        )
        assert len(resultado) == 1
        assert resultado[0].id == 4

    def test_busca_por_codigo_barras(
        self, use_case: ListarTitulosUseCase
    ) -> None:
        resultado = use_case.execute(
            escritorio_id=1,
            filtro=FiltroTitulosDTO(texto="1234567890"),
        )
        assert len(resultado) == 1
        assert resultado[0].id == 4

    def test_filtro_por_status_quitado(
        self, use_case: ListarTitulosUseCase
    ) -> None:
        resultado = use_case.execute(
            escritorio_id=1,
            filtro=FiltroTitulosDTO(status="PAGO"),
        )
        assert len(resultado) == 1
        assert resultado[0].status == "PAGO"

    def test_filtro_por_tipo(
        self, use_case: ListarTitulosUseCase
    ) -> None:
        resultado = use_case.execute(
            escritorio_id=1,
            filtro=FiltroTitulosDTO(tipo="RECEBER"),
        )
        assert len(resultado) == 2
        assert all(t.tipo == "RECEBER" for t in resultado)

    def test_filtro_por_categoria(
        self, use_case: ListarTitulosUseCase
    ) -> None:
        resultado = use_case.execute(
            escritorio_id=1,
            filtro=FiltroTitulosDTO(categoria="OUTRO"),
        )
        assert len(resultado) == 2
        assert all(t.categoria == "OUTRO" for t in resultado)

    def test_filtro_por_intervalo_vencimento(
        self, use_case: ListarTitulosUseCase, hoje: date
    ) -> None:
        resultado = use_case.execute(
            escritorio_id=1,
            filtro=FiltroTitulosDTO(
                data_vencimento_inicio=hoje - timedelta(days=2),
                data_vencimento_fim=hoje + timedelta(days=2),
            ),
        )
        assert len(resultado) == 3

    def test_intervalo_vencimento_invalido(
        self, use_case: ListarTitulosUseCase, hoje: date
    ) -> None:
        with pytest.raises(ValueError, match="inicial nao pode ser posterior"):
            use_case.execute(
                escritorio_id=1,
                filtro=FiltroTitulosDTO(
                    data_vencimento_inicio=hoje + timedelta(days=5),
                    data_vencimento_fim=hoje,
                ),
            )

    def test_filtro_situacao_vencidos(
        self, use_case: ListarTitulosUseCase
    ) -> None:
        resultado = use_case.execute(
            escritorio_id=1,
            filtro=FiltroTitulosDTO(
                situacao_vencimento=SituacaoVencimento.VENCIDOS.value
            ),
        )
        assert len(resultado) == 1
        assert resultado[0].id == 1

    def test_filtro_situacao_hoje(
        self, use_case: ListarTitulosUseCase
    ) -> None:
        resultado = use_case.execute(
            escritorio_id=1,
            filtro=FiltroTitulosDTO(
                situacao_vencimento=SituacaoVencimento.HOJE.value
            ),
        )
        assert len(resultado) == 1
        assert resultado[0].id == 2

    def test_filtro_situacao_amanha(
        self, use_case: ListarTitulosUseCase
    ) -> None:
        resultado = use_case.execute(
            escritorio_id=1,
            filtro=FiltroTitulosDTO(
                situacao_vencimento=SituacaoVencimento.AMANHA.value
            ),
        )
        assert len(resultado) == 0

    def test_filtro_situacao_proxima_semana(
        self, use_case: ListarTitulosUseCase
    ) -> None:
        resultado = use_case.execute(
            escritorio_id=1,
            filtro=FiltroTitulosDTO(
                situacao_vencimento=SituacaoVencimento.PROXIMA_SEMANA.value
            ),
        )
        assert len(resultado) == 2
        assert {t.id for t in resultado} == {3, 4}

    def test_combinacao_de_filtros(
        self, use_case: ListarTitulosUseCase
    ) -> None:
        resultado = use_case.execute(
            escritorio_id=1,
            filtro=FiltroTitulosDTO(
                texto="NF",
                tipo="PAGAR",
                status="ABERTO",
            ),
        )
        assert len(resultado) == 1
        assert resultado[0].id == 1
