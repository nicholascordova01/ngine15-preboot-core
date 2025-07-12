#!/usr/bin/env bash

# 1) always run from the repo root
cd "$(dirname "$0")"

SCRIPT="engine15_autonomous.py"
LOG="chloe.log"
PYTHON=$(which python3)

while true; do
  # 2) only restart if not already running
  if ! pgrep -f "$PYTHON $SCRIPT" > /dev/null; then
    echo "[WATCHDOG] $(date +'%F %T') Chloe runtime not detected. Launching now…" | tee -a "$LOG"
    nohup $PYTHON "$SCRIPT" >> "$LOG" 2>&1 &
  fi
  sleep 15
done