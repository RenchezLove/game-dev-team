#!/usr/bin/env bash
cd /e/game-dev-team || exit 1
while true; do
  ts=$(date '+%Y-%m-%d %H:%M:%S')
  status=$(cat reports/Agents/gl_heartbeat_status.txt 2>/dev/null)
  {
    echo "## [$ts] game-lead heartbeat 💓"
    echo "$status"
    echo ""
    echo "---"
    echo ""
  } >> reports/Agents/HEARTBEAT.md
  git add reports/Agents/ 2>/dev/null
  git commit -q -m "heartbeat $ts" 2>/dev/null
  git push -q origin docs/phase0-gdd 2>/dev/null
  sleep 600
done
