# 透過 RAG 實現線上閱讀與考試系統

## 技術簡報

---

## 📋 目錄

1. [專案概述](#專案概述)
2. [系統架構](#系統架構)
3. [核心功能](#核心功能)
4. [技術特色](#技術特色)
5. [部署方案](#部署方案)
6. [使用場景](#使用場景)
7. [未來發展](#未來發展)

---

## 🎯 專案概述

### 基於 Flask 的 RAG (Retrieval-Augmented Generation) 智能問答系統

**整合技術：**
- Pinecone 向量資料庫
- Gemini AI 模型
- Flask 後端框架
- Bootstrap 5 前端框架

**線上 Demo：** https://d6530614201f.ngrok.app/

---

## 🔧 系統架構

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端介面       │    │   Flask 後端    │     │   外部服務       │
│   (HTML/CSS/JS) │◄──►│   (Python)      │◄──►│   Pinecone      │
│                 │    │                 │    │   Gemini AI     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**技術棧：**
- **前端**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5
- **後端**: Flask, Python
- **向量資料庫**: Pinecone
- **AI 模型**: Google Gemini
- **嵌入模型**: sentence-transformers/all-MiniLM-L6-v2

---

## ⚡ 核心功能

### 1. 🔍 RAG 智能問答系統
- 語義搜尋與檢索
- AI 生成準確回答
- 相關資料來源顯示
- 即時系統狀態監控

### 2. 📚 線上閱讀中心
- 支援 .txt 和 .pdf 格式
- 教材內容線上瀏覽
- 內容搜尋功能
- 響應式設計

### 3. 📝 智能考試系統
**支援題型：**
- **選擇題** - 四選一，自動評分
- **填空題** - 模糊匹配評分
- **簡答題** - AI 智能評分
- **是非題** - 自動評分

---

## 🎨 功能特色

| 功能 | 描述 |
|------|------|
| 🔍 **智能檢索** | 使用 Pinecone 向量資料庫進行語義搜尋 |
| 🤖 **AI 生成** | 整合 Gemini AI 模型生成準確回答 |
| 📚 **線上閱讀** | 提供教材內容的線上閱讀功能 |
| 📝 **智能考試** | 基於教材內容自動生成考試題目 |
| ✅ **自動評分** | 支援多種題型的自動評分 |
| 💻 **現代化介面** | 美觀的響應式 Web 介面 |
| 📊 **即時狀態** | 系統狀態即時監控 |
| 🔒 **安全配置** | 環境變數管理 API 金鑰 |
| 🐳 **Docker 部署** | 完整的 Docker Compose 容器化部署方案 |

---

## 🚀 考試流程

1. **選擇教材** - 支援 .txt 和 .pdf 格式
2. **設定題數** - 預設 5 題，可自定義
3. **AI 生成** - 自動生成題目
4. **學生作答** - 多種題型支援
5. **自動評分** - 即時評分與解析
6. **成績統計** - 詳細分析報告

---

## 📡 API 端點

### RAG 查詢端點
```http
POST /query
Content-Type: application/json

{
  "query": "您的問題"
}
```

### 考試系統端點
```http
GET  /exam/files          # 取得教材列表
POST /exam/generate       # 生成考試題目
POST /exam/grade          # 評分考試
```

### 閱讀中心端點
```http
POST /read/content        # 讀取教材內容
```

### 健康檢查端點
```http
GET  /health             # 系統狀態檢查
```

---

## 🛠️ 部署方案

### 方法一：Docker Compose（推薦）

```bash
# 1. 下載專案
git clone <repository-url>
cd rag-examination-system

# 2. 設定環境變數
cp env.example .env
# 編輯 .env 檔案，填入 API 金鑰

# 3. 啟動服務
./docker-start.sh

# 4. 訪問應用
http://localhost:5002
```

### 方法二：本地安裝

```bash
# 1. 安裝依賴
pip install -r requirements.txt

# 2. 設定環境變數
cp env.example .env

# 3. 初始化資料庫
python init_db.py

# 4. 啟動應用
python run.py
```

---

## 📁 專案結構

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
├── Dockerfile            # Docker 容器配置
├── docker-compose.yml    # Docker Compose 配置
├── templates/            # HTML 模板
│   ├── index.html        # 首頁 (RAG 問答系統)
│   ├── exam.html         # 考試系統頁面
│   └── read.html         # 閱讀中心頁面
├── static/               # 靜態資源
│   ├── css/
│   │   └── style.css     # 樣式檔案
│   └── js/
│       ├── app.js        # 主要 JavaScript 邏輯
│       ├── exam.js       # 考試系統 JavaScript
│       └── read.js       # 閱讀中心 JavaScript
└── data/                 # 教材資料
    ├── 歷史第一冊.txt     # 歷史教材資料
    ├── 地理第一冊.txt     # 地理教材資料
    └── 公民第一冊.pdf    # PDF 教材資料
```

---

## 🎯 適用場景

| 場景 | 應用 |
|------|------|
| 🏫 **教育機構** | 線上教材閱讀與考試 |
| 📚 **圖書館** | 文獻檢索與問答 |
| 🏢 **企業培訓** | 員工培訓與考核 |
| 🔬 **研究機構** | 文獻智能問答 |

---

## 🔮 未來發展方向

- [ ] 支援更多文件格式（Word, PowerPoint）
- [ ] 多語言支援
- [ ] 用戶權限管理
- [ ] 考試結果分析與報表
- [ ] 移動端適配優化
- [ ] API 速率限制與安全增強
- [ ] 語音問答功能
- [ ] 多媒體內容支援

---

## 📊 技術統計

| 指標 | 數值 |
|------|------|
| **主要模組** | 3 個 |
| **支援題型** | 4 種 |
| **自動評分** | 100% |
| **文件格式** | .txt, .pdf |
| **部署方式** | Docker, 本地 |

---

## 🎉 結語

**RAG 智能問答系統** 成功整合了現代化的 AI 技術與教育應用場景，提供了一個完整的線上閱讀與考試解決方案。

**核心價值：**
- 🚀 **技術創新** - 結合 RAG 與教育應用
- 📚 **實用性強** - 解決實際教育需求
- 🔧 **易於部署** - 完整的容器化方案
- 🎨 **用戶友好** - 現代化 Web 介面

**線上 Demo：** https://d6530614201f.ngrok.app/

---

*技術簡報 | 2024* 