#!/usr/bin/env bash
# install.sh — loan-article-skill 跨平台自动安装
# 用法:
#   ./install.sh                # auto-detect platform
#   ./install.sh --platform all
#   ./install.sh --platform claude
#   ./install.sh --platform cursor
#   ./install.sh --dry-run

set -e

SKILL_NAME="loan-article-skill"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PLATFORM="auto"
DRY_RUN="false"
INSTALL_ALL="false"

for arg in "$@"; do
  case $arg in
    --platform=*) PLATFORM="${arg#*=}" ;;
    --platform) shift; PLATFORM="$1"; shift ;;
    --all) INSTALL_ALL="true" ;;
    --dry-run) DRY_RUN="true" ;;
    *) ;;
  esac
done

run_install() {
  local target="$1"
  local desc="$2"
  if [ "$DRY_RUN" = "true" ]; then
    echo "[DRY-RUN] Would install to: $target"
  else
    mkdir -p "$target"
    cp -R "$SCRIPT_DIR/." "$target/"
    echo "[OK] Installed to: $target  ($desc)"
  fi
}

install_claude() {
  run_install "$HOME/.claude/skills/$SKILL_NAME" "Claude Code"
}

install_copilot() {
  run_install "$HOME/.copilot/skills/$SKILL_NAME" "GitHub Copilot CLI"
}

install_cursor() {
  if [ -d ".cursor" ]; then
    run_install ".cursor/skills/$SKILL_NAME" "Cursor (project)"
  else
    echo "[SKIP] Cursor: .cursor/ not in current dir; please run from project root"
  fi
}

install_codex() {
  run_install "$HOME/.agents/skills/$SKILL_NAME" "Codex CLI (universal path)"
}

install_gemini() {
  run_install "$HOME/.gemini/skills/$SKILL_NAME" "Gemini CLI"
}

install_kiro() {
  if [ -d ".kiro" ]; then
    run_install ".kiro/skills/$SKILL_NAME" "Kiro (project)"
  else
    run_install "$HOME/.kiro/skills/$SKILL_NAME" "Kiro (global)"
  fi
}

install_goose() {
  run_install "$HOME/.config/goose/skills/$SKILL_NAME" "Goose"
}

install_opencode() {
  run_install "$HOME/.config/opencode/skills/$SKILL_NAME" "OpenCode"
}

install_cline() {
  run_install "$HOME/.cline/skills/$SKILL_NAME" "Cline"
}

install_universal() {
  run_install "$HOME/.agents/skills/$SKILL_NAME" "Universal agent path"
}

# Auto-detect
if [ "$PLATFORM" = "auto" ]; then
  if [ "$INSTALL_ALL" = "true" ]; then
    PLATFORM="all"
  else
    if [ -d "$HOME/.claude" ]; then
      PLATFORM="claude"
    elif [ -d "$HOME/.copilot" ]; then
      PLATFORM="copilot"
    elif [ -d "$HOME/.gemini" ]; then
      PLATFORM="gemini"
    elif [ -d "$HOME/.config/opencode" ]; then
      PLATFORM="opencode"
    else
      PLATFORM="universal"
    fi
  fi
fi

echo "loan-article-skill :: installing"
echo "  platform: $PLATFORM"
echo "  source:   $SCRIPT_DIR"
echo ""

case "$PLATFORM" in
  claude) install_claude ;;
  copilot) install_copilot ;;
  cursor) install_cursor ;;
  codex|universal) install_universal ;;
  gemini) install_gemini ;;
  kiro) install_kiro ;;
  goose) install_goose ;;
  opencode) install_opencode ;;
  cline) install_cline ;;
  all)
    install_claude
    install_copilot
    install_universal
    install_gemini
    install_goose
    install_opencode
    install_cline
    if [ -d ".cursor" ]; then install_cursor; fi
    if [ -d ".kiro" ]; then install_kiro; fi
    ;;
  *)
    echo "Unknown platform: $PLATFORM"
    echo "Valid: claude, copilot, cursor, codex, gemini, kiro, goose, opencode, cline, universal, all"
    exit 1
    ;;
esac

echo ""
echo "Installation complete."
echo ""
echo "Next steps:"
echo "  1. Open a new session in your agent"
echo "  2. Type: /loan-article-skill 帮我写北京房产抵押的文章"
echo ""
