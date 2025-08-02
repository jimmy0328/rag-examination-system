# 📊 專案簡報方案指南

本指南提供三種不同的簡報方案，讓你可以選擇最適合的方式在 GitHub 上展示你的 RAG 智能問答系統專案。

## 🎯 方案選擇

### 方案一：Reveal.js 技術簡報（推薦）
**檔案：** `slides.html`
- ✅ 專業的簡報效果
- ✅ 支援動畫和過渡效果
- ✅ 可在 GitHub Pages 上直接瀏覽
- ✅ 適合技術展示和演講
- ✅ 包含返回專案頁面連結

### 方案二：Markdown 簡報
**檔案：** `PRESENTATION.md`
- ✅ 簡單易讀
- ✅ 在 GitHub 上直接查看
- ✅ 支援目錄導航
- ✅ 適合文檔式展示

### 方案三：專案展示頁面
**檔案：** `index.html`
- ✅ 美觀的響應式設計
- ✅ 完整的專案介紹
- ✅ 適合專案展示和推廣
- ✅ 包含 Demo 連結

## 🚀 部署步驟

### 1. 啟用 GitHub Pages

1. 前往你的 GitHub 專案頁面
2. 點擊 **Settings** 標籤
3. 滾動到 **Pages** 區塊
4. 在 **Source** 選擇 **Deploy from a branch**
5. 選擇 **main** 分支和 **/(root)** 資料夾
6. 點擊 **Save**

### 2. 選擇預設頁面

根據你的需求選擇其中一個檔案作為預設頁面：

#### 選項 A：使用 Reveal.js 簡報
```bash
# 直接訪問 slides.html
# 或將 slides.html 重命名為 index.html
mv slides.html index.html
```

#### 選項 B：使用專案展示頁面
```bash
# index.html 已經是預設檔案
# 不需要額外設定
```

#### 選項 C：使用 Markdown 簡報
```bash
# 在 README.md 中加入連結
echo "## 📊 [專案簡報](PRESENTATION.md)" >> README.md
```

### 3. 自動部署設定

已經創建了 `.github/workflows/deploy.yml` 檔案，會自動部署到 GitHub Pages。

## 📋 檔案說明

| 檔案 | 用途 | 特點 |
|------|------|------|
| `slides.html` | Reveal.js 技術簡報 | 專業簡報效果，支援動畫 |
| `PRESENTATION.md` | Markdown 簡報 | 簡單易讀，GitHub 原生支援 |
| `.github/workflows/deploy.yml` | 自動部署配置 | GitHub Actions 自動部署 |

## 🎨 自訂化建議

### 修改簡報內容

1. **更新 Demo 連結**
   ```html
   <!-- 在 presentation.html 和 index.html 中 -->
   <a href="你的實際 Demo 連結">🚀 線上 Demo</a>
   ```

2. **更新專案資訊**
   - 修改專案名稱和描述
   - 更新技術棧資訊
   - 調整功能特色

3. **添加截圖**
   ```html
   <img src="screenshots/demo.png" alt="系統截圖" class="img-fluid">
   ```

### 添加專案截圖

1. 創建 `screenshots/` 資料夾
2. 添加系統截圖
3. 在簡報中引用

## 🔧 進階設定

### 自訂主題

#### Reveal.js 主題
```html
<!-- 在 presentation.html 中 -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.3.1/theme/black.min.css">
```

#### Bootstrap 主題
```html
<!-- 在 index.html 中 -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
```

### 添加分析追蹤

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

## 📱 行動裝置優化

所有方案都已經包含響應式設計，支援：
- 📱 手機
- 📱 平板
- 💻 桌面電腦

## 🎯 使用建議

### 技術演講
- 使用 **方案一** (Reveal.js)
- 適合現場演講和技術分享

### 專案展示
- 使用 **方案三** (專案展示頁面)
- 適合專案推廣和展示

### 文檔閱讀
- 使用 **方案二** (Markdown)
- 適合詳細閱讀和參考

## 🔗 快速連結

部署完成後，你的簡報將在以下網址可用：
```
https://你的用戶名.github.io/你的專案名/
```

## 📞 支援

如果遇到問題：
1. 檢查 GitHub Pages 設定
2. 確認檔案路徑正確
3. 查看 GitHub Actions 日誌

---

*選擇最適合你需求的方案，開始展示你的 RAG 智能問答系統吧！* 