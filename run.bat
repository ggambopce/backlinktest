@echo off
call .venv\Scripts\activate.bat
set PYTHONPATH=%CD%\src
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
