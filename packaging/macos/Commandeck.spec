# PyInstaller spec for Commandeck macOS .app bundle
# Free build:  COMMANDECK_PRO=0 pyinstaller --noconfirm --clean Commandeck.spec
# Pro build:   COMMANDECK_PRO=1 pyinstaller --noconfirm --clean Commandeck.spec

import os
from pathlib import Path

ROOT = Path(SPECPATH).parent.parent  # repo root
PRO_BUILD = os.environ.get('COMMANDECK_PRO', '0') == '1'

block_cipher = None

a = Analysis(
    [str(ROOT / 'commandeck_qt' / '__main__.py')],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        # Core translations
        (str(ROOT / 'commandeck_core' / 'translations'), 'commandeck_core/translations'),
        # Qt resources: Bootstrap icons + custom icons
        (str(ROOT / 'data' / 'resources' / 'bootstrap'), 'data/resources/bootstrap'),
        (str(ROOT / 'data' / 'resources' / 'icons'), 'data/resources/icons'),
        # QSS stylesheets
        (str(ROOT / 'commandeck_qt' / 'resources' / 'style'), 'commandeck_qt/resources/style'),
    ],
    hiddenimports=[
        'fabric',
        'paramiko',
        # fabric -> invoke.context does `from unittest.mock import Mock` at
        # module top level, so the SSH stack cannot import without unittest.
        'unittest',
        'unittest.mock',
        'tomli_w',
        'keyring.backends.macOS',
        'commandeck_core.platform.macos',
    ] + ([
        'cryptography',
        'bcrypt',
        'commandeck_core.pro',
        'commandeck_core.pro.license',
        'commandeck_core.pro.mcp_server',
        'commandeck_core.pro.models',
        'commandeck_core.pro.models.machine',
        'commandeck_core.pro.models.execution_profile',
        'commandeck_core.pro.services',
        'commandeck_core.pro.services.executor_pro',
        'commandeck_core.pro.services.ssh_service',
        'commandeck_core.pro.services.ssh_key_service',
    ] if PRO_BUILD else []),
    excludes=[
        'gi',
        'gtk',
        'PySide6.Qt3DAnimation',
        'PySide6.Qt3DCore',
        'PySide6.Qt3DExtras',
        'PySide6.Qt3DInput',
        'PySide6.Qt3DLogic',
        'PySide6.Qt3DRender',
        'PySide6.QtBluetooth',
        'PySide6.QtCharts',
        'PySide6.QtDataVisualization',
        'PySide6.QtMultimedia',
        'PySide6.QtMultimediaWidgets',
        'PySide6.QtNfc',
        'PySide6.QtPdf',
        'PySide6.QtPdfWidgets',
        'PySide6.QtPositioning',
        'PySide6.QtQuick',
        'PySide6.QtQuick3D',
        'PySide6.QtQuickControls2',
        'PySide6.QtQuickWidgets',
        'PySide6.QtRemoteObjects',
        'PySide6.QtSensors',
        'PySide6.QtSerialBus',
        'PySide6.QtSerialPort',
        'PySide6.QtSpatialAudio',
        'PySide6.QtTextToSpeech',
        'PySide6.QtWebChannel',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineQuick',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebSockets',
        'tkinter',
        'test',
    ] + ([] if PRO_BUILD else [
        'commandeck_core.pro',
        'commandeck_core.pro.license',
        'commandeck_core.pro.mcp_server',
        'commandeck_core.pro.models',
        'commandeck_core.pro.models.machine',
        'commandeck_core.pro.models.execution_profile',
        'commandeck_core.pro.services',
        'commandeck_core.pro.services.executor_pro',
        'commandeck_core.pro.services.ssh_service',
        'commandeck_core.pro.services.ssh_key_service',
    ]),
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Commandeck',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Commandeck',
)

app = BUNDLE(
    coll,
    name='Commandeck.app',
    icon='Commandeck.icns',
    bundle_identifier='io.github.neurocontrarian.commandeck',
    info_plist={
        'CFBundleName': 'Commandeck',
        'CFBundleDisplayName': 'Commandeck',
        'CFBundleIdentifier': 'io.github.neurocontrarian.commandeck',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'CFBundlePackageType': 'APPL',
        'CFBundleSignature': '????',
        'LSMinimumSystemVersion': '12.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
        'NSAppleEventsUsageDescription':
            'Commandeck uses AppleEvents to open Terminal.app for terminal-mode commands.',
        'LSApplicationCategoryType': 'public.app-category.utilities',
        'NSHumanReadableCopyright': '© 2026 neurocontrarian',
    },
)
