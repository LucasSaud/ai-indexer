# PyInstaller spec for AI Indexer GUI
# Run via build_app.sh or directly:
#   pyinstaller ai_indexer_gui.spec

from PyInstaller.building.api import COLLECT, EXE, BUNDLE, PYZ
from PyInstaller.building.build_main import Analysis

block_cipher = None

# ── Modules we do NOT need from PySide6 ──────────────────────────────────────
# We only use QtCore + QtGui + QtWidgets. Excluding everything else saves ~900 MB.
_QT_EXCLUDES = [
    # Web engine — by far the largest (~500 MB)
    "PySide6.QtWebEngineWidgets",
    "PySide6.QtWebEngineCore",
    "PySide6.QtWebEngineQuick",
    "PySide6.QtWebChannel",
    # 3D
    "PySide6.Qt3DCore",
    "PySide6.Qt3DInput",
    "PySide6.Qt3DLogic",
    "PySide6.Qt3DRender",
    "PySide6.Qt3DAnimation",
    "PySide6.Qt3DExtras",
    # QML / Quick
    "PySide6.QtQml",
    "PySide6.QtQuick",
    "PySide6.QtQuickWidgets",
    "PySide6.QtQuickControls2",
    # Charts & data viz
    "PySide6.QtCharts",
    "PySide6.QtDataVisualization",
    # Multimedia
    "PySide6.QtMultimedia",
    "PySide6.QtMultimediaWidgets",
    # PDF
    "PySide6.QtPdf",
    "PySide6.QtPdfWidgets",
    # Sensors / location
    "PySide6.QtBluetooth",
    "PySide6.QtNfc",
    "PySide6.QtSensors",
    "PySide6.QtLocation",
    "PySide6.QtPositioning",
    # Misc extras
    "PySide6.QtRemoteObjects",
    "PySide6.QtScxml",
    "PySide6.QtStateMachine",
    "PySide6.QtVirtualKeyboard",
    "PySide6.QtSql",
    "PySide6.QtTest",
    "PySide6.QtConcurrent",
    "PySide6.QtDesigner",
    "PySide6.QtHelp",
    "PySide6.QtUiTools",
]

a = Analysis(
    ["src/ai_indexer/gui/app.py"],
    pathex=["src"],
    binaries=[],
    datas=[
        ("templates", "templates"),
        ("assets",    "assets"),
    ],
    hiddenimports=[
        "ai_indexer",
        "ai_indexer.gui",
        "ai_indexer.gui.app",
        "ai_indexer.gui.main_window",
        "ai_indexer.gui.engine_worker",
        "ai_indexer.gui.components",
        "ai_indexer.gui.components.project_panel",
        "ai_indexer.gui.components.files_table",
        "ai_indexer.gui.components.hotspots_panel",
        "ai_indexer.gui.components.warnings_panel",
        "ai_indexer.gui.components.log_console",
        "ai_indexer.gui.components.output_panel",
        "ai_indexer.core",
        "ai_indexer.core.engine",
        "ai_indexer.core.models",
        "ai_indexer.core.cache",
        "ai_indexer.parsers",
        "ai_indexer.parsers.base",
        "ai_indexer.parsers.python",
        "ai_indexer.parsers.typescript",
        "ai_indexer.exporters",
        "ai_indexer.exporters.toon",
        "ai_indexer.exporters.html",
        "ai_indexer.exporters.dsl",
        "ai_indexer.exporters.xml_exporter",
        "ai_indexer.utils",
        "ai_indexer.utils.config",
        "ai_indexer.utils.io",
        "ai_indexer.main",
        "pathspec",
        "pydantic",
        "rich",
    ],
    excludes=_QT_EXCLUDES + [
        "tkinter",
        "unittest",
        "email",
        "html",
        "http",
        "urllib",
        "xmlrpc",
        "pydoc",
        "doctest",
        "optparse",
        "difflib",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AI Indexer",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,           # UPX can break Qt dylibs on macOS
    console=False,       # no terminal window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="AI Indexer",
)

app = BUNDLE(
    coll,
    name="AI Indexer.app",
    icon="assets/icon.icns" if __import__("pathlib").Path("assets/icon.icns").exists() else None,
    bundle_identifier="com.aiindexer.app",
    version="0.0.7",
    info_plist={
        "CFBundleName":            "AI Indexer",
        "CFBundleDisplayName":     "AI Indexer",
        "CFBundleVersion":         "0.0.7",
        "CFBundleShortVersionString": "0.0.7",
        "NSRequiresAquaSystemAppearance": False,
        "NSHighResolutionCapable": True,
        "NSDesktopFolderUsageDescription":
            "Required to analyse project files on the Desktop.",
        "NSDocumentsFolderUsageDescription":
            "Required to analyse project files in Documents.",
        "NSDownloadsFolderUsageDescription":
            "Required to analyse project files in Downloads.",
        "NSAppleEventsUsageDescription":
            "AI Indexer uses Apple Events for file-open operations.",
        "NSHumanReadableCopyright": "MIT License",
    },
)
