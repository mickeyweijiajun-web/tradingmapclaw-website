#!/bin/bash
# TMC ops migration installer — idempotent. Run on the Mac mini.
# Installs: public_pipeline, tools_bypass, public-content tree, ops_migration
# scripts + launchd jobs ai.tmc.daily_brief / ai.tmc.weekly_content.
# Does NOT touch existing ai.hermes.* / com.hermes.* jobs, memory.sqlite,
# stocks.yaml, or any internal scheduler state.
set -euo pipefail
PY="$HOME/.hermes/hermes-agent/venv/bin/python"
STAGE="$(cd "$(dirname "$0")/.." && pwd)"   # mac-staging/
TMC="$HOME/TradingMapClaw"

echo "== 1. public pipeline =="
mkdir -p "$TMC/public_pipeline" "$TMC/tools_bypass"
cp -R "$HOME/Downloads/tmc-handoff-bundle/pipeline/"* "$TMC/public_pipeline/"
if [ -d "$TMC/public_pipeline/audit" ]; then
  cp -R "$TMC/public_pipeline/audit/"* "$TMC/tools_bypass/" && rm -rf "$TMC/public_pipeline/audit"
fi

echo "== 2. public-content tree =="
mkdir -p "$TMC/public-content"/{inbox,normalized,redacted,drafts,approved,rejected,archive,logs}

echo "== 3. ops_migration scripts =="
mkdir -p "$TMC/ops_migration/logs"
cp "$STAGE/ops_migration/daily_brief.py" "$STAGE/ops_migration/weekly_content.py" "$TMC/ops_migration/"
cp "$STAGE/ops_migration/FACTS.md" "$TMC/ops_migration/FACTS.md"
chmod +x "$TMC/ops_migration/"*.py

echo "== 4. pipeline tests =="
cd "$TMC/public_pipeline"
$PY -m py_compile _common.py public_content_exporter.py compliance_filter.py radar_page_builder.py content_repurpose.py publish_gate.py
$PY tests/run_all.py | tail -3

echo "== 5. launchd jobs (ai.tmc.*) =="
mkdir -p "$HOME/Library/LaunchAgents"
for j in ai.tmc.daily_brief ai.tmc.weekly_content; do
  cp "$STAGE/launchd/$j.plist" "$HOME/Library/LaunchAgents/$j.plist"
  launchctl unload "$HOME/Library/LaunchAgents/$j.plist" 2>/dev/null || true
  launchctl load "$HOME/Library/LaunchAgents/$j.plist"
done
launchctl list | grep ai.tmc || true

echo "== DONE. Next: dry-runs =="
echo "  $PY $TMC/ops_migration/daily_brief.py --dry-run"
echo "  $PY $TMC/ops_migration/weekly_content.py --dry-run"
