#!/usr/bin/env bash
# build_app.sh — bundle AI Indexer as a standalone macOS .app via py2app
#
# Uses the project's existing venv (venv/) for all Python/pip operations.
#
# Usage:
#   ./build_app.sh            # full standalone build  → dist/AI Indexer.app
#   ./build_app.sh --alias    # alias mode (fast, for development)
#   ./build_app.sh --open     # build + open the app immediately after
#   ./build_app.sh --dmg      # build + package into a .dmg (requires create-dmg)

set -euo pipefail

# ── Locate project root and venv ──────────────────────────────────────────────
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$REPO_DIR/venv"
PYTHON="$VENV_DIR/bin/python"  # use python -m pip to avoid broken shebangs in relocated venvs

APP_NAME="AI Indexer"
DIST_DIR="$REPO_DIR/dist"
BUILD_DIR="$REPO_DIR/build"
APP_PATH="$DIST_DIR/$APP_NAME.app"

ALIAS_MODE=false
OPEN_AFTER=false
MAKE_DMG=false

for arg in "$@"; do
  case "$arg" in
    --alias)  ALIAS_MODE=true ;;
    --open)   OPEN_AFTER=true ;;
    --dmg)    MAKE_DMG=true ;;
    --help|-h)
      echo "Usage: $0 [--alias] [--open] [--dmg]"
      echo "  --alias   Fast alias build (edits reflected live, not distributable)"
      echo "  --open    Launch the app after building"
      echo "  --dmg     Package the .app into a .dmg (requires: brew install create-dmg)"
      exit 0
      ;;
    *)
      echo "Unknown option: $arg  (use --help)" >&2
      exit 1
      ;;
  esac
done

# ── Helpers ───────────────────────────────────────────────────────────────────
step() { echo; echo "▶  $*"; }
ok()   { echo "   ✓  $*"; }
warn() { echo "   ⚠  $*"; }

# ── Verify venv exists ────────────────────────────────────────────────────────
step "Locating venv"

if [ ! -f "$PYTHON" ]; then
  echo "ERROR: venv not found at $VENV_DIR" >&2
  echo "Create it first with:" >&2
  echo "  python3.12 -m venv venv && venv/bin/pip install -e '.[full,gui]'" >&2
  exit 1
fi
ok "venv: $VENV_DIR"
ok "Python: $($PYTHON --version)"

cd "$REPO_DIR"

# ── Ensure dependencies are present inside the venv ───────────────────────────
step "Checking dependencies in venv"

if ! "$PYTHON" -c "import PySide6" 2>/dev/null; then
  warn "PySide6 not found — installing into venv…"
  "$PYTHON" -m pip install "PySide6>=6.6" --quiet
fi
ok "PySide6 present"

if ! "$PYTHON" -c "import py2app" 2>/dev/null; then
  warn "py2app not found — installing into venv…"
  "$PYTHON" -m pip install py2app --quiet
fi
ok "py2app present"

if ! "$PYTHON" -c "import ai_indexer" 2>/dev/null; then
  warn "ai-indexer not installed in venv — installing in editable mode…"
  "$PYTHON" -m pip install -e "$REPO_DIR[full]" --quiet
fi
ok "ai-indexer present"

if [ ! -f "$REPO_DIR/assets/icon.icns" ]; then
  warn "assets/icon.icns missing — building without custom icon"
fi

# ── Clean previous build ──────────────────────────────────────────────────────
step "Cleaning previous build artefacts"
rm -rf "$DIST_DIR" "$BUILD_DIR"
ok "Cleaned dist/ and build/"

# ── Build ─────────────────────────────────────────────────────────────────────
# py2app 0.28+ rejects install_requires, but setuptools reads it from
# pyproject.toml and overwrites our explicit install_requires=[] in setup_gui.py.
# Fix: hide pyproject.toml for the duration of the build; restore it via trap
# so it is always put back even if the build fails.
PYPROJECT="$REPO_DIR/pyproject.toml"
PYPROJECT_BAK="$REPO_DIR/pyproject.toml.bak"

_restore_pyproject() {
  [ -f "$PYPROJECT_BAK" ] && mv "$PYPROJECT_BAK" "$PYPROJECT"
}
trap '_restore_pyproject' EXIT INT TERM

mv "$PYPROJECT" "$PYPROJECT_BAK"

if [ "$ALIAS_MODE" = true ]; then
  step "Building in ALIAS mode (development — not distributable)"
  "$PYTHON" "$REPO_DIR/setup_gui.py" py2app -A 2>&1
else
  step "Building STANDALONE bundle (distributable)"
  "$PYTHON" "$REPO_DIR/setup_gui.py" py2app 2>&1
fi

_restore_pyproject
trap - EXIT INT TERM

if [ ! -d "$APP_PATH" ]; then
  echo "ERROR: Build failed — $APP_PATH not created." >&2
  exit 1
fi

APP_SIZE=$(du -sh "$APP_PATH" 2>/dev/null | cut -f1)
ok "Bundle created: $APP_PATH  ($APP_SIZE)"

# ── Code-sign (ad-hoc, for local use) ────────────────────────────────────────
if [ "$ALIAS_MODE" = false ] && command -v codesign &>/dev/null; then
  step "Ad-hoc code signing"
  codesign --force --deep --sign - "$APP_PATH" 2>&1 || warn "codesign failed (non-fatal)"
  ok "Signed (ad-hoc)"
fi

# ── DMG packaging ─────────────────────────────────────────────────────────────
if [ "$MAKE_DMG" = true ]; then
  step "Packaging into .dmg"
  if ! command -v create-dmg &>/dev/null; then
    echo "ERROR: create-dmg not found. Install with: brew install create-dmg" >&2
    exit 1
  fi
  VERSION=$("$PYTHON" -c "from ai_indexer import __version__; print(__version__)")
  DMG_PATH="$DIST_DIR/AI-Indexer-$VERSION.dmg"
  create-dmg \
    --volname "AI Indexer $VERSION" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "$APP_NAME.app" 175 190 \
    --hide-extension "$APP_NAME.app" \
    --app-drop-link 425 190 \
    "$DMG_PATH" \
    "$DIST_DIR/"
  ok "DMG criado: $DMG_PATH"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
echo
echo "Build complete."
if [ "$ALIAS_MODE" = true ]; then
  echo "  Mode:   alias (development)"
else
  echo "  Mode:   standalone"
fi
echo "  App:    $APP_PATH"

if [ "$OPEN_AFTER" = true ]; then
  step "Launching $APP_NAME…"
  open "$APP_PATH"
fi
