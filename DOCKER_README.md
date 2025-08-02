# Docker 部署指南

本指南將幫助您使用 Docker Compose 快速部署 RAG 智能問答系統。

## 前置需求

- Docker Desktop 或 Docker Engine
- Docker Compose
- 有效的 Pinecone API 金鑰
- 有效的 Gemini API 金鑰

## 快速開始

### 1. 設定環境變數

```bash
# 複製環境變數範例
cp env.example .env

# 編輯 .env 文件，填入您的 API 金鑰
nano .env
```

確保 `.env` 文件包含以下內容：

```env
PINECONE_API_KEY=your_actual_pinecone_api_key
PINECONE_ENV=us-east-1
PINECONE_INDEX_NAME=text-chunks-index
GEMINI_API_KEY=your_actual_gemini_api_key
```

### 2. 啟動服務

```bash
# 使用啟動腳本（推薦）
./docker-start.sh

# 或手動執行
docker-compose up -d
```

### 3. 訪問應用程式

打開瀏覽器訪問：http://localhost:5002

## 常用命令

### 服務管理

```bash
# 啟動服務
docker-compose up -d

# 停止服務
docker-compose down

# 重啟服務
docker-compose restart

# 查看服務狀態
docker-compose ps
```

### 日誌查看

```bash
# 查看所有服務日誌
docker-compose logs

# 實時查看日誌
docker-compose logs -f

# 查看特定服務日誌
docker-compose logs rag-app
```

### 容器管理

```bash
# 進入容器
docker-compose exec rag-app bash

# 重新構建映像
docker-compose build

# 重新構建並啟動
docker-compose up --build -d
```

### 資料管理

```bash
# 備份 data 目錄
docker cp rag-final-report:/app/data ./backup_data

# 恢復 data 目錄
docker cp ./backup_data/. rag-final-report:/app/data
```

## 配置選項

### 修改端口

編輯 `docker-compose.yml`：

```yaml
services:
  rag-app:
    ports:
      - "8080:5002"  # 將主機端口改為 8080
```

### 添加環境變數

編輯 `docker-compose.yml`：

```yaml
services:
  rag-app:
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=False
      - APP_HOST=0.0.0.0
      - APP_PORT=5002
      - CUSTOM_VAR=value  # 添加自定義變數
```

### 掛載額外目錄

編輯 `docker-compose.yml`：

```yaml
services:
  rag-app:
    volumes:
      - ./data:/app/data
      - ./static:/app/static
      - ./logs:/app/logs  # 添加日誌目錄
```

## 故障排除

### 常見問題

#### 1. 容器啟動失敗

```bash
# 查看詳細錯誤
docker-compose logs rag-app

# 檢查環境變數
docker-compose exec rag-app env | grep -E "(PINECONE|GEMINI)"
```

#### 2. API 金鑰錯誤

確保 `.env` 文件中的 API 金鑰正確：

```bash
# 檢查環境變數是否正確載入
docker-compose exec rag-app python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('PINECONE_API_KEY:', os.getenv('PINECONE_API_KEY')[:10] + '...')
print('GEMINI_API_KEY:', os.getenv('GEMINI_API_KEY')[:10] + '...')
"
```

#### 3. 端口衝突

如果端口 5002 被佔用：

```bash
# 查看端口使用情況
lsof -i :5002

# 修改 docker-compose.yml 中的端口映射
```

#### 4. 磁碟空間不足

```bash
# 清理 Docker 資源
docker system prune -a

# 查看磁碟使用情況
docker system df
```

### 健康檢查

應用程式提供健康檢查端點：

```bash
# 檢查服務健康狀態
curl http://localhost:5002/health

# 預期回應
{
  "status": "healthy",
  "rag_system_ready": true
}
```

## 生產環境部署

### 1. 安全配置

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  rag-app:
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=False
    restart: unless-stopped
    # 添加資源限制
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

### 2. 使用 Nginx 反向代理

```yaml
# docker-compose.prod.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - rag-app
```

### 3. 添加監控

```yaml
# docker-compose.prod.yml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
```

## 備份和恢復

### 備份資料

```bash
# 創建備份腳本
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# 備份 data 目錄
docker cp rag-final-report:/app/data $BACKUP_DIR/

# 備份環境變數
cp .env $BACKUP_DIR/

echo "備份完成: $BACKUP_DIR"
EOF

chmod +x backup.sh
```

### 恢復資料

```bash
# 恢復腳本
cat > restore.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=$1

if [ -z "$BACKUP_DIR" ]; then
    echo "請指定備份目錄"
    exit 1
fi

# 恢復 data 目錄
docker cp $BACKUP_DIR/data/. rag-final-report:/app/data/

# 恢復環境變數
cp $BACKUP_DIR/.env ./

echo "恢復完成"
EOF

chmod +x restore.sh
```

## 性能優化

### 1. 多階段構建

```dockerfile
# 使用多階段構建減少映像大小
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "run.py"]
```

### 2. 快取優化

```yaml
# docker-compose.yml
services:
  rag-app:
    build:
      context: .
      cache_from:
        - rag-app:latest
```

## 開發環境

### 使用 Docker 進行開發

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  rag-app:
    build: .
    volumes:
      - .:/app
      - /app/__pycache__
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=True
    ports:
      - "5002:5002"
```

啟動開發環境：

```bash
docker-compose -f docker-compose.dev.yml up -d
```

這樣您就可以在容器中進行開發，代碼變更會即時反映到容器中。 