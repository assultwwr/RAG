@echo off
chcp 65001 >nul
echo ========================================
echo   RAG知识库 - Streamlit 前端启动中...
echo ========================================
echo.
cd /d "%~dp0"
echo 正在启动 Streamlit 前端...
echo 访问地址：http://localhost:8501
echo.
streamlit run app/main.py
pause