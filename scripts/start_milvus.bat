@echo off
REM 启动Milvus向量数据库 (Windows)

echo 正在启动Milvus向量数据库...

REM 检查Docker是否运行
docker info >nul 2>&1
if errorlevel 1 (
    echo 错误: Docker未运行，请先启动Docker
    exit /b 1
)

REM 检查Milvus容器是否已存在
docker ps -a | findstr /C:"milvus-standalone" >nul 2>&1
if errorlevel 1 (
    echo 创建新的Milvus容器...
    docker run -d --name milvus-standalone -p 19530:19530 -p 9091:9091 milvusdb/milvus:latest
) else (
    echo Milvus容器已存在，检查运行状态...
    docker ps | findstr /C:"milvus-standalone" >nul 2>&1
    if errorlevel 1 (
        echo 启动现有Milvus容器...
        docker start milvus-standalone
    ) else (
        echo Milvus已在运行中
    )
)

echo 等待Milvus启动...
timeout /t 5 /nobreak >nul

REM 验证Milvus是否运行
docker ps | findstr /C:"milvus-standalone" >nul 2>&1
if errorlevel 1 (
    echo Milvus启动失败，请检查日志: docker logs milvus-standalone
    exit /b 1
) else (
    echo Milvus已成功启动
    echo   端口: 19530 (gRPC), 9091 (HTTP)
)


