"""Use cases para a entidade Titulo."""

from __future__ import annotations

from decimal import Decimal

from application.dto.titulo_dto import (
    CadastrarTituloDTO,
    EditarTituloDTO,
    FiltroTitulosDTO,
    QuitarTituloDTO,
    TituloResponseDTO,
)
from application.ports.conta_bancaria_repository import ContaBancariaRepository
from application.ports.titulo_repository import TituloRepository
from domain.entities.titulo import Titulo
from domain.enums.categoria_titulo import CategoriaTitulo
from domain.enums.forma_pagamento import FormaPagamento
from domain.enums.status_titulo import StatusTitulo
from domain.enums.tipo_titulo import TipoTitulo


def _para_response_dto(titulo: Titulo) -> TituloResponseDTO:
    """Converte entidade Titulo para ResponseDTO."""
    return TituloResponseDTO(
        id=titulo.id if titulo.id is not None else 0,
        escritorio_id=titulo.escritorio_id,
        empresa_id=titulo.empresa_id,
        plano_conta_id=titulo.plano_conta_id,
        centro_custo_id=titulo.centro_custo_id,
        numero_documento=titulo.numero_documento,
        codigo_barras=titulo.codigo_barras,
        categoria=titulo.categoria.value,
        descricao=titulo.descricao,
        tipo=titulo.tipo.value,
        status=titulo.status.value,
        valor=titulo.valor,
        valor_pago=titulo.valor_pago,
        data_emissao=titulo.data_emissao,
        data_vencimento=titulo.data_vencimento,
        data_quitacao=titulo.data_quitacao,
        conta_bancaria_id=titulo.conta_bancaria_id,
        forma_pagamento=titulo.forma_pagamento.value,
        observacao=titulo.observacao,
        observacao_quitacao=titulo.observacao_quitacao,
    )


def _validar_dto(dto: CadastrarTituloDTO | EditarTituloDTO) -> None:
    """Valida campos comuns dos DTOs de titulo."""
    if dto.escritorio_id <= 0:
        raise ValueError("Escritorio ID deve ser um numero positivo.")
    if dto.plano_conta_id <= 0:
        raise ValueError("Plano de Conta ID deve ser um numero positivo.")
    if dto.empresa_id is not None and dto.empresa_id <= 0:
        raise ValueError("Empresa ID deve ser um numero positivo.")
    if dto.centro_custo_id is not None and dto.centro_custo_id <= 0:
        raise ValueError("Centro de Custo ID deve ser um numero positivo.")
    if not dto.descricao or not dto.descricao.strip():
        raise ValueError("Descricao do titulo nao pode ser vazia.")
    if dto.valor <= Decimal("0"):
        raise ValueError("Valor do titulo deve ser maior que zero.")
    if dto.data_vencimento < dto.data_emissao:
        raise ValueError(
            "Data de vencimento nao pode ser anterior a data de emissao."
        )


def _parse_tipo(tipo_str: str) -> TipoTitulo:
    """Converte string para TipoTitulo."""
    try:
        return TipoTitulo(tipo_str)
    except ValueError:
        tipos_validos = [t.value for t in TipoTitulo]
        raise ValueError(
            f"Tipo de titulo invalido: '{tipo_str}'. "
            f"Valores aceitos: {tipos_validos}."
        ) from None


def _parse_categoria(categoria_str: str) -> CategoriaTitulo:
    """Converte string para CategoriaTitulo."""
    try:
        return CategoriaTitulo(categoria_str)
    except ValueError:
        categorias_validas = [c.value for c in CategoriaTitulo]
        raise ValueError(
            f"Categoria invalida: '{categoria_str}'. "
            f"Valores aceitos: {categorias_validas}."
        ) from None


def _parse_forma_pagamento(forma_str: str) -> FormaPagamento:
    """Converte string para FormaPagamento."""
    try:
        return FormaPagamento(forma_str)
    except ValueError:
        formas_validas = [f.value for f in FormaPagamento]
        raise ValueError(
            f"Forma de pagamento invalida: '{forma_str}'. "
            f"Valores aceitos: {formas_validas}."
        ) from None


class CadastrarTituloUseCase:
    """Use case para cadastro de titulo financeiro."""

    def __init__(self, repository: TituloRepository) -> None:
        self._repository = repository

    def execute(self, dto: CadastrarTituloDTO) -> TituloResponseDTO:
        """Executa o cadastro de um titulo.

        Raises:
            ValueError: se dados invalidos.
        """
        _validar_dto(dto)
        tipo = _parse_tipo(dto.tipo)
        categoria = _parse_categoria(dto.categoria)

        titulo = Titulo(
            escritorio_id=dto.escritorio_id,
            empresa_id=dto.empresa_id,
            plano_conta_id=dto.plano_conta_id,
            centro_custo_id=dto.centro_custo_id,
            numero_documento=dto.numero_documento.strip()
            if dto.numero_documento
            else None,
            codigo_barras=dto.codigo_barras.strip()
            if dto.codigo_barras
            else None,
            categoria=categoria,
            descricao=dto.descricao.strip(),
            tipo=tipo,
            status=StatusTitulo.ABERTO,
            valor=dto.valor,
            data_emissao=dto.data_emissao,
            data_vencimento=dto.data_vencimento,
            observacao=dto.observacao.strip() if dto.observacao else None,
        )

        salvo = self._repository.create(titulo)
        return _para_response_dto(salvo)


class EditarTituloUseCase:
    """Use case para edicao de titulo financeiro."""

    def __init__(self, repository: TituloRepository) -> None:
        self._repository = repository

    def execute(self, dto: EditarTituloDTO) -> TituloResponseDTO:
        """Executa a edicao de um titulo.

        Raises:
            ValueError: se titulo nao existe ou dados invalidos.
        """
        existente = self._repository.get_by_id(dto.id)
        if existente is None:
            raise ValueError(f"Titulo com ID {dto.id} nao encontrado.")
        if existente.status == StatusTitulo.CANCELADO:
            raise ValueError("Nao e possivel editar um titulo cancelado.")

        _validar_dto(dto)
        tipo = _parse_tipo(dto.tipo)
        categoria = _parse_categoria(dto.categoria)

        titulo = Titulo(
            id=dto.id,
            escritorio_id=dto.escritorio_id,
            empresa_id=dto.empresa_id,
            plano_conta_id=dto.plano_conta_id,
            centro_custo_id=dto.centro_custo_id,
            numero_documento=dto.numero_documento.strip()
            if dto.numero_documento
            else None,
            codigo_barras=dto.codigo_barras.strip()
            if dto.codigo_barras
            else None,
            categoria=categoria,
            descricao=dto.descricao.strip(),
            tipo=tipo,
            status=existente.status,
            valor=dto.valor,
            valor_pago=existente.valor_pago,
            data_emissao=dto.data_emissao,
            data_vencimento=dto.data_vencimento,
            data_quitacao=existente.data_quitacao,
            conta_bancaria_id=existente.conta_bancaria_id,
            forma_pagamento=FormaPagamento(existente.forma_pagamento.value)
            if existente.forma_pagamento
            else FormaPagamento.OUTRO,
            observacao=dto.observacao.strip() if dto.observacao else None,
            observacao_quitacao=existente.observacao_quitacao,
        )

        salvo = self._repository.update(titulo)
        return _para_response_dto(salvo)


class ListarTitulosUseCase:
    """Use case para listagem de titulos financeiros."""

    def __init__(self, repository: TituloRepository) -> None:
        self._repository = repository

    def execute(
        self,
        escritorio_id: int,
        filtro: FiltroTitulosDTO | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[TituloResponseDTO]:
        """Lista titulos de um escritorio com filtros opcionais."""
        if filtro is None:
            filtro = FiltroTitulosDTO()

        filtro_validado = FiltroTitulosDTO(
            empresa_id=filtro.empresa_id,
            texto=filtro.texto.strip().lower() if filtro.texto else None,
            categoria=filtro.categoria,
            tipo=filtro.tipo,
            status=filtro.status,
            data_vencimento_inicio=filtro.data_vencimento_inicio,
            data_vencimento_fim=filtro.data_vencimento_fim,
            situacao_vencimento=filtro.situacao_vencimento,
        )

        if (
            filtro_validado.data_vencimento_inicio is not None
            and filtro_validado.data_vencimento_fim is not None
            and filtro_validado.data_vencimento_inicio
            > filtro_validado.data_vencimento_fim
        ):
            raise ValueError(
                "Data de vencimento inicial nao pode ser posterior a data final."
            )

        titulos = self._repository.list_filtered(
            escritorio_id=escritorio_id,
            filtro=filtro_validado,
            skip=skip,
            limit=limit,
        )
        return [_para_response_dto(t) for t in titulos]


class ObterTituloUseCase:
    """Use case para obter titulo por ID."""

    def __init__(self, repository: TituloRepository) -> None:
        self._repository = repository

    def execute(self, id: int) -> TituloResponseDTO:
        """Obtem titulo por ID.

        Raises:
            ValueError: se titulo nao existe.
        """
        titulo = self._repository.get_by_id(id)
        if titulo is None:
            raise ValueError(f"Titulo com ID {id} nao encontrado.")
        return _para_response_dto(titulo)


class QuitarTituloUseCase:
    """Use case para quitacao integral de titulo."""

    def __init__(
        self,
        repository: TituloRepository,
        conta_repository: ContaBancariaRepository | None = None,
    ) -> None:
        self._repository = repository
        self._conta_repository = conta_repository

    def execute(self, dto: QuitarTituloDTO) -> TituloResponseDTO:
        """Marca um titulo como pago com dados da quitacao.

        Raises:
            ValueError: se titulo nao existe, empresa divergente,
                        conta invalida/inativa/de outra empresa,
                        valor invalido ou titulo nao estiver aberto.
        """
        existente = self._repository.get_by_id(dto.id)
        if existente is None:
            raise ValueError(f"Titulo com ID {dto.id} nao encontrado.")

        if dto.empresa_id is not None and dto.empresa_id != existente.empresa_id:
            raise ValueError(
                "Titulo nao pertence a empresa ativa."
            )

        if dto.conta_bancaria_id is None or dto.conta_bancaria_id <= 0:
            raise ValueError("Conta bancaria deve ser informada.")

        conta = None
        if self._conta_repository is not None:
            conta = self._conta_repository.get_by_id(dto.conta_bancaria_id)
            if conta is None:
                raise ValueError("Conta bancaria nao encontrada.")
            if conta.empresa_id != existente.empresa_id:
                raise ValueError(
                    "Conta bancaria nao pertence a empresa do titulo."
                )
            if not conta.ativo:
                raise ValueError("Conta bancaria esta inativa.")

        forma_pagamento = _parse_forma_pagamento(dto.forma_pagamento)

        titulo = Titulo(
            id=existente.id,
            escritorio_id=existente.escritorio_id,
            empresa_id=existente.empresa_id,
            plano_conta_id=existente.plano_conta_id,
            centro_custo_id=existente.centro_custo_id,
            numero_documento=existente.numero_documento,
            codigo_barras=existente.codigo_barras,
            categoria=existente.categoria,
            descricao=existente.descricao,
            tipo=existente.tipo,
            status=existente.status,
            valor=existente.valor,
            valor_pago=existente.valor_pago,
            data_emissao=existente.data_emissao,
            data_vencimento=existente.data_vencimento,
            data_quitacao=existente.data_quitacao,
            conta_bancaria_id=existente.conta_bancaria_id,
            forma_pagamento=existente.forma_pagamento,
            observacao=existente.observacao,
            observacao_quitacao=existente.observacao_quitacao,
        )

        titulo.quitar(
            data_quitacao=dto.data_quitacao,
            valor_pago=dto.valor_pago,
            conta_bancaria_id=dto.conta_bancaria_id,
            forma_pagamento=forma_pagamento,
            observacao_quitacao=dto.observacao_quitacao,
        )

        salvo = self._repository.update(titulo)
        return _para_response_dto(salvo)


class CancelarTituloUseCase:
    """Use case para cancelamento de titulo."""

    def __init__(self, repository: TituloRepository) -> None:
        self._repository = repository

    def execute(self, id: int) -> TituloResponseDTO:
        """Marca um titulo como cancelado.

        Raises:
            ValueError: se titulo nao existe.
        """
        existente = self._repository.get_by_id(id)
        if existente is None:
            raise ValueError(f"Titulo com ID {id} nao encontrado.")

        titulo = Titulo(
            id=existente.id,
            escritorio_id=existente.escritorio_id,
            empresa_id=existente.empresa_id,
            plano_conta_id=existente.plano_conta_id,
            centro_custo_id=existente.centro_custo_id,
            numero_documento=existente.numero_documento,
            codigo_barras=existente.codigo_barras,
            categoria=existente.categoria,
            descricao=existente.descricao,
            tipo=existente.tipo,
            status=StatusTitulo.CANCELADO,
            valor=existente.valor,
            valor_pago=None,
            data_emissao=existente.data_emissao,
            data_vencimento=existente.data_vencimento,
            data_quitacao=None,
            conta_bancaria_id=None,
            forma_pagamento=FormaPagamento.OUTRO,
            observacao=existente.observacao,
        )

        salvo = self._repository.update(titulo)
        return _para_response_dto(salvo)


class RemoverTituloUseCase:
    """Use case para remocao de titulo."""

    def __init__(self, repository: TituloRepository) -> None:
        self._repository = repository

    def execute(self, id: int) -> None:
        """Remove um titulo por ID.

        Raises:
            ValueError: se titulo nao existe.
        """
        existente = self._repository.get_by_id(id)
        if existente is None:
            raise ValueError(f"Titulo com ID {id} nao encontrado.")
        self._repository.delete(id)
