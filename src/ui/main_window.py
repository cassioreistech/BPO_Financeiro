"""Janela principal do sistema com navegacao lateral."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

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
from ui.views.centros_custo_view import CentrosCustoView
from ui.views.contadores_view import ContadoresView
from ui.views.contas_bancarias_view import ContasBancariasView
from ui.views.dashboard_view import DashboardView
from ui.views.empresas_view import EmpresasView
from ui.views.escritorios_view import EscritoriosView
from ui.views.plano_contas_view import PlanoContasView
from ui.views.titulos_view import TitulosView


class MainWindow(QMainWindow):
    """Janela principal com navegacao lateral entre telas."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Sistema BPO Financeiro")
        self.resize(1200, 720)
        self.showMaximized()

        self._configurar_repositories()
        self._montar_ui()
        self._navegar(0)

    def _configurar_repositories(self) -> None:
        self._esc_repo = SQLiteEscritorioRepository(SessionLocal)
        self._emp_repo = SQLiteEmpresaRepository(SessionLocal)
        self._cont_repo = SQLiteContadorRepository(SessionLocal)
        self._conta_repo = SQLiteContaBancariaRepository(SessionLocal)
        self._plano_repo = SQLitePlanoContaRepository(SessionLocal)
        self._titulo_repo = SQLiteTituloRepository(SessionLocal)
        self._centro_repo = SQLiteCentroCustoRepository(SessionLocal)

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
            ListarPlanoContaUseCase,
            ObterPlanoContaUseCase,
            RemoverPlanoContaUseCase,
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

        self._uc_listar_titulo = ListarTitulosUseCase(self._titulo_repo)
        self._uc_obter_titulo = ObterTituloUseCase(self._titulo_repo)
        self._uc_criar_titulo = CadastrarTituloUseCase(self._titulo_repo)
        self._uc_editar_titulo = EditarTituloUseCase(self._titulo_repo)
        self._uc_quitar_titulo = QuitarTituloUseCase(self._titulo_repo)
        self._uc_cancelar_titulo = CancelarTituloUseCase(self._titulo_repo)
        self._uc_remover_titulo = RemoverTituloUseCase(self._titulo_repo)

        self._uc_listar_centro = ListarCentroCustoUseCase(self._centro_repo)
        self._uc_obter_centro = ObterCentroCustoUseCase(self._centro_repo)
        self._uc_criar_centro = CadastrarCentroCustoUseCase(self._centro_repo)
        self._uc_editar_centro = EditarCentroCustoUseCase(self._centro_repo)
        self._uc_desativar_centro = DesativarCentroCustoUseCase(self._centro_repo)

    def _montar_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        principal = QHBoxLayout(central)
        principal.setContentsMargins(0, 0, 0, 0)
        principal.setSpacing(0)

        sidebar = self._criar_sidebar()
        principal.addWidget(sidebar)

        self._stack = QStackedWidget()
        self._stack.setObjectName("contentArea")
        self._criar_paginas()
        principal.addWidget(self._stack)

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
            ("  Empresas", 1),
            ("  Plano de Contas", 2),
            ("  Centros de Custo", 3),
            ("  Titulos", 4),
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
            ("    Contas Bancarias", 2),
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
        if indice in (0, 1, 3, 4):  # indices dos itens principais
            self._colapsar_config()
        self._stack.setCurrentIndex(indice)
        for i, btn in enumerate(self._botoes_nav):
            btn.setProperty("active", i == indice)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _criar_paginas(self) -> None:
        # 0: Dashboard
        self._view_dashboard = DashboardView(
            resumo=self._uc_resumo_dashboard,
            listar_empresas=self._uc_listar_emp,
        )
        self._stack.addWidget(self._view_dashboard)

        # 1: Empresas
        self._view_empresas = EmpresasView(
            listar=self._uc_listar_emp,
            obter=self._uc_obter_emp,
            criar=self._uc_criar_emp,
            editar=self._uc_editar_emp,
            excluir=self._uc_excluir_emp,
            listar_escritorios=self._uc_listar_esc,
        )
        self._stack.addWidget(self._view_empresas)

        # 2: Contas Bancarias
        self._view_contas = ContasBancariasView(
            listar=self._uc_listar_conta,
            obter=self._uc_obter_conta,
            criar=self._uc_criar_conta,
            editar=self._uc_editar_conta,
            desativar=self._uc_desativar_conta,
            listar_empresas=self._uc_listar_emp,
        )
        self._stack.addWidget(self._view_contas)

        # 3: Plano de Contas
        self._view_plano = PlanoContasView(
            listar=self._uc_listar_plano,
            obter=self._uc_obter_plano,
            criar=self._uc_criar_plano,
            editar=self._uc_editar_plano,
            remover=self._uc_remover_plano,
            listar_escritorios=self._uc_listar_esc,
        )
        self._stack.addWidget(self._view_plano)

        # 4: Centros de Custo
        self._view_centros = CentrosCustoView(
            listar=self._uc_listar_centro,
            obter=self._uc_obter_centro,
            criar=self._uc_criar_centro,
            editar=self._uc_editar_centro,
            desativar=self._uc_desativar_centro,
            listar_empresas=self._uc_listar_emp,
        )
        self._stack.addWidget(self._view_centros)

        # 4: Titulos
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
            listar_plano_contas=self._uc_listar_plano,
            listar_centros_custo=self._uc_listar_centro,
        )
        self._stack.addWidget(self._view_titulos)

        # 6: Escritorios (config)
        self._view_escritorios = EscritoriosView(
            listar=self._uc_listar_esc,
            obter=self._uc_obter_esc,
            criar=self._uc_criar_esc,
            editar=self._uc_editar_esc,
            excluir=self._uc_excluir_esc,
        )
        self._stack.addWidget(self._view_escritorios)

        # 7: Contadores (config)
        self._view_contadores = ContadoresView(
            listar=self._uc_listar_cont,
            obter=self._uc_obter_cont,
            criar=self._uc_criar_cont,
            editar=self._uc_editar_cont,
            excluir=self._uc_excluir_cont,
            listar_escritorios=self._uc_listar_esc,
        )
        self._stack.addWidget(self._view_contadores)
