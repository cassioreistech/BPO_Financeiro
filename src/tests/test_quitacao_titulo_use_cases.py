"""Testes unitarios do use case de quitacao de titulos."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from application.dto.titulo_dto import EditarTituloDTO, FiltroTitulosDTO, QuitarTituloDTO
from application.ports.conta_bancaria_repository import ContaBancariaRepository
from application.ports.titulo_repository import TituloRepository
from application.use_cases.titulo_use_cases import (
    EditarTituloUseCase,
    QuitarTituloUseCase,
)
from domain.entities.alerta_titulo import AlertaTitulo
from domain.entities.conta_bancaria import ContaBancaria
from domain.entities.titulo import Titulo
from domain.enums.status_titulo import StatusTitulo
from domain.enums.tipo_conta_bancaria import TipoContaBancaria
from domain.enums.tipo_titulo import TipoTitulo


class FakeTituloRepository(TituloRepository):
    """Repositorio fake para testes de titulos."""

    def __init__(self) -> None:
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
            raise ValueError("ID do título não pode ser None.")
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
        items = [
            t
            for t in self._titulos.values()
            if t.escritorio_id == escritorio_id
        ]
        if empresa_id is not None:
            items = [t for t in items if t.empresa_id == empresa_id]
        if tipo is not None:
            items = [t for t in items if t.tipo == tipo]
        if status is not None:
            items = [t for t in items if t.status == status]
        return items

    def list_filtered(
        self,
        escritorio_id: int,
        filtro: FiltroTitulosDTO,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Titulo]:
        items = [
            t
            for t in self._titulos.values()
            if t.escritorio_id == escritorio_id
        ]
        if filtro.empresa_id is not None:
            items = [t for t in items if t.empresa_id == filtro.empresa_id]
        if filtro.categoria is not None:
            items = [t for t in items if t.categoria.value == filtro.categoria]
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
                or (t.numero_documento is not None and termo in t.numero_documento.lower())
                or (t.codigo_barras is not None and termo in t.codigo_barras.lower())
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
        return items[skip : skip + limit]

    def total_por_status(
        self,
        escritorio_id: int,
        status: StatusTitulo,
        tipo: TipoTitulo | None = None,
    ) -> Decimal:
        total = Decimal("0")
        for t in self._titulos.values():
            if t.escritorio_id != escritorio_id or t.status != status:
                continue
            if tipo is not None and t.tipo != tipo:
                continue
            total += t.valor
        return total

    def list_alertas(
        self,
        escritorio_id: int,
        empresa_id: int | None,
        data_referencia: date,
        incluir_vencidos: bool,
    ) -> list[AlertaTitulo]:
        return []


class FakeContaBancariaRepository(ContaBancariaRepository):
    """Repositorio fake para testes de contas bancarias."""

    def __init__(self) -> None:
        self._contas: dict[int, ContaBancaria] = {}
        self._proximo_id = 1

    def create(self, conta: ContaBancaria) -> ContaBancaria:
        conta.id = self._proximo_id
        self._contas[self._proximo_id] = conta
        self._proximo_id += 1
        return conta

    def get_by_id(self, id: int) -> ContaBancaria | None:
        return self._contas.get(id)

    def update(self, conta: ContaBancaria) -> ContaBancaria:
        if conta.id is None:
            raise ValueError("ID da conta nao pode ser None.")
        self._contas[conta.id] = conta
        return conta

    def delete(self, id: int) -> None:
        self._contas.pop(id, None)

    def list_all(
        self, empresa_id: int | None = None, skip: int = 0, limit: int = 100
    ) -> list[ContaBancaria]:
        items = list(self._contas.values())
        if empresa_id is not None:
            items = [c for c in items if c.empresa_id == empresa_id]
        return items[skip : skip + limit]


def _criar_titulo(
    repo: FakeTituloRepository,
    status: StatusTitulo = StatusTitulo.ABERTO,
    empresa_id: int = 1,
) -> Titulo:
    titulo = Titulo(
        escritorio_id=1,
        empresa_id=empresa_id,
        plano_conta_id=1,
        descricao="Titulo teste",
        tipo=TipoTitulo.PAGAR,
        status=status,
        valor=Decimal("150.00"),
        data_emissao=date(2026, 8, 1),
        data_vencimento=date(2026, 8, 20),
    )
    return repo.create(titulo)


def _criar_conta(
    repo: FakeContaBancariaRepository,
    empresa_id: int = 1,
    ativo: bool = True,
) -> ContaBancaria:
    conta = ContaBancaria(
        empresa_id=empresa_id,
        banco_nome="Banco Teste",
        agencia="0001",
        conta="12345-6",
        tipo=TipoContaBancaria.CORRENTE,
        descricao="Conta corrente",
        ativo=ativo,
    )
    return repo.create(conta)


@pytest.fixture
def titulo_repo() -> FakeTituloRepository:
    return FakeTituloRepository()


@pytest.fixture
def conta_repo() -> FakeContaBancariaRepository:
    return FakeContaBancariaRepository()


@pytest.fixture
def use_case(
    titulo_repo: FakeTituloRepository,
    conta_repo: FakeContaBancariaRepository,
) -> QuitarTituloUseCase:
    return QuitarTituloUseCase(titulo_repo, conta_repo)


@pytest.fixture
def editar_use_case(
    titulo_repo: FakeTituloRepository,
) -> EditarTituloUseCase:
    return EditarTituloUseCase(titulo_repo)


class TestQuitarTituloUseCase:
    def test_quitar_titulo_aberto_com_dados_validos(
        self,
        use_case: QuitarTituloUseCase,
        titulo_repo: FakeTituloRepository,
        conta_repo: FakeContaBancariaRepository,
    ) -> None:
        titulo = _criar_titulo(titulo_repo)
        conta = _criar_conta(conta_repo)
        assert titulo.id is not None
        assert conta.id is not None

        dto = QuitarTituloDTO(
            id=titulo.id,
            data_quitacao=date(2026, 8, 15),
            valor_pago=Decimal("150.00"),
            conta_bancaria_id=conta.id,
            forma_pagamento="PIX",
            observacao_quitacao="Quitado via PIX",
        )

        resultado = use_case.execute(dto)

        assert resultado.status == "PAGO"
        assert resultado.valor_pago == Decimal("150.00")
        assert resultado.conta_bancaria_id == conta.id
        assert resultado.forma_pagamento == "PIX"
        assert resultado.observacao_quitacao == "Quitado via PIX"

    def test_impede_quitar_titulo_ja_quitado(
        self,
        use_case: QuitarTituloUseCase,
        titulo_repo: FakeTituloRepository,
        conta_repo: FakeContaBancariaRepository,
    ) -> None:
        titulo = _criar_titulo(titulo_repo, status=StatusTitulo.PAGO)
        conta = _criar_conta(conta_repo)
        assert titulo.id is not None
        assert conta.id is not None

        dto = QuitarTituloDTO(
            id=titulo.id,
            data_quitacao=date(2026, 8, 15),
            valor_pago=Decimal("150.00"),
            conta_bancaria_id=conta.id,
        )

        with pytest.raises(ValueError, match="ja esta quitado"):
            use_case.execute(dto)

    def test_impede_quitar_titulo_cancelado(
        self,
        use_case: QuitarTituloUseCase,
        titulo_repo: FakeTituloRepository,
        conta_repo: FakeContaBancariaRepository,
    ) -> None:
        titulo = _criar_titulo(titulo_repo, status=StatusTitulo.CANCELADO)
        conta = _criar_conta(conta_repo)
        assert titulo.id is not None
        assert conta.id is not None

        dto = QuitarTituloDTO(
            id=titulo.id,
            data_quitacao=date(2026, 8, 15),
            valor_pago=Decimal("150.00"),
            conta_bancaria_id=conta.id,
        )

        with pytest.raises(ValueError, match="cancelado"):
            use_case.execute(dto)

    def test_impede_valor_zero(
        self,
        use_case: QuitarTituloUseCase,
        titulo_repo: FakeTituloRepository,
        conta_repo: FakeContaBancariaRepository,
    ) -> None:
        titulo = _criar_titulo(titulo_repo)
        conta = _criar_conta(conta_repo)
        assert titulo.id is not None
        assert conta.id is not None

        dto = QuitarTituloDTO(
            id=titulo.id,
            data_quitacao=date(2026, 8, 15),
            valor_pago=Decimal("0.00"),
            conta_bancaria_id=conta.id,
        )

        with pytest.raises(ValueError, match="maior que zero"):
            use_case.execute(dto)

    def test_impede_valor_maior_que_titulo(
        self,
        use_case: QuitarTituloUseCase,
        titulo_repo: FakeTituloRepository,
        conta_repo: FakeContaBancariaRepository,
    ) -> None:
        titulo = _criar_titulo(titulo_repo)
        conta = _criar_conta(conta_repo)
        assert titulo.id is not None
        assert conta.id is not None

        dto = QuitarTituloDTO(
            id=titulo.id,
            data_quitacao=date(2026, 8, 15),
            valor_pago=Decimal("200.00"),
            conta_bancaria_id=conta.id,
        )

        with pytest.raises(ValueError, match="igual ao valor do titulo"):
            use_case.execute(dto)

    def test_valida_conta_bancaria_ativa(
        self,
        use_case: QuitarTituloUseCase,
        titulo_repo: FakeTituloRepository,
        conta_repo: FakeContaBancariaRepository,
    ) -> None:
        titulo = _criar_titulo(titulo_repo)
        conta = _criar_conta(conta_repo, ativo=False)
        assert titulo.id is not None
        assert conta.id is not None

        dto = QuitarTituloDTO(
            id=titulo.id,
            data_quitacao=date(2026, 8, 15),
            valor_pago=Decimal("150.00"),
            conta_bancaria_id=conta.id,
        )

        with pytest.raises(ValueError, match="inativa"):
            use_case.execute(dto)

    def test_impede_conta_de_outra_empresa(
        self,
        use_case: QuitarTituloUseCase,
        titulo_repo: FakeTituloRepository,
        conta_repo: FakeContaBancariaRepository,
    ) -> None:
        titulo = _criar_titulo(titulo_repo, empresa_id=1)
        conta = _criar_conta(conta_repo, empresa_id=2)
        assert titulo.id is not None
        assert conta.id is not None

        dto = QuitarTituloDTO(
            id=titulo.id,
            data_quitacao=date(2026, 8, 15),
            valor_pago=Decimal("150.00"),
            conta_bancaria_id=conta.id,
        )

        with pytest.raises(ValueError, match="nao pertence a empresa do titulo"):
            use_case.execute(dto)

    def test_valida_forma_pagamento_invalida(
        self,
        use_case: QuitarTituloUseCase,
        titulo_repo: FakeTituloRepository,
        conta_repo: FakeContaBancariaRepository,
    ) -> None:
        titulo = _criar_titulo(titulo_repo)
        conta = _criar_conta(conta_repo)
        assert titulo.id is not None
        assert conta.id is not None

        dto = QuitarTituloDTO(
            id=titulo.id,
            data_quitacao=date(2026, 8, 15),
            valor_pago=Decimal("150.00"),
            conta_bancaria_id=conta.id,
            forma_pagamento="INVALIDA",
        )

        with pytest.raises(ValueError, match="Forma de pagamento invalida"):
            use_case.execute(dto)

    def test_valida_data_pagamento_obrigatoria(
        self,
        use_case: QuitarTituloUseCase,
        titulo_repo: FakeTituloRepository,
        conta_repo: FakeContaBancariaRepository,
    ) -> None:
        titulo = _criar_titulo(titulo_repo)
        conta = _criar_conta(conta_repo)
        assert titulo.id is not None
        assert conta.id is not None

        dto = QuitarTituloDTO(
            id=titulo.id,
            data_quitacao=None,  # type: ignore[arg-type]
            valor_pago=Decimal("150.00"),
            conta_bancaria_id=conta.id,
        )

        with pytest.raises(ValueError, match="Data de quitacao"):
            use_case.execute(dto)

    def test_valida_empresa_ativa_quando_informada(
        self,
        use_case: QuitarTituloUseCase,
        titulo_repo: FakeTituloRepository,
        conta_repo: FakeContaBancariaRepository,
    ) -> None:
        titulo = _criar_titulo(titulo_repo, empresa_id=1)
        conta = _criar_conta(conta_repo, empresa_id=1)
        assert titulo.id is not None
        assert conta.id is not None

        dto = QuitarTituloDTO(
            id=titulo.id,
            data_quitacao=date(2026, 8, 15),
            valor_pago=Decimal("150.00"),
            conta_bancaria_id=conta.id,
            empresa_id=2,
        )

        with pytest.raises(ValueError, match="empresa ativa"):
            use_case.execute(dto)

    def test_quitar_sem_repositorio_de_conta_aceita_conta_informada(
        self,
        titulo_repo: FakeTituloRepository,
    ) -> None:
        use_case = QuitarTituloUseCase(titulo_repo)
        titulo = _criar_titulo(titulo_repo)
        assert titulo.id is not None

        dto = QuitarTituloDTO(
            id=titulo.id,
            data_quitacao=date(2026, 8, 15),
            valor_pago=Decimal("150.00"),
            conta_bancaria_id=99,
        )

        resultado = use_case.execute(dto)
        assert resultado.status == "PAGO"
        assert resultado.conta_bancaria_id == 99


class TestEdicaoPreservaQuitacao:
    def test_edicao_preserva_observacao_quitacao(
        self,
        use_case: QuitarTituloUseCase,
        editar_use_case: EditarTituloUseCase,
        titulo_repo: FakeTituloRepository,
        conta_repo: FakeContaBancariaRepository,
    ) -> None:
        titulo = _criar_titulo(titulo_repo)
        conta = _criar_conta(conta_repo)
        assert titulo.id is not None
        assert conta.id is not None

        use_case.execute(
            QuitarTituloDTO(
                id=titulo.id,
                data_quitacao=date(2026, 8, 15),
                valor_pago=titulo.valor,
                conta_bancaria_id=conta.id,
                forma_pagamento="PIX",
                observacao_quitacao="Observacao importante",
            )
        )

        editado = editar_use_case.execute(
            EditarTituloDTO(
                id=titulo.id,
                escritorio_id=titulo.escritorio_id,
                empresa_id=titulo.empresa_id,
                plano_conta_id=titulo.plano_conta_id,
                descricao="Titulo alterado",
                tipo=titulo.tipo.value,
                valor=titulo.valor,
                data_emissao=titulo.data_emissao,
                data_vencimento=titulo.data_vencimento,
                observacao="Nova observacao",
            )
        )

        assert editado.descricao == "Titulo alterado"
        assert editado.observacao == "Nova observacao"
        assert editado.observacao_quitacao == "Observacao importante"
        assert editado.status == "PAGO"
        assert editado.valor_pago == titulo.valor
        assert editado.data_quitacao == date(2026, 8, 15)

    def test_edicao_preserva_dados_quitacao(
        self,
        use_case: QuitarTituloUseCase,
        editar_use_case: EditarTituloUseCase,
        titulo_repo: FakeTituloRepository,
        conta_repo: FakeContaBancariaRepository,
    ) -> None:
        titulo = _criar_titulo(titulo_repo)
        conta = _criar_conta(conta_repo)
        assert titulo.id is not None
        assert conta.id is not None

        use_case.execute(
            QuitarTituloDTO(
                id=titulo.id,
                data_quitacao=date(2026, 8, 15),
                valor_pago=titulo.valor,
                conta_bancaria_id=conta.id,
                forma_pagamento="BOLETO",
            )
        )

        editado = editar_use_case.execute(
            EditarTituloDTO(
                id=titulo.id,
                escritorio_id=titulo.escritorio_id,
                empresa_id=titulo.empresa_id,
                plano_conta_id=titulo.plano_conta_id,
                descricao="Descricao alterada",
                tipo=titulo.tipo.value,
                valor=titulo.valor,
                data_emissao=titulo.data_emissao,
                data_vencimento=titulo.data_vencimento,
            )
        )

        assert editado.status == "PAGO"
        assert editado.valor_pago == titulo.valor
        assert editado.conta_bancaria_id == conta.id
        assert editado.forma_pagamento == "BOLETO"
