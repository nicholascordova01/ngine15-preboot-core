#!/bin/bash
SCRIPT_TO_RUN="engine15_autonomous.py"
while true; do
  if ! pgrep -f "python3 $SCRIPT_TO_RUN"; then
    echo "[WATCHDOG] Chloe runtime not detected. Launching now..."
    nohup python3 $SCRIPT_TO_RUN &
  fi
  sleep 15
done
