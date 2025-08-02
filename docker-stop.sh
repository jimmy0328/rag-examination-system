#!/bin/bash

# RAG 系統 Docker 停止腳本

echo "🛑 停止 RAG 智能問答系統 (Docker)"

# 停止所有服務
echo "⏹️  停止 Docker Compose 服務..."
docker-compose down

# 檢查是否還有容器在運行
if docker ps | grep -q "rag-final-report"; then
    echo "⚠️  發現仍在運行的容器，強制停止..."
    docker stop $(docker ps -q --filter "name=rag-final-report")
    docker rm $(docker ps -aq --filter "name=rag-final-report")
fi

echo "✅ 所有服務已停止"
echo ""
echo "📝 常用命令:"
echo "  啟動服務: ./docker-start.sh"
echo "  查看日誌: docker-compose logs"
echo "  重新構建: docker-compose up --build -d" 