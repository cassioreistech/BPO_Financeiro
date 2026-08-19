"""Entidade Contador — profissional contabil."""

from __future__ import annotations

from dataclasses import dataclass

from domain.value_objects.crc import CRC
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone


@dataclass
class Contador:
    """Contador vinculado a um escritorio.

    Atributos:
        id: identificador unico (None antes de persistir)
        escritorio_id: FK para o escritorio
        nome: nome completo do contador
        crc: registro no CRC (opcional)
        email: email profissional (opcional)
        telefone: telefone de contato (opcional)
    """

    escritorio_id: int
    nome: str
    id: int | None = None
    crc: CRC | None = None
    email: Email | None = None
    telefone: Telefone | None = None

    def __post_init__(self) -> None:
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome do contador não pode ser vazio.")
        if self.escritorio_id is None or self.escritorio_id <= 0:
            raise ValueError("Escritorio ID deve ser um numero positivo.")

        object.__setattr__(self, "nome", self.nome.strip())
