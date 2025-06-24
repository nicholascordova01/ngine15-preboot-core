#!/bin/bash
echo "[SETUP] Installing Python core dependencies..."
pip install --user -r requirements.txt
echo "[SETUP] Core environment ready. Note: NLU/torch libraries require manual installation if supported."
