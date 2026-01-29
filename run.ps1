# 가상환경 활성화 및 서버 실행 스크립트
.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "$PWD\src;$env:PYTHONPATH"
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
