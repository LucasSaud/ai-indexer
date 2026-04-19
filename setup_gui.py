"""py2app build script for the AI Indexer macOS application bundle.

Usage
-----
# Alias mode (fast iteration — edits reflected immediately):
    python setup_gui.py py2app -A
    open "dist/AI Indexer.app"

# Standalone distributable build:
    python setup_gui.py py2app
    open "dist/AI Indexer.app"
"""

from __future__ import annotations

from pathlib import Path

from setuptools import setup

APP = [str(Path("src/ai_indexer/gui/app.py"))]

_ICON = "assets/icon.icns"
_icon_exists = Path(_ICON).exists()

OPTIONS: dict = {
    "argv_emulation": False,  # Must be False for PySide6 — True breaks the event loop
    "packages": ["ai_indexer", "PySide6"],
    "includes": [
        "PySide6",
        "shiboken6",
        "ai_indexer",
        "ai_indexer.gui",
        "ai_indexer.gui.components",
        "ai_indexer.core",
        "ai_indexer.parsers",
        "ai_indexer.exporters",
        "ai_indexer.utils",
        "ai_indexer.mcp",
    ],
    "plist": {
        "CFBundleName": "AI Indexer",
        "CFBundleDisplayName": "AI Indexer",
        "CFBundleIdentifier": "com.aiindexer.app",
        "CFBundleVersion": "0.0.7",
        "CFBundleShortVersionString": "0.0.7",
        "NSRequiresAquaSystemAppearance": False,
        "NSDesktopFolderUsageDescription": (
            "Required to analyse project files located on the Desktop."
        ),
        "NSDocumentsFolderUsageDescription": (
            "Required to analyse project files located in Documents."
        ),
        "NSDownloadsFolderUsageDescription": (
            "Required to analyse project files located in Downloads."
        ),
        "NSAppleEventsUsageDescription": (
            "AI Indexer uses Apple Events for file-open operations."
        ),
        "NSHumanReadableCopyright": "MIT License",
    },
}

if _icon_exists:
    OPTIONS["iconfile"] = _ICON
else:
    print(
        "WARNING: assets/icon.icns not found — building without custom icon.\n"
        "Place a valid .icns file at assets/icon.icns and rebuild."
    )

setup(
    app=APP,
    name="AI Indexer",
    # install_requires=[] overrides what setuptools reads from pyproject.toml.
    # py2app 0.28+ raises an error if install_requires is non-empty.
    install_requires=[],
    options={"py2app": OPTIONS},
    # setup_requires removed — py2app must already be installed in the venv.
)
