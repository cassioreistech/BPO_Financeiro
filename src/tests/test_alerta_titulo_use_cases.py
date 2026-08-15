"""Testes dos use cases de alertas de titulos."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from application.dto.alerta_titulo_dto import FiltroAlertasTitulosDTO
from application.dto.titulo_dto import FiltroTitulosDTO
from application.ports.titulo_repository import TituloRepository
from application.use_cases.alerta_titulo_use_cases import (
    ObterDashboardAlertasTitulosUseCase,
)
from domain.entities.alerta_titulo import AlertaTitulo, NivelUrgencia
from domain.entities.titulo import Titulo
from domain.enums.status_titulo import StatusTitulo
from domain.enums.tipo_titulo import TipoTitulo


class FakeTituloRepository(TituloRepository):
    """Repositorio fake para testes de alertas."""

    def __init__(self, alertas: list[AlertaTitulo] | None = None) -> None:
        self._alertas = alertas or []
        self._titulos: dict[int, Titulo] = {}
        self._proximo_id = 1

    def create(self, titulo: Titulo) -> Titulo:
        titulo.id = self._proximo_id
        self._titulos[self._proximo_id] = titulo
        self._proximo_id += 1
        return titulo

    def get_by_id(self, id: int) -> Titulo | None:
        return self._titulos.get(id)

    def update(self, titulo: Titulo) -> Titulo:
        if titulo.id is None:
            raise ValueError("ID do titulo nao pode ser None.")
        self._titulos[titulo.id] = titulo
        return titulo

    def delete(self, id: int) -> None:
        self._titulos.pop(id, None)

    def list_by_escritorio(
        self,
        escritorio_id: int,
        empresa_id: int | None = None,
        tipo: TipoTitulo | None = None,
        status: StatusTitulo | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Titulo]:
        return list(self._titulos.values())

    def list_filtered(
        self,
        escritorio_id: int,
        filtro: FiltroTitulosDTO,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Titulo]:
        return list(self._titulos.values())[skip : skip + limit]

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
        alertas = [
            a
            for a in self._alertas
            if a.empresa_id == empresa_id or empresa_id is None
        ]
        if not incluir_vencidos:
            alertas = [
                a
                for a in alertas
                if a.data_vencimento >= data_referencia
            ]
        limite = data_referencia + timedelta(days=7)
        alertas = [a for a in alertas if a.data_vencimento <= limite]
        return sorted(
            alertas,
            key=lambda a: (
                a.data_vencimento,
                a.empresa_nome.lower(),
                a.descricao.lower(),
            ),
        )


def _alerta(
    titulo_id: int,
    empresa_id: int,
    empresa_nome: str,
    descricao: str,
    valor: str,
    data_vencimento: date,
) -> AlertaTitulo:
    return AlertaTitulo(
        titulo_id=titulo_id,
        empresa_id=empresa_id,
        empresa_nome=empresa_nome,
        descricao=descricao,
        categoria="OUTRO",
        numero_documento=None,
        valor=Decimal(valor),
        data_vencimento=data_vencimento,
        status=StatusTitulo.ABERTO,
        urgencia=NivelUrgencia.INFORMATIVO,
    )


@pytest.fixture
def hoje() -> date:
    return date(2026, 8, 15)


class TestObterDashboardAlertasTitulos:
    def test_classifica_grupos_corretamente(
        self, hoje: date
    ) -> None:
        alertas = [
            _alerta(1, 1, "Empresa A", "Vencido", "100.00", hoje - timedelta(days=2)),
            _alerta(2, 1, "Empresa A", "Hoje", "200.00", hoje),
            _alerta(3, 2, "Empresa B", "Amanha", "300.00", hoje + timedelta(days=1)),
            _alerta(4, 2, "Empresa B", "Semana", "400.00", hoje + timedelta(days=5)),
            _alerta(5, 1, "Empresa A", "Depois", "500.00", hoje + timedelta(days=10)),
        ]
        use_case = ObterDashboardAlertasTitulosUseCase(
            FakeTituloRepository(alertas)
        )
        filtro = FiltroAlertasTitulosDTO(
            data_referencia=hoje, incluir_vencidos=True
        )

        resultado = use_case.execute(escritorio_id=1, filtro=filtro)

        assert resultado.vencidos.quantidade == 1
        assert resultado.vence_hoje.quantidade == 1
        assert resultado.vence_amanha.quantidade == 1
        assert resultado.semana.quantidade == 1
        assert resultado.total_quantidade == 4
        assert resultado.total_valor == Decimal("1000.00")

    def test_nao_duplica_titulos_na_semana(
        self, hoje: date
    ) -> None:
        alertas = [
            _alerta(1, 1, "A", "Hoje", "100.00", hoje),
            _alerta(2, 1, "A", "Amanha", "200.00", hoje + timedelta(days=1)),
            _alerta(3, 1, "A", "Semana", "300.00", hoje + timedelta(days=3)),
        ]
        use_case = ObterDashboardAlertasTitulosUseCase(
            FakeTituloRepository(alertas)
        )
        filtro = FiltroAlertasTitulosDTO(data_referencia=hoje)

        resultado = use_case.execute(escritorio_id=1, filtro=filtro)

        assert resultado.vence_hoje.quantidade == 1
        assert resultado.vence_amanha.quantidade == 1
        assert resultado.semana.quantidade == 1
        assert resultado.total_quantidade == 3

    def test_filtra_por_empresa(
        self, hoje: date
    ) -> None:
        alertas = [
            _alerta(1, 1, "Empresa A", "Titulo A", "100.00", hoje),
            _alerta(2, 2, "Empresa B", "Titulo B", "200.00", hoje),
        ]
        use_case = ObterDashboardAlertasTitulosUseCase(
            FakeTituloRepository(alertas)
        )
        filtro = FiltroAlertasTitulosDTO(
            empresa_id=1, data_referencia=hoje
        )

        resultado = use_case.execute(escritorio_id=1, filtro=filtro)

        assert resultado.vence_hoje.quantidade == 1
        assert resultado.total_valor == Decimal("100.00")
        assert resultado.vence_hoje.itens[0].empresa_id == 1

    def test_modo_consolidado_traz_todas_empresas(
        self, hoje: date
    ) -> None:
        alertas = [
            _alerta(1, 1, "Empresa A", "Titulo A", "100.00", hoje),
            _alerta(2, 2, "Empresa B", "Titulo B", "200.00", hoje),
            _alerta(3, 3, "Empresa C", "Titulo C", "300.00", hoje),
        ]
        use_case = ObterDashboardAlertasTitulosUseCase(
            FakeTituloRepository(alertas)
        )
        filtro = FiltroAlertasTitulosDTO(data_referencia=hoje)

        resultado = use_case.execute(escritorio_id=1, filtro=filtro)

        assert resultado.vence_hoje.quantidade == 3
        assert resultado.total_valor == Decimal("600.00")

    def test_exclui_vencidos_quando_configurado(
        self, hoje: date
    ) -> None:
        alertas = [
            _alerta(1, 1, "A", "Vencido", "100.00", hoje - timedelta(days=1)),
            _alerta(2, 1, "A", "Hoje", "200.00", hoje),
        ]
        use_case = ObterDashboardAlertasTitulosUseCase(
            FakeTituloRepository(alertas)
        )
        filtro = FiltroAlertasTitulosDTO(
            data_referencia=hoje, incluir_vencidos=False
        )

        resultado = use_case.execute(escritorio_id=1, filtro=filtro)

        assert resultado.vencidos.quantidade == 0
        assert resultado.vence_hoje.quantidade == 1

    def test_classifica_urgencia_corretamente(
        self, hoje: date
    ) -> None:
        alertas = [
            _alerta(1, 1, "A", "Vencido", "100.00", hoje - timedelta(days=1)),
            _alerta(2, 1, "A", "Hoje", "200.00", hoje),
            _alerta(3, 1, "A", "Amanha", "300.00", hoje + timedelta(days=1)),
            _alerta(4, 1, "A", "Semana", "400.00", hoje + timedelta(days=7)),
        ]
        use_case = ObterDashboardAlertasTitulosUseCase(
            FakeTituloRepository(alertas)
        )
        filtro = FiltroAlertasTitulosDTO(data_referencia=hoje)

        resultado = use_case.execute(escritorio_id=1, filtro=filtro)

        assert resultado.vencidos.itens[0].urgencia == "CRITICO"
        assert resultado.vence_hoje.itens[0].urgencia == "ALTO"
        assert resultado.vence_amanha.itens[0].urgencia == "MEDIO"
        assert resultado.semana.itens[0].urgencia == "INFORMATIVO"

    def test_escritorio_id_invalido(self, hoje: date) -> None:
        use_case = ObterDashboardAlertasTitulosUseCase(
            FakeTituloRepository()
        )
        filtro = FiltroAlertasTitulosDTO(data_referencia=hoje)

        with pytest.raises(ValueError, match="Escritorio ID"):
            use_case.execute(escritorio_id=0, filtro=filtro)
