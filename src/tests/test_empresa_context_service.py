"""Testes do servico de contexto de empresa ativa."""

from __future__ import annotations

import pytest

from application.dto.contexto_empresa_dto import EmpresaAtivaDTO
from application.services.empresa_context_service import EmpresaContextService


@pytest.fixture
def service() -> EmpresaContextService:
    return EmpresaContextService()


@pytest.fixture
def empresa() -> EmpresaAtivaDTO:
    return EmpresaAtivaDTO(
        id=1,
        nome_fantasia="Empresa Teste",
        razao_social="Empresa Teste LTDA",
        cnpj="11111111000109",
    )


class TestEmpresaContextService:
    def test_inicial_sem_empresa_ativa(
        self, service: EmpresaContextService
    ) -> None:
        assert service.get_empresa_ativa() is None
        assert service.get_empresa_ativa_detalhes() is None

    def test_set_e_get_empresa_ativa(
        self,
        service: EmpresaContextService,
        empresa: EmpresaAtivaDTO,
    ) -> None:
        service.set_empresa_ativa(empresa.id, empresa)

        assert service.get_empresa_ativa() == empresa.id
        assert service.get_empresa_ativa_detalhes() == empresa

    def test_callback_eh_chamado_ao_mudar_empresa(
        self,
        service: EmpresaContextService,
        empresa: EmpresaAtivaDTO,
    ) -> None:
        chamadas: list[int | None] = []
        service.adicionar_callback(lambda empresa_id: chamadas.append(empresa_id))

        service.set_empresa_ativa(empresa.id, empresa)

        assert chamadas == [empresa.id]

    def test_remover_callback(
        self,
        service: EmpresaContextService,
        empresa: EmpresaAtivaDTO,
    ) -> None:
        chamadas: list[int | None] = []

        def callback(empresa_id: int | None) -> None:
            chamadas.append(empresa_id)

        service.adicionar_callback(callback)
        service.remover_callback(callback)

        service.set_empresa_ativa(empresa.id, empresa)

        assert chamadas == []

    def test_trocar_empresa_ativa_notifica_novo_id(
        self,
        service: EmpresaContextService,
        empresa: EmpresaAtivaDTO,
    ) -> None:
        chamadas: list[int | None] = []
        service.adicionar_callback(lambda empresa_id: chamadas.append(empresa_id))

        service.set_empresa_ativa(empresa.id, empresa)
        service.set_empresa_ativa(2, None)

        assert chamadas == [empresa.id, 2]
