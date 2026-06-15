#!/usr/bin/env bash
cd /e/game-dev-team || exit 1
f=reports/Agents/TEST_REPORT.md
old=$(md5sum "$f" 2>/dev/null | cut -d' ' -f1)
while true; do
  sleep 60
  new=$(md5sum "$f" 2>/dev/null | cut -d' ' -f1)
  if [ "$new" != "$old" ]; then
    echo "СБОРЩИК ОБНОВИЛ TEST_REPORT.md (был $old, стал $new) — прочитать и среагировать"
    exit 0
  fi
done
