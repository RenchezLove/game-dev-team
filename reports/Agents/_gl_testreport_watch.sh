#!/usr/bin/env bash
cd /e/game-dev-team || exit 1
f=reports/Agents/TEST_REPORT.md
# триггер только на значимые маркеры, не на лёгкие пульсы
cnt() { grep -cE '🟡 ВЗЯЛ|🔵.*(PASS|FAIL|Этап)|ИТОГ:.*(PASS|FAIL)' "$f" 2>/dev/null; }
old=$(cnt)
while true; do
  sleep 60
  new=$(cnt)
  if [ "$new" != "$old" ]; then echo "СБОРЩИК: значимый отчёт в TEST_REPORT (взял/PASS/FAIL) — прочитать"; exit 0; fi
done
