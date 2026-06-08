# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[
        '.',
        'pages',
        'pages/Account Manager',
        'pages/CRUD',
        'pages/Career Toolkit',
        'pages/Dashboard',
        'pages/Dashboard Admin',
        'pages/Live Discovery',
        'pages/Job Archive',
        'pages/Job Posting',
        'pages/Modul',
        'pages/Modul/Scraper',
        'pages/Skill Manager',
    ],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('database/Database Permanen/Skill Dictionary', 'database/Database Permanen/Skill Dictionary')
    ],
    hiddenimports=[
        # Scraper modules
        'scrapper_main',
        'scraper_glints',
        'playwright',

        # Root-level modules
        'login',
        'app_router',

        # Account Manager
        'create_user',

        # Dashboard
        'dashboard',

        # Dashboard Admin
        'dashboard_admin',

        # Live Discovery
        'live_discovery',

        # Job Archive
        'job_archive',

        # Career Toolkit
        'toolkit_main',
        'ui_components',
        'data_manager',
        'flow_layout',
        'gemini_api',
        'pdf_generator',

        # Job Posting
        'job_posting',
        'job_posting_page',
        'job_card_widget',
        'skill_tag_input',
        'constants',

        # Skill Manager
        'skill_manager',

        # CRUD
        'Create',
        'Read',
        'Update',
        'Delete',
        'Shared',

        # Modul (top-level names)
        'modul_database',
        'modul_antarmuka_pengguna',
        'modul_kategorisasi',
        'modul_pengolahan_data',
        'modul_visualisasi_data',

        # Modul (as package)
        'Modul',
        'Modul.modul_database',
        'Modul.modul_antarmuka_pengguna',
        'Modul.modul_kategorisasi',
        'Modul.modul_pengolahan_data',
        'Modul.modul_visualisasi_data',

        # Career Toolkit as package
        'Career Toolkit',

        # Job Posting as package
        'Job Posting',

        # CRUD as package
        'CRUD',
        'CRUD.Create',
        'CRUD.Read',
        'CRUD.Update',
        'CRUD.Delete',
        'CRUD.Shared',

        # Common third-party
        'PyQt5',
        'PyQt5.QtWidgets',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.backends.backend_qt5agg',
        'numpy',
        'json',
        'os',
        're',
        'datetime',
        'collections',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='GottaJob',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GottaJob',
)
