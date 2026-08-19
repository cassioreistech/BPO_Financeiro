"""Entidade Empresa — empresa cliente do escritorio."""

from __future__ import annotations

from dataclasses import dataclass, field

from domain.enums.regime_tributario import RegimeTributario
from domain.enums.status_empresa import StatusEmpresa
from domain.value_objects.documento import Documento
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone


@dataclass
class Empresa:
    """Empresa cliente atendida pelo escritorio contabil.

    Atributos:
        id: identificador unico (None antes de persistir)
        escritorio_id: FK para o escritorio responsavel
        contador_id: FK para o contador responsavel (opcional)
        documento: CNPJ ou CPF validado
        razao_social: nome oficial da empresa
        nome_fantasia: nome comercial
        regime_tributario: regime tributario vigente
        email_financeiro: email para assuntos financeiros (opcional)
        telefone_financeiro: telefone para assuntos financeiros (opcional)
        ativo: status da empresa (ativa por padrao)
    """

    escritorio_id: int
    documento: Documento
    razao_social: str
    nome_fantasia: str
    regime_tributario: RegimeTributario
    id: int | None = None
    contador_id: int | None = None
    email_financeiro: Email | None = None
    telefone_financeiro: Telefone | None = None
    ativo: StatusEmpresa = field(default=StatusEmpresa.ATIVA)

    def __post_init__(self) -> None:
        if not self.razao_social or not self.razao_social.strip():
            raise ValueError("Razao social não pode ser vazia.")
        if not self.nome_fantasia or not self.nome_fantasia.strip():
            raise ValueError("Nome fantasia não pode ser vazio.")
        if self.escritorio_id is None or self.escritorio_id <= 0:
            raise ValueError("Escritorio ID deve ser um numero positivo.")

        object.__setattr__(self, "razao_social", self.razao_social.strip())
        object.__setattr__(self, "nome_fantasia", self.nome_fantasia.strip())

    @property
    def cnpj(self) -> str:
        """Compatibilidade: retorna o documento como string (apenas dígitos)."""
        return self.documento.apenas_digitos()

    @property
    def tipo_documento(self) -> str:
        return self.documento.tipo
