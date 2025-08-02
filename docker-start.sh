#!/bin/bash

# RAG 系統 Docker 啟動腳本

echo "🚀 啟動 RAG 智能問答系統 (Docker)"

# 檢查 .env 文件是否存在
if [ ! -f .env ]; then
    echo "❌ 錯誤: .env 文件不存在"
    echo "請複製 env.example 為 .env 並填入您的 API 金鑰"
    echo "cp env.example .env"
    exit 1
fi

# 檢查必要的環境變數
source .env
if [ -z "$PINECONE_API_KEY" ] || [ "$PINECONE_API_KEY" = "your_pinecone_api_key_here" ]; then
    echo "❌ 錯誤: 請在 .env 文件中設定 PINECONE_API_KEY"
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "your_gemini_api_key_here" ]; then
    echo "❌ 錯誤: 請在 .env 文件中設定 GEMINI_API_KEY"
    exit 1
fi

echo "✅ 環境變數檢查通過"

# 構建並啟動容器
echo "🔨 構建 Docker 映像..."
docker-compose build

echo "🚀 啟動服務..."
docker-compose up -d

echo "⏳ 等待服務啟動..."
sleep 10

# 檢查服務狀態
if docker-compose ps | grep -q "Up"; then
    echo "✅ 服務已成功啟動"
    echo "🌍 訪問地址: http://localhost:5002"
    echo "📊 健康檢查: http://localhost:5002/health"
    echo ""
    echo "📝 常用命令:"
    echo "  查看日誌: docker-compose logs -f"
    echo "  停止服務: docker-compose down"
    echo "  重啟服務: docker-compose restart"
else
    echo "❌ 服務啟動失敗"
    echo "請檢查日誌: docker-compose logs"
    exit 1
fi 