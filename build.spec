# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from pathlib import Path

# Diretório do projeto (onde está o spec)
PROJECT_DIR = Path.cwd()

# Adiciona src ao path para imports
sys.path.insert(0, str(PROJECT_DIR / "src"))

block_cipher = None

# Coleta arquivos de dados necessários
datas = [
    # Inclui arquivos de configuração se existirem
]

# Módulos ocultos que PyInstaller pode não detectar automaticamente
hiddenimports = [
    "PySide6.QtCore",
    "PySide6.QtWidgets",
    "PySide6.QtGui",
    "PySide6.QtSql",
    "sqlalchemy",
    "sqlalchemy.orm",
    "sqlalchemy.dialects.sqlite",
    "pydantic",
    "pydantic.v1",
    "structlog",
    "fpdf",
    "fpdf.fonts",
    "fpdf.enums",
    "fpdf.errors",
    "fpdf.util",
    "fpdf.fpdf",
    "fpdf.html",
    "fpdf.image_parsing",
    "fpdf.output",
    "fpdf.pages",
    "fpdf.parser",
    "fpdf.progressive",
    "fpdf.syntax",
    "fpdf.text",
    "fpdf.ttfonts",
    "fpdf.vector",
    "fpdf.xmp",
    "reportlab",
    "reportlab.lib",
    "reportlab.lib.pagesizes",
    "reportlab.lib.styles",
    "reportlab.lib.units",
    "reportlab.lib.enums",
    "reportlab.lib.colors",
    "reportlab.platypus",
    "reportlab.platypus.doctemplate",
    "reportlab.platypus.paragraph",
    "reportlab.platypus.tables",
    "reportlab.platypus.flowables",
    "reportlab.pdfbase",
    "reportlab.pdfbase.ttfonts",
    "reportlab.pdfbase.pdfmetrics",
    "reportlab.pdfgen.canvas",
    "reportlab.graphics",
    "domain",
    "domain.value_objects",
    "domain.value_objects.telefone",
    "domain.value_objects.email",
    "domain.value_objects.crc",
    "domain.value_objects.cnpj",
    "domain.value_objects.banco_codigo",
    "domain.enums",
    "domain.enums.situacao_vencimento",
    "domain.enums.regime_tributario",
    "domain.enums.forma_pagamento",
    "domain.enums.categoria_titulo",
    "application",
    "application.use_cases",
    "application.use_cases.titulo_use_cases",
    "application.use_cases.relatorio_titulos_use_cases",
    "application.use_cases.plano_conta_use_cases",
    "application.use_cases.escritorio_use_cases",
    "application.use_cases.empresa_use_cases",
    "application.use_cases.dashboard_use_cases",
    "application.use_cases.conta_bancaria_use_cases",
    "application.use_cases.contador_use_cases",
    "application.use_cases.centro_custo_use_cases",
    "application.use_cases.alerta_titulo_use_cases",
    "application.ports",
    "application.ports.titulo_repository",
    "application.ports.plano_conta_repository",
    "application.ports.escritorio_repository",
    "application.ports.empresa_repository",
    "application.ports.conta_bancaria_repository",
    "application.ports.contador_repository",
    "application.ports.centro_custo_repository",
    "application.services",
    "application.services.empresa_context_service",
    "application.services.backup_service",
    "application.dto",
    "application.dto.titulo_dto",
    "application.dto.plano_conta_dto",
    "infrastructure",
    "infrastructure.database",
    "infrastructure.database.schema_upgrade",
    "infrastructure.reports",
    "infrastructure.reports.pdf_gerador",
    "infrastructure.reports.pdf_report_generator",
    "infrastructure.logging_config",
    "ui",
    "ui.main_window",
    "ui.styles",
    "ui.views",
    "ui.views.titulo_form_view",
    "ui.views.titulos_view",
    "ui.views.table_helpers",
    "ui.views.table_delegate",
    "ui.views.status_formatter",
    "ui.views.relatorio_dialog",
    "ui.views.quitacao_dialog",
    "ui.views.plano_conta_form_view",
    "ui.views.plano_contas_view",
    "ui.views.escritorio_form_view",
    "ui.views.escritorios_view",
    "ui.views.empresa_form_view",
    "ui.views.empresas_view",
    "ui.views.dashboard_view",
    "ui.views.conta_bancaria_form_view",
    "ui.views.contas_bancarias_view",
    "ui.views.contador_form_view",
    "ui.views.contadores_view",
    "ui.views.centro_custo_form_view",
    "ui.views.centros_custo_view",
    "ui.views.alertas_titulos_view",
    "ui.views.formatadores",
]

# Análise do entrypoint
a = Analysis(
    ["src/main.py"],
    pathex=[str(PROJECT_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tests",
        "pytest",
        "ruff",
        "black",
        "mypy",
        "setuptools",
        "pip",
        "wheel",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Filtra módulos desnecessários para reduzir tamanho
a.datas = [x for x in a.datas if not any(ex in x[0] for ex in [".pyc", "__pycache__", ".git", "tests", ".venv", ".mypy_cache", ".pytest_cache", ".opencode"])]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="SistemaBPOFinanceiro",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI app - sem console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Adicione um .ico se tiver
    version_file="version_info.txt",
)

# Cria pasta de distribuição
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="SistemaBPOFinanceiro",
)