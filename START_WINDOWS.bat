@echo off
call .venv\Scripts\activate.bat
python check_setup.py
start http://127.0.0.1:8000
uvicorn backend.main:app --host 127.0.0.1 --port 8000
