# 透過RAG實現線上閱讀與考試系統

基於 Flask 的 RAG (Retrieval-Augmented Generation) 智能問答系統，整合 Pinecone 向量資料庫和 Gemini AI 模型。

DEMO: https://d6530614201f.ngrok.app/

## 📊 專案簡報

- **技術簡報**: [slides.html](slides.html) - Reveal.js 專業簡報
- **Markdown 簡報**: [PRESENTATION.md](PRESENTATION.md) - 文檔式簡報
- **專案展示頁面**: [index.html](index.html) - 響應式專案展示


## 功能特色

- 🔍 **智能檢索**: 使用 Pinecone 向量資料庫進行語義搜尋
- 🤖 **AI 生成**: 整合 Gemini AI 模型生成準確回答
- 📚 **線上閱讀**: 提供教材內容的線上閱讀功能
- 📝 **智能考試**: 基於教材內容自動生成考試題目
- ✅ **自動評分**: 支援多種題型（選擇題、填空題、簡答題、是非題）的自動評分
- 💻 **現代化介面**: 美觀的響應式 Web 介面
- 📊 **即時狀態**: 系統狀態即時監控
- 🔒 **安全配置**: 環境變數管理 API 金鑰
- 🐳 **Docker 部署**: 完整的 Docker Compose 容器化部署方案

## 系統架構

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端介面       │    │   Flask 後端    │     │   外部服務       │
│   (HTML/CSS/JS) │◄──►│   (Python)      │◄──►│   Pinecone      │
│                 │    │                 │    │   Gemini AI     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 安裝與設定

### 方法一：使用 Docker Compose（推薦）

#### 1. 下載專案

```bash
git clone <repository-url>
cd rag-examination-system 
```

#### 2. 設定環境變數

複製環境變數範例檔案：

```bash
cp env.example .env
```

編輯 `.env` 檔案，填入您的 API 金鑰：

```env
# Pinecone 配置
PINECONE_API_KEY=your_actual_pinecone_api_key
PINECONE_ENV=us-east-1
PINECONE_INDEX_NAME=text-chunks-index

# Gemini AI 配置
GEMINI_API_KEY=your_actual_gemini_api_key
```

#### 3. 使用 Docker Compose 啟動

```bash
# 使用啟動腳本（推薦）
./docker-start.sh

# 或手動執行
docker-compose up -d
```

#### 4. 訪問應用程式

應用程式將在 `http://localhost:5002` 啟動。

#### 5. 常用 Docker 命令

```bash
# 查看日誌
docker-compose logs -f

# 停止服務
docker-compose down

# 重啟服務
docker-compose restart

# 重新構建並啟動
docker-compose up --build -d
```

### 方法二：本地安裝

#### 1. 下載專案

```bash
git clone <repository-url>
cd rag-examination-system
```

#### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

#### 3. 設定環境變數

複製環境變數範例檔案：

```bash
cp env.example .env
```

編輯 `.env` 檔案，填入您的 API 金鑰：

```env
# Pinecone 配置
PINECONE_API_KEY=your_actual_pinecone_api_key
PINECONE_ENV=us-east-1
PINECONE_INDEX_NAME=text-chunks-index

# Gemini AI 配置
GEMINI_API_KEY=your_actual_gemini_api_key
```

#### 4. 準備向量資料庫

使用 `init_db.py` 將您的文件上傳到 Pinecone：

```bash
# 執行初始化腳本
python init_db.py
```

或手動處理單個文件：

```python
# 在 Python 中執行
from vectorStore import process_file
process_file('your_document.txt')  # 支援 .txt 和 .pdf
```

#### 5. 啟動應用程式

```bash
python run.py
```

應用程式將在 `http://localhost:5002` 啟動。

## 使用方式

### 1. RAG 智能問答系統

1. **開啟瀏覽器** 訪問 `http://localhost:5002`
2. **輸入問題** 在查詢框中輸入您的問題
3. **查看結果** 系統會顯示 AI 回答和相關資料來源
4. **狀態監控** 側邊欄顯示系統各組件狀態

### 2. 線上閱讀中心

1. **訪問閱讀頁面** 點擊導航欄中的「閱讀中心」
2. **選擇教材** 從下拉選單中選擇要閱讀的教材（支援 .txt 和 .pdf 格式）
3. **開始閱讀** 系統會載入並顯示教材內容
4. **搜尋功能** 使用搜尋框快速找到特定內容

### 3. 智能考試系統

1. **訪問考試頁面** 點擊導航欄中的「考試系統」
2. **選擇教材** 從下拉選單中選擇要出題的教材（支援 .txt 和 .pdf 格式）
3. **設定題數** 選擇要生成的題目數量（預設5題）
4. **生成題目** 點擊「生成考試」按鈕
5. **開始作答** 系統會顯示題目，您可以開始作答
6. **提交評分** 完成作答後點擊「提交評分」
7. **查看結果** 系統會顯示評分結果和詳細解析

#### 支援的題型

- **選擇題**: 四選一，自動評分
- **填空題**: 模糊匹配評分
- **簡答題**: AI 智能評分
- **是非題**: 自動評分

#### 考試功能特色

- ✅ 基於教材內容自動生成題目
- ✅ 多種題型支援
- ✅ 即時評分和解析
- ✅ 詳細的成績統計
- ✅ 題目隨機生成，每次考試都不同

## API 端點

### RAG 查詢端點
- **POST** `/query`
- **請求體**: `{"query": "您的問題"}`
- **回應**: 
  ```json
  {
    "success": true,
    "query": "您的問題",
    "answer": "AI 回答",
    "retrieved_chunks": [...],
    "has_context": true
  }
  ```

### 考試系統端點

#### 取得教材列表
- **GET** `/exam/files`
- **回應**:
  ```json
  {
    "success": true,
    "files": ["歷史第一冊.txt", "地理第一冊.txt", "教材.pdf"]
  }
  ```

#### 生成考試題目
- **POST** `/exam/generate`
- **請求體**: `{"file_name": "歷史第一冊.txt", "num_questions": 5}`
- **回應**:
  ```json
  {
    "success": true,
    "questions": [...],
    "total_questions": 5
  }
  ```

#### 評分考試
- **POST** `/exam/grade`
- **請求體**: `{"questions": [...], "answers": {"1": "A", "2": "答案"}}`
- **回應**:
  ```json
  {
    "success": true,
    "results": [...],
    "statistics": {
      "total_questions": 5,
      "correct_answers": 3,
      "accuracy": 60.0,
      "average_score": 6.0
    }
  }
  ```

### 閱讀中心端點

#### 讀取教材內容
- **POST** `/read/content`
- **請求體**: `{"file_name": "教材.pdf"}`
- **回應**:
  ```json
  {
    "success": true,
    "content": "教材內容...",
    "file_name": "教材.pdf"
  }
  ```

### 健康檢查端點
- **GET** `/health`
- **回應**:
  ```json
  {
    "status": "healthy",
    "rag_system_ready": true
  }
  ```

## 專案結構

```
rag-examination-system/
├── app.py                 # Flask 主應用程式
├── rag_system.py          # RAG 系統核心邏輯
├── vectorStore.py         # 向量資料庫操作
├── Retrieval.py           # 原始檢索模組
├── init_db.py             # 資料庫初始化腳本
├── run.py                 # 應用程式啟動腳本
├── requirements.txt       # Python 依賴
├── env.example           # 環境變數範例
├── README.md             # 專案說明
├── DOCKER_README.md      # Docker 部署指南
├── Dockerfile            # Docker 容器配置
├── docker-compose.yml    # Docker Compose 配置
├── docker-compose.dev.yml # 開發環境配置
├── docker-compose.prod.yml # 生產環境配置
├── docker-start.sh       # Docker 啟動腳本
├── docker-stop.sh        # Docker 停止腳本
├── .dockerignore         # Docker 忽略文件
├── nginx.conf            # Nginx 反向代理配置
├── templates/
│   ├── index.html        # 首頁 (RAG 問答系統)
│   ├── exam.html         # 考試系統頁面
│   └── read.html         # 閱讀中心頁面
├── static/
│   ├── css/
│   │   └── style.css     # 樣式檔案
│   └── js/
│       ├── app.js        # 主要 JavaScript 邏輯
│       ├── exam.js       # 考試系統 JavaScript
│       └── read.js       # 閱讀中心 JavaScript
└── data/
    ├── 歷史第一冊.txt     # 歷史教材資料
    ├── 地理第一冊.txt     # 地理教材資料
    └── 教材.pdf          # PDF 教材資料（支援）
```

## 技術棧

- **後端**: Flask, Python
- **向量資料庫**: Pinecone
- **AI 模型**: Google Gemini
- **嵌入模型**: Sentence Transformers
- **PDF 處理**: PyPDF2, pdfplumber
- **前端**: HTML5, CSS3, JavaScript (ES6+)
- **UI 框架**: Bootstrap 5
- **圖示**: Font Awesome

## 配置選項

### 調整檢索參數

在 `rag_system.py` 中修改：

```python
# 檢索的文字塊數量
result = rag_system.query(user_query, top_k=5)

# 相似度閾值
if chunk['score'] > 0.7:  # 只顯示相似度 > 70% 的結果
```

### 自定義提示詞

在 `rag_system.py` 的 `generate_prompt` 方法中修改提示詞模板。

## 故障排除

### 常見問題

1. **Pinecone 連接失敗**
   - 檢查 API 金鑰是否正確
   - 確認索引名稱是否存在
   - 檢查網路連接

2. **Gemini API 錯誤**
   - 檢查 API 金鑰是否有效
   - 確認 API 配額是否足夠
   - 檢查網路連接

3. **嵌入模型載入失敗**
   - 檢查網路連接（首次載入需要下載模型）
   - 確認磁碟空間充足

### 日誌查看

應用程式會在控制台輸出詳細日誌，包括：
- 系統初始化狀態
- 查詢處理過程
- 錯誤訊息

## 開發指南

### 添加新功能

1. 在 `rag_system.py` 中添加新的方法
2. 在 `app.py` 中添加對應的路由
3. 在前端 `app.js` 中添加 UI 邏輯
4. 更新 CSS 樣式

### 測試

```bash
# 啟動測試模式
FLASK_ENV=testing python app.py
```

## 授權

此專案僅供學習和研究使用。

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 更新日誌

### v1.3.0
- 新增線上閱讀中心功能
- 新增智能考試系統
- 支援多種題型（選擇題、填空題、簡答題、是非題）
- 自動評分和成績統計
- 完整的 Docker 容器化部署方案
- 新增 PDF 文件支援（閱讀和考試系統）
- 支援 PDF 內容載入到向量資料庫

### v1.2.0
- 新增檔案讀取功能
- 安全的檔案系統訪問
- Web 介面和 API 支援
- 支援多種檔案格式
- 檔案大小限制保護
- 路徑安全檢查機制

### v1.1.0
- 移除圖片轉PDF功能
- 優化 RAG 系統性能
- 改進錯誤處理機制

### v1.0.0
- 初始版本發布
- 基本 RAG 功能實現
- 現代化 Web 介面
- 系統狀態監控 