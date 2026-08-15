"""Janela principal do sistema com navegacao lateral."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from application.dto.contexto_empresa_dto import EmpresaAtivaDTO
from application.services.empresa_context_service import EmpresaContextService
from infrastructure.database import SessionLocal
from infrastructure.database.repositories.sqlite_centro_custo_repository import (
    SQLiteCentroCustoRepository,
)
from infrastructure.database.repositories.sqlite_conta_bancaria_repository import (
    SQLiteContaBancariaRepository,
)
from infrastructure.database.repositories.sqlite_contador_repository import (
    SQLiteContadorRepository,
)
from infrastructure.database.repositories.sqlite_empresa_repository import (
    SQLiteEmpresaRepository,
)
from infrastructure.database.repositories.sqlite_escritorio_repository import (
    SQLiteEscritorioRepository,
)
from infrastructure.database.repositories.sqlite_plano_conta_repository import (
    SQLitePlanoContaRepository,
)
from infrastructure.database.repositories.sqlite_titulo_repository import (
    SQLiteTituloRepository,
)
from ui.views.alertas_titulos_view import AlertasTitulosView
from ui.views.contadores_view import ContadoresView
from ui.views.contas_bancarias_view import ContasBancariasView
from ui.views.dashboard_view import DashboardView
from ui.views.empresas_view import EmpresasView
from ui.views.escritorios_view import EscritoriosView
from ui.views.titulos_view import TitulosView


class MainWindow(QMainWindow):
    """Janela principal com navegacao lateral entre telas."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Sistema BPO Financeiro")
        self.resize(1200, 720)
        self.showMaximized()

        self._contexto_empresa = EmpresaContextService()
        self._configurar_repositories()
        self._carregar_empresas_iniciais()
        self._montar_ui()
        self._navegar(0)

    def _carregar_empresas_iniciais(self) -> None:
        """Carrega empresas e define a primeira como ativa, se houver."""
        try:
            empresas = self._uc_listar_emp.execute(skip=0, limit=1000)
        except Exception:
            empresas = []

        self._empresas: dict[int, EmpresaAtivaDTO] = {}
        for emp in empresas:
            if emp.id is not None:
                self._empresas[emp.id] = EmpresaAtivaDTO(
                    id=emp.id,
                    nome_fantasia=emp.nome_fantasia,
                    razao_social=emp.razao_social,
                    cnpj=emp.cnpj,
                )

        if self._empresas:
            primeira_id = next(iter(self._empresas))
            self._contexto_empresa.set_empresa_ativa(
                primeira_id, self._empresas[primeira_id]
            )

    def _configurar_repositories(self) -> None:
        self._esc_repo = SQLiteEscritorioRepository(SessionLocal)
        self._emp_repo = SQLiteEmpresaRepository(SessionLocal)
        self._cont_repo = SQLiteContadorRepository(SessionLocal)
        self._conta_repo = SQLiteContaBancariaRepository(SessionLocal)
        self._plano_repo = SQLitePlanoContaRepository(SessionLocal)
        self._titulo_repo = SQLiteTituloRepository(SessionLocal)
        self._centro_repo = SQLiteCentroCustoRepository(SessionLocal)

        from application.use_cases.alerta_titulo_use_cases import (
            ObterDashboardAlertasTitulosUseCase,
        )
        from application.use_cases.centro_custo_use_cases import (
            CadastrarCentroCustoUseCase,
            DesativarCentroCustoUseCase,
            EditarCentroCustoUseCase,
            ListarCentroCustoUseCase,
            ObterCentroCustoUseCase,
        )
        from application.use_cases.conta_bancaria_use_cases import (
            CadastrarContaBancariaUseCase,
            DesativarContaBancariaUseCase,
            EditarContaBancariaUseCase,
            ListarContasBancariasUseCase,
            ObterContaBancariaUseCase,
        )
        from application.use_cases.contador_use_cases import (
            CadastrarContadorUseCase,
            EditarContadorUseCase,
            ExcluirContadorUseCase,
            ListarContadoresUseCase,
            ObterContadorUseCase,
        )
        from application.use_cases.dashboard_use_cases import (
            ResumoFinanceiroUseCase,
        )
        from application.use_cases.empresa_use_cases import (
            CadastrarEmpresaUseCase,
            EditarEmpresaUseCase,
            ExcluirEmpresaUseCase,
            ListarEmpresasUseCase,
            ObterEmpresaUseCase,
        )
        from application.use_cases.escritorio_use_cases import (
            CriarEscritorioUseCase,
            EditarEscritorioUseCase,
            ExcluirEscritorioUseCase,
            ListarEscritoriosUseCase,
            ObterEscritorioUseCase,
        )
        from application.use_cases.plano_conta_use_cases import (
            CadastrarPlanoContaUseCase,
            EditarPlanoContaUseCase,
            GarantirContaPadraoUseCase,
            ListarPlanoContaUseCase,
            ObterPlanoContaUseCase,
            RemoverPlanoContaUseCase,
        )
        from application.use_cases.relatorio_titulos_use_cases import (
            FluxoCaixaUseCase,
            ProjecaoFinanceiraUseCase,
            RelatorioTitulosUseCase,
        )
        from application.use_cases.titulo_use_cases import (
            CadastrarTituloUseCase,
            CancelarTituloUseCase,
            EditarTituloUseCase,
            ListarTitulosUseCase,
            ObterTituloUseCase,
            QuitarTituloUseCase,
            RemoverTituloUseCase,
        )

        self._uc_listar_esc = ListarEscritoriosUseCase(self._esc_repo)
        self._uc_obter_esc = ObterEscritorioUseCase(self._esc_repo)
        self._uc_resumo_dashboard = ResumoFinanceiroUseCase(self._titulo_repo)
        self._uc_criar_esc = CriarEscritorioUseCase(self._esc_repo)
        self._uc_editar_esc = EditarEscritorioUseCase(self._esc_repo)
        self._uc_excluir_esc = ExcluirEscritorioUseCase(self._esc_repo)

        self._uc_listar_emp = ListarEmpresasUseCase(self._emp_repo)
        self._uc_obter_emp = ObterEmpresaUseCase(self._emp_repo)
        self._uc_criar_emp = CadastrarEmpresaUseCase(self._emp_repo)
        self._uc_editar_emp = EditarEmpresaUseCase(self._emp_repo)
        self._uc_excluir_emp = ExcluirEmpresaUseCase(self._emp_repo)

        self._uc_listar_cont = ListarContadoresUseCase(self._cont_repo)
        self._uc_obter_cont = ObterContadorUseCase(self._cont_repo)
        self._uc_criar_cont = CadastrarContadorUseCase(self._cont_repo)
        self._uc_editar_cont = EditarContadorUseCase(self._cont_repo)
        self._uc_excluir_cont = ExcluirContadorUseCase(self._cont_repo)

        self._uc_listar_conta = ListarContasBancariasUseCase(self._conta_repo)
        self._uc_obter_conta = ObterContaBancariaUseCase(self._conta_repo)
        self._uc_criar_conta = CadastrarContaBancariaUseCase(self._conta_repo)
        self._uc_editar_conta = EditarContaBancariaUseCase(self._conta_repo)
        self._uc_desativar_conta = DesativarContaBancariaUseCase(self._conta_repo)

        self._uc_listar_plano = ListarPlanoContaUseCase(self._plano_repo)
        self._uc_obter_plano = ObterPlanoContaUseCase(self._plano_repo)
        self._uc_criar_plano = CadastrarPlanoContaUseCase(self._plano_repo)
        self._uc_editar_plano = EditarPlanoContaUseCase(self._plano_repo)
        self._uc_remover_plano = RemoverPlanoContaUseCase(self._plano_repo)
        self._uc_garantir_conta_padrao = GarantirContaPadraoUseCase(
            self._plano_repo
        )

        self._uc_listar_titulo = ListarTitulosUseCase(self._titulo_repo)
        self._uc_obter_titulo = ObterTituloUseCase(self._titulo_repo)
        self._uc_dashboard_alertas = ObterDashboardAlertasTitulosUseCase(
            self._titulo_repo
        )
        self._uc_criar_titulo = CadastrarTituloUseCase(self._titulo_repo)
        self._uc_editar_titulo = EditarTituloUseCase(self._titulo_repo)
        self._uc_quitar_titulo = QuitarTituloUseCase(
            self._titulo_repo, self._conta_repo
        )
        self._uc_cancelar_titulo = CancelarTituloUseCase(self._titulo_repo)
        self._uc_remover_titulo = RemoverTituloUseCase(self._titulo_repo)
        self._uc_relatorio_titulos = RelatorioTitulosUseCase(self._titulo_repo)
        self._uc_fluxo_caixa = FluxoCaixaUseCase(self._titulo_repo)
        self._uc_projecao_financeira = ProjecaoFinanceiraUseCase(
            self._titulo_repo
        )

        self._uc_listar_centro = ListarCentroCustoUseCase(self._centro_repo)
        self._uc_obter_centro = ObterCentroCustoUseCase(self._centro_repo)
        self._uc_criar_centro = CadastrarCentroCustoUseCase(self._centro_repo)
        self._uc_editar_centro = EditarCentroCustoUseCase(self._centro_repo)
        self._uc_desativar_centro = DesativarCentroCustoUseCase(self._centro_repo)

    def _montar_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        principal = QVBoxLayout(central)
        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(0)

        header = self._criar_header_empresa()
        principal.addWidget(header)

        corpo = QHBoxLayout()
        corpo.setContentsMargins(0, 0, 0, 0)
        corpo.setSpacing(0)

        sidebar = self._criar_sidebar()
        corpo.addWidget(sidebar)

        self._stack = QStackedWidget()
        self._stack.setObjectName("contentArea")
        self._criar_paginas()
        corpo.addWidget(self._stack)

        principal.addLayout(corpo)
        self._atualizar_label_empresa_ativa()

    def _criar_header_empresa(self) -> QWidget:
        """Cria o cabecalho superior com seletor de empresa ativa."""
        header = QWidget()
        header.setObjectName("headerEmpresa")
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        self._label_empresa_ativa = QLabel("Empresa ativa: —")
        self._label_empresa_ativa.setObjectName("labelEmpresaAtiva")
        layout.addWidget(self._label_empresa_ativa)
        layout.addStretch()

        layout.addWidget(QLabel("Trocar empresa:"))
        self._combo_empresa_ativa = QComboBox()
        self._combo_empresa_ativa.setMinimumWidth(300)
        self._combo_empresa_ativa.addItem("Selecione...", None)
        for empresa in self._empresas.values():
            texto = f"{empresa.nome_fantasia} ({self._formatar_cnpj(empresa.cnpj)})"
            self._combo_empresa_ativa.addItem(texto, empresa.id)

        empresa_ativa = self._contexto_empresa.get_empresa_ativa()
        if empresa_ativa is not None:
            idx = self._combo_empresa_ativa.findData(empresa_ativa)
            if idx >= 0:
                self._combo_empresa_ativa.setCurrentIndex(idx)

        self._combo_empresa_ativa.currentIndexChanged.connect(
            self._empresa_ativa_alterada
        )
        layout.addWidget(self._combo_empresa_ativa)

        return header

    @staticmethod
    def _formatar_cnpj(cnpj: str) -> str:
        """Formata CNPJ para exibicao."""
        if len(cnpj) != 14:
            return cnpj
        return (
            f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/"
            f"{cnpj[8:12]}-{cnpj[12:]}"
        )

    def _empresa_ativa_alterada(self) -> None:
        empresa_id = self._combo_empresa_ativa.currentData()
        if empresa_id is None:
            return
        empresa = self._empresas.get(empresa_id)
        self._contexto_empresa.set_empresa_ativa(empresa_id, empresa)
        self._atualizar_label_empresa_ativa()
        self._recarregar_telas_operacionais()

    def _atualizar_label_empresa_ativa(self) -> None:
        empresa = self._contexto_empresa.get_empresa_ativa_detalhes()
        if empresa is None:
            self._label_empresa_ativa.setText("Empresa ativa: —")
            return
        texto = (
            f"Empresa ativa: {empresa.nome_fantasia} — "
            f"CNPJ {self._formatar_cnpj(empresa.cnpj)}"
        )
        self._label_empresa_ativa.setText(texto)

    def _recarregar_telas_operacionais(self) -> None:
        if hasattr(self, "_view_titulos"):
            self._view_titulos.carregar_empresa_ativa()
        if hasattr(self, "_view_contas"):
            self._view_contas.carregar_empresa_ativa()
        if hasattr(self, "_view_dashboard"):
            self._view_dashboard.carregar_empresa_ativa()
        if hasattr(self, "_view_alertas"):
            self._view_alertas.atualizar()

    def _atualizar_dashboard_e_alertas(self) -> None:
        """Atualiza Dashboard e Alertas apos operacao de titulos."""
        if hasattr(self, "_view_dashboard"):
            self._view_dashboard.atualizar()
        if hasattr(self, "_view_alertas"):
            self._view_alertas.atualizar()

    def _criar_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(220)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        logo = QPushButton("BPO Financeiro")
        logo.setObjectName("logo")
        logo.setEnabled(False)
        layout.addWidget(logo)

        sep = QWidget()
        sep.setFixedHeight(1)
        sep.setObjectName("separator")
        layout.addWidget(sep)

        self._botoes_nav: list[QPushButton] = []

        # Itens principais (operacionais)
        main_items = [
            ("  Dashboard", 0),
            ("  Titulos", 1),
            ("  Alertas", 2),
        ]

        for texto, indice in main_items:
            btn = QPushButton(texto)
            btn.setObjectName("navButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=indice: self._navegar(i))
            layout.addWidget(btn)
            self._botoes_nav.append(btn)

        # Separador antes de Configurações
        sep2 = QWidget()
        sep2.setFixedHeight(1)
        sep2.setObjectName("separator")
        layout.addWidget(sep2)

        # Botão Configurações (expansível)
        self._btn_config = QPushButton("  Configurações")
        self._btn_config.setObjectName("navButton")
        self._btn_config.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_config.setCheckable(True)
        self._btn_config.clicked.connect(self._toggle_config)
        layout.addWidget(self._btn_config)

        # Container dos itens de configuração (inicialmente oculto)
        self._config_container = QWidget()
        self._config_container.setVisible(False)
        config_layout = QVBoxLayout(self._config_container)
        config_layout.setContentsMargins(16, 8, 0, 8)
        config_layout.setSpacing(4)

        config_items = [
            ("    Contas Bancarias", 3),
            ("    Empresas", 4),
            ("    Escritorios", 5),
            ("    Contadores", 6),
        ]

        self._botoes_config: list[QPushButton] = []
        for texto, indice in config_items:
            btn = QPushButton(texto)
            btn.setObjectName("navButtonConfig")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, i=indice: self._navegar(i))
            config_layout.addWidget(btn)
            self._botoes_config.append(btn)

        layout.addWidget(self._config_container)
        layout.addStretch()

        return sidebar

    def _toggle_config(self) -> None:
        """Alterna visibilidade do menu de configuracoes."""
        visivel = self._config_container.isVisible()
        self._config_container.setVisible(not visivel)
        self._btn_config.setChecked(not visivel)

    def _colapsar_config(self) -> None:
        """Colapsa o menu de configuracoes se estiver aberto."""
        if self._config_container.isVisible():
            self._config_container.setVisible(False)
            self._btn_config.setChecked(False)

    def _navegar(self, indice: int) -> None:
        # Colapsa config ao navegar para item principal
        if indice in (0, 1, 2):  # indices dos itens principais
            self._colapsar_config()
        self._stack.setCurrentIndex(indice)

        for i, btn in enumerate(self._botoes_nav):
            btn.setProperty("active", i == indice)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        for i, btn in enumerate(self._botoes_config):
            btn.setProperty("active", i == (indice - 3))
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _criar_paginas(self) -> None:
        # 0: Dashboard
        self._view_dashboard = DashboardView(
            resumo=self._uc_resumo_dashboard,
            listar_escritorios=self._uc_listar_esc,
            listar_empresas=self._uc_listar_emp,
            contexto_empresa=self._contexto_empresa,
        )
        self._stack.addWidget(self._view_dashboard)

        # 1: Titulos
        self._view_titulos = TitulosView(
            listar=self._uc_listar_titulo,
            obter=self._uc_obter_titulo,
            criar=self._uc_criar_titulo,
            editar=self._uc_editar_titulo,
            quitar=self._uc_quitar_titulo,
            cancelar=self._uc_cancelar_titulo,
            remover=self._uc_remover_titulo,
            listar_escritorios=self._uc_listar_esc,
            listar_empresas=self._uc_listar_emp,
            listar_contas_bancarias=self._uc_listar_conta,
            garantir_conta_padrao=self._uc_garantir_conta_padrao,
            relatorio_titulos=self._uc_relatorio_titulos,
            fluxo_caixa=self._uc_fluxo_caixa,
            projecao_financeira=self._uc_projecao_financeira,
            contexto_empresa=self._contexto_empresa,
            on_titulo_quitado=self._atualizar_dashboard_e_alertas,
        )
        self._stack.addWidget(self._view_titulos)

        # 2: Alertas
        self._view_alertas = AlertasTitulosView(
            dashboard_use_case=self._uc_dashboard_alertas,
            listar_empresas=self._uc_listar_emp,
            listar_escritorios=self._uc_listar_esc,
            contexto_empresa=self._contexto_empresa,
        )
        self._stack.addWidget(self._view_alertas)

        # 3: Contas Bancarias (config)
        self._view_contas = ContasBancariasView(
            listar=self._uc_listar_conta,
            obter=self._uc_obter_conta,
            criar=self._uc_criar_conta,
            editar=self._uc_editar_conta,
            desativar=self._uc_desativar_conta,
            listar_empresas=self._uc_listar_emp,
            contexto_empresa=self._contexto_empresa,
        )
        self._stack.addWidget(self._view_contas)

        # 4: Empresas (config)
        self._view_empresas = EmpresasView(
            listar=self._uc_listar_emp,
            obter=self._uc_obter_emp,
            criar=self._uc_criar_emp,
            editar=self._uc_editar_emp,
            excluir=self._uc_excluir_emp,
            listar_escritorios=self._uc_listar_esc,
        )
        self._stack.addWidget(self._view_empresas)

        # 4: Escritorios (config)
        self._view_escritorios = EscritoriosView(
            listar=self._uc_listar_esc,
            obter=self._uc_obter_esc,
            criar=self._uc_criar_esc,
            editar=self._uc_editar_esc,
            excluir=self._uc_excluir_esc,
        )
        self._stack.addWidget(self._view_escritorios)

        # 5: Contadores (config)
        self._view_contadores = ContadoresView(
            listar=self._uc_listar_cont,
            obter=self._uc_obter_cont,
            criar=self._uc_criar_cont,
            editar=self._uc_editar_cont,
            excluir=self._uc_excluir_cont,
            listar_escritorios=self._uc_listar_esc,
        )
        self._stack.addWidget(self._view_contadores)
