#!/usr/bin/env bash
cd /e/game-dev-team || exit 1
git fetch -q origin docs/phase0-gdd 2>/dev/null
old=$(git rev-parse origin/docs/phase0-gdd:reports/Agents/INBOX.md 2>/dev/null)
while true; do
  sleep 90
  git fetch -q origin docs/phase0-gdd 2>/dev/null
  new=$(git rev-parse origin/docs/phase0-gdd:reports/Agents/INBOX.md 2>/dev/null)
  if [ "$new" != "$old" ]; then
    git pull -q --no-rebase --no-edit origin docs/phase0-gdd 2>/dev/null
    echo "РИНАТ написал в INBOX.md — прочитать и среагировать"; exit 0
  fi
done
