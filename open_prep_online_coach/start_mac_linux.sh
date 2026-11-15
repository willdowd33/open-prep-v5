#!/usr/bin/env bash
cd "$(dirname "$0")"
if [ ! -d .venv ]; then python3 -m venv .venv; fi
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if [ ! -f .env ]; then
  cp .env.example .env
  echo "Edit .env and add your OpenAI API key, then run this script again."
  exit 0
fi
python -m uvicorn app:app --host 0.0.0.0 --port 8000
