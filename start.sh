#!/usr/bin/env bash
set -e

echo "=================================================================="
echo "    LPU-RISK-01 - Explainable Academic Early-Warning System"
echo "=================================================================="

# Ensure database tables and demo seed data exist
python -m backend.app.scripts.seed_demo_data

# Launch FastAPI via Uvicorn (listening on 0.0.0.0 for container / cloud hosting)
PORT="${PORT:-8000}"
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port "$PORT"
