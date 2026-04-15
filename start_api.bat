@echo off
chcp 65001 >nul
echo ========================================
echo   RAG 知识库 - FastAPI 服务器启动中...
echo ========================================
echo.
cd /d "%~dp0"
echo 正在启动 API 服务器...
echo 访问地址：http://localhost:8000
echo API 文档：http://localhost:8000/docs
echo.
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
pause