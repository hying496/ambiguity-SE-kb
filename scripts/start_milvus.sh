#!/bin/bash
# 启动Milvus向量数据库

echo "正在启动Milvus向量数据库..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "错误: Docker未运行，请先启动Docker"
    exit 1
fi

# 检查Milvus容器是否已存在
if docker ps -a | grep -q milvus-standalone; then
    echo "Milvus容器已存在，检查运行状态..."
    if docker ps | grep -q milvus-standalone; then
        echo "Milvus已在运行中"
    else
        echo "启动现有Milvus容器..."
        docker start milvus-standalone
    fi
else
    echo "创建新的Milvus容器..."
    docker run -d --name milvus-standalone \
        -p 19530:19530 \
        -p 9091:9091 \
        milvusdb/milvus:latest
fi

echo "等待Milvus启动..."
sleep 5

# 验证Milvus是否运行
if docker ps | grep -q milvus-standalone; then
    echo "✓ Milvus已成功启动"
    echo "  端口: 19530 (gRPC), 9091 (HTTP)"
else
    echo "✗ Milvus启动失败，请检查日志: docker logs milvus-standalone"
    exit 1
fi


