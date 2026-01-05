# build/backend_server.spec（修正版・完全版）
# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_data_files

block_cipher = None

# プロジェクトルート
project_root = os.path.abspath(os.path.join(SPECPATH, '..'))
backend_dir = os.path.join(project_root, 'backend')

# llama-cpp-pythonの全データを収集
datas_llama, binaries_llama, hiddenimports_llama = collect_all('llama_cpp')

# 追加の隠れた依存関係
additional_hiddenimports = [
    # FastAPI関連
    'fastapi',
    'fastapi.routing',
    'fastapi.params',
    'fastapi.datastructures',
    
    # Uvicorn関連
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.protocols.websockets.wsproto_impl',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    
    # SQLAlchemy関連
    'sqlalchemy',
    'sqlalchemy.ext',
    'sqlalchemy.ext.declarative',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.sql.default_comparator',
    
    # Pydantic関連
    'pydantic',
    'pydantic.fields',
    'pydantic.main',
    
    # システム情報
    'cpuinfo',
    'psutil',
    
    # ワードクラウド関連
    'janome',
    'janome.tokenizer',
    'wordcloud',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageFont',
    
    # その他
    'starlette',
    'starlette.routing',
    'starlette.middleware',
    'starlette.middleware.cors',
]

a = Analysis(
    [os.path.join(backend_dir, 'main.py')],
    pathex=[backend_dir],
    binaries=binaries_llama,
    datas=datas_llama,
    hiddenimports=hiddenimports_llama + additional_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 不要なパッケージを除外（サイズ削減）
        'matplotlib',
        'numpy.distutils',
        'scipy',
        'pandas',
        'notebook',
        'IPython',
        'tkinter',
        'test',
        'tests',
        'pytest',
        'setuptools',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ========================================
# 重要: --onedir モードに変更
# ========================================
exe = EXE(
    pyz,
    a.scripts,
    [],  # ← ここを空にする（--onedir モード）
    exclude_binaries=True,  # ← 追加
    name='backend_server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # コンソール表示（デバッグ用）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# ========================================
# COLLECT を追加（--onedir モード用）
# ========================================
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='backend_server',
)