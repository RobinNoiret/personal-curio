# -*- mode: python ; coding: utf-8 -*-
"""
Fichier de configuration PyInstaller pour Curio
"""
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collecter les modules nécessaires
hiddenimports = [
    'customtkinter',
    'PIL._tkinter_finder',
]

# Collecter tous les data files de customtkinter
datas = collect_data_files('customtkinter')

# Ajouter les assets de l'application
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Assets (fonts, images, etc.)
        ('assets', 'assets'),
        # Config par défaut (optionnel, pour avoir un exemple)
        ('config', 'config'),
    ] + datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Curio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Pas de console pour une application GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/Curio_optimized.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Curio',
)
