// 閱讀系統 JavaScript

class ReadingSystem {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.loadFiles();
        this.currentFile = null;
        this.currentContent = '';
        this.fontSize = 'medium';
    }

    initializeElements() {
        // 搜尋元素
        this.searchInput = document.getElementById('searchInput');
        this.searchBtn = document.getElementById('searchBtn');
        
        // 檔案列表元素
        this.fileList = document.getElementById('fileList');
        
        // 內容顯示元素
        this.contentDisplay = document.getElementById('contentDisplay');
        
        // 字體大小控制
        this.fontSizeBtns = document.querySelectorAll('.font-size-btn');
        
        // 錯誤元素
        this.errorSection = document.getElementById('errorSection');
        this.errorMessage = document.getElementById('errorMessage');
    }

    bindEvents() {
        // 搜尋按鈕
        this.searchBtn.addEventListener('click', () => this.searchContent());
        
        // 搜尋輸入框 Enter 鍵
        this.searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchContent();
            }
        });
        
        // 字體大小按鈕
        this.fontSizeBtns.forEach(btn => {
            btn.addEventListener('click', () => this.changeFontSize(btn.dataset.size));
        });
    }

    async loadFiles() {
        try {
            const response = await fetch('/exam/files');
            const data = await response.json();
            
            if (data.success) {
                this.renderFileList(data.files);
            } else {
                this.showError('載入檔案清單失敗: ' + data.error);
            }
        } catch (error) {
            this.showError('載入檔案清單時發生錯誤: ' + error.message);
        }
    }

    renderFileList(files) {
        this.fileList.innerHTML = '';
        
        if (files.length === 0) {
            this.fileList.innerHTML = `
                <div class="text-center text-muted">
                    <i class="fas fa-folder-open fa-2x mb-2"></i>
                    <p>沒有找到任何檔案</p>
                </div>
            `;
            return;
        }
        
        files.forEach(file => {
            const fileItem = this.createFileItem(file);
            this.fileList.appendChild(fileItem);
        });
    }

    createFileItem(file) {
        const div = document.createElement('div');
        div.className = 'file-item';
        
        // 根據文件類型選擇圖標和顯示名稱
        const isPdf = file.toLowerCase().endsWith('.pdf');
        const icon = isPdf ? 'fas fa-file-pdf text-danger' : 'fas fa-file-text text-primary';
        const displayName = file.replace(/\.(txt|pdf)$/i, '');
        
        div.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="${icon} me-2"></i>
                <div>
                    <h6 class="mb-0">${displayName}</h6>
                    <small class="text-muted">${isPdf ? 'PDF 文件' : '文字文件'} - 點擊閱讀</small>
                </div>
            </div>
        `;
        
        div.addEventListener('click', () => this.loadFileContent(file));
        
        return div;
    }

    async loadFileContent(fileName) {
        try {
            // 更新選中狀態
            this.updateFileSelection(fileName);
            
            // 顯示載入狀態
            this.contentDisplay.innerHTML = `
                <div class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">載入中...</span>
                    </div>
                    <p class="mt-2">載入檔案內容中...</p>
                </div>
            `;
            
            const response = await fetch('/read/content', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    file_name: fileName
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentFile = fileName;
                this.currentContent = data.content;
                this.displayContent(data.content);
            } else {
                this.showError(data.error || '載入檔案失敗');
            }
        } catch (error) {
            this.showError('載入檔案時發生錯誤: ' + error.message);
        }
    }

    updateFileSelection(fileName) {
        // 移除所有選中狀態
        document.querySelectorAll('.file-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // 添加選中狀態到當前檔案
        document.querySelectorAll('.file-item').forEach(item => {
            if (item.querySelector('h6').textContent === fileName.replace('.txt', '')) {
                item.classList.add('active');
            }
        });
    }

    displayContent(content) {
        // 格式化內容，將換行符轉換為 HTML
        const formattedContent = content
            .split('\n')
            .map(line => {
                line = line.trim();
                if (line === '') return '<br>';
                if (line.startsWith('#')) {
                    const level = line.match(/^#+/)[0].length;
                    const text = line.replace(/^#+\s*/, '');
                    return `<h${level}>${text}</h${level}>`;
                }
                return `<p>${line}</p>`;
            })
            .join('');
        
        this.contentDisplay.innerHTML = formattedContent;
        this.applyFontSize();
    }

    searchContent() {
        const searchTerm = this.searchInput.value.trim();
        
        if (!searchTerm) {
            this.showError('請輸入搜尋關鍵字');
            return;
        }
        
        if (!this.currentContent) {
            this.showError('請先選擇一個檔案');
            return;
        }
        
        // 高亮搜尋結果
        this.highlightSearchResults(searchTerm);
    }

    highlightSearchResults(searchTerm) {
        const content = this.currentContent;
        const regex = new RegExp(`(${searchTerm})`, 'gi');
        const highlightedContent = content.replace(regex, '<mark>$1</mark>');
        
        this.displayContent(highlightedContent);
        
        // 滾動到第一個搜尋結果
        const firstMark = this.contentDisplay.querySelector('mark');
        if (firstMark) {
            firstMark.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
        }
    }

    changeFontSize(size) {
        this.fontSize = size;
        
        // 更新按鈕狀態
        this.fontSizeBtns.forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.size === size) {
                btn.classList.add('active');
            }
        });
        
        this.applyFontSize();
    }

    applyFontSize() {
        const sizeMap = {
            'small': '0.9rem',
            'medium': '1.1rem',
            'large': '1.3rem'
        };
        
        this.contentDisplay.style.fontSize = sizeMap[this.fontSize];
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorSection.style.display = 'block';
        
        // 滾動到錯誤訊息
        this.errorSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
}

// 頁面載入完成後初始化閱讀系統
document.addEventListener('DOMContentLoaded', () => {
    window.readingSystem = new ReadingSystem();
}); 