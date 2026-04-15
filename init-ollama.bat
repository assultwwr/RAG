@echo off
echo ========================================
echo Ollama 模型初始化脚本
echo ========================================
echo.

echo [1/2] 正在下载 qwen3-embedding 模型...
docker exec -it ollama-service ollama pull qwen3-embedding
if errorlevel 1 (
    echo 错误：qwen3-embedding 下载失败
    pause
    exit /b 1
)

echo.
echo [2/2] 正在下载 qwen2.5:7b 模型...
docker exec -it ollama-service ollama pull qwen2.5:7b
if errorlevel 1 (
    echo 错误：qwen2.5:7b 下载失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 模型下载完成！
echo ========================================
echo.
echo 可以使用以下命令启动服务：
echo docker-compose up -d
echo.
pause
