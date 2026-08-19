"""Implementacoes fake dos repositories para testes."""

from __future__ import annotations

from application.ports.empresa_repository import EmpresaRepository
from application.ports.escritorio_repository import EscritorioRepository
from domain.entities.empresa import Empresa
from domain.entities.escritorio import Escritorio
from domain.enums.status_empresa import StatusEmpresa


class FakeEscritorioRepository(EscritorioRepository):
    """Repositorio fake em memoria para testes de escritorio."""

    def __init__(self) -> None:
        self._dados: dict[int, Escritorio] = {}
        self._proximo_id = 1

    def create(self, escritorio: Escritorio) -> Escritorio:
        novo = Escritorio(
            id=self._proximo_id,
            nome=escritorio.nome,
            cnpj_cpf=escritorio.cnpj_cpf,
            email=escritorio.email,
            telefone=escritorio.telefone,
        )
        self._dados[self._proximo_id] = novo
        self._proximo_id += 1
        return novo

    def get_by_id(self, id: int) -> Escritorio | None:
        return self._dados.get(id)

    def get_by_cnpj(self, cnpj: str) -> Escritorio | None:
        for esc in self._dados.values():
            if esc.cnpj_cpf == cnpj:
                return esc
        return None

    def update(self, escritorio: Escritorio) -> Escritorio:
        if escritorio.id is None:
            raise ValueError("ID do escritório não pode ser None para atualizacao.")
        self._dados[escritorio.id] = escritorio
        return escritorio

    def delete(self, id: int) -> None:
        self._dados.pop(id, None)

    def list_all(self, skip: int = 0, limit: int = 100) -> list[Escritorio]:
        itens = list(self._dados.values())
        return itens[skip : skip + limit]


class FakeEmpresaRepository(EmpresaRepository):
    """Repositorio fake em memoria para testes de empresa."""

    def __init__(self) -> None:
        self._dados: dict[int, Empresa] = {}
        self._proximo_id = 1

    def create(self, empresa: Empresa) -> Empresa:
        nova = Empresa(
            id=self._proximo_id,
            escritorio_id=empresa.escritorio_id,
            contador_id=empresa.contador_id,
            cnpj=empresa.cnpj,
            razao_social=empresa.razao_social,
            nome_fantasia=empresa.nome_fantasia,
            regime_tributario=empresa.regime_tributario,
            email_financeiro=empresa.email_financeiro,
            telefone_financeiro=empresa.telefone_financeiro,
            ativo=empresa.ativo,
        )
        self._dados[self._proximo_id] = nova
        self._proximo_id += 1
        return nova

    def get_by_id(self, id: int) -> Empresa | None:
        return self._dados.get(id)

    def get_by_cnpj(self, cnpj: str) -> Empresa | None:
        for emp in self._dados.values():
            if emp.cnpj.valor == cnpj:
                return emp
        return None

    def update(self, empresa: Empresa) -> Empresa:
        if empresa.id is None:
            raise ValueError("ID da empresa não pode ser None para atualizacao.")
        self._dados[empresa.id] = empresa
        return empresa

    def delete(self, id: int) -> None:
        self._dados.pop(id, None)

    def list_all(
        self,
        escritorio_id: int | None = None,
        contador_id: int | None = None,
        ativo: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Empresa]:
        itens = list(self._dados.values())

        if escritorio_id is not None:
            itens = [e for e in itens if e.escritorio_id == escritorio_id]
        if contador_id is not None:
            itens = [e for e in itens if e.contador_id == contador_id]
        if ativo is not None:
            status_alvo = StatusEmpresa.ATIVA if ativo else StatusEmpresa.INATIVA
            itens = [e for e in itens if e.ativo == status_alvo]

        return itens[skip : skip + limit]
