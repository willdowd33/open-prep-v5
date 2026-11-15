@echo off
cd /d "%~dp0"
if not exist .venv (
  py -3 -m venv .venv
)
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist .env (
  copy .env.example .env
  echo.
  echo IMPORTANT: Open .env in Notepad and paste your OpenAI API key.
  echo Then save it and run start_windows.bat again.
  pause
  exit /b
)
python -m uvicorn app:app --host 0.0.0.0 --port 8000
