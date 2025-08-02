// RAG 系統前端 JavaScript

class RAGApp {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.checkSystemStatus();
    }

    initializeElements() {
        // 查詢相關元素
        this.queryInput = document.getElementById('queryInput');
        this.queryBtn = document.getElementById('queryBtn');
        
        // 顯示區域元素
        this.loadingSection = document.getElementById('loadingSection');
        this.resultsSection = document.getElementById('resultsSection');
        this.errorSection = document.getElementById('errorSection');
        
        // 結果顯示元素
        this.displayQuery = document.getElementById('displayQuery');
        this.answerContent = document.getElementById('answerContent');
        this.contextDisplay = document.getElementById('contextDisplay');
        this.contextContent = document.getElementById('contextContent');
        this.databaseStatus = document.getElementById('databaseStatus');
        this.statusText = document.getElementById('statusText');
        this.errorMessage = document.getElementById('errorMessage');
        
        // 語音播放元素
        this.playAudioBtn = document.getElementById('playAudioBtn');
        
        // 狀態指示器
        this.pineconeStatus = document.getElementById('pinecone-status');
        this.geminiStatus = document.getElementById('gemini-status');
        
        // 語音相關變數
        this.speechSynthesis = window.speechSynthesis;
        this.currentUtterance = null;
        this.isPlaying = false;
        this.manuallyStopped = false;
    }

    bindEvents() {
        // 查詢按鈕點擊事件
        this.queryBtn.addEventListener('click', () => this.handleQuery());
        
        // 輸入框回車事件
        this.queryInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleQuery();
            }
        });
        
        // 輸入框輸入事件（即時驗證）
        this.queryInput.addEventListener('input', () => {
            this.validateInput();
        });
        
        // 語音播放按鈕事件
        this.playAudioBtn.addEventListener('click', () => this.toggleAudioPlayback());
    }

    validateInput() {
        const query = this.queryInput.value.trim();
        const isValid = query.length > 0;
        
        this.queryBtn.disabled = !isValid;
        
        if (isValid) {
            this.queryBtn.classList.remove('btn-secondary');
            this.queryBtn.classList.add('btn-primary');
        } else {
            this.queryBtn.classList.remove('btn-primary');
            this.queryBtn.classList.add('btn-secondary');
        }
    }

    async checkSystemStatus() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            // 更新狀態指示器
            if (data.rag_system_ready) {
                this.pineconeStatus.classList.remove('offline');
                this.geminiStatus.classList.remove('offline');
                this.pineconeStatus.classList.add('online');
                this.geminiStatus.classList.add('online');
            } else {
                this.pineconeStatus.classList.remove('online');
                this.geminiStatus.classList.remove('online');
                this.pineconeStatus.classList.add('offline');
                this.geminiStatus.classList.add('offline');
            }
            
            // 檢查資料庫檔案
            await this.checkDatabaseFiles();
            
        } catch (error) {
            console.error('系統狀態檢查失敗:', error);
            this.pineconeStatus.classList.add('offline');
            this.geminiStatus.classList.add('offline');
        }
    }
    
    async checkDatabaseFiles() {
        try {
            const response = await fetch('/exam/files');
            const data = await response.json();
            
            if (data.success && data.files.length > 0) {
                const fileList = data.files.map(file => file.replace('.txt', '')).join('、');
                this.updateDatabaseStatusDisplay(`已載入 ${data.files.length} 個檔案：${fileList}`);
            } else {
                this.updateDatabaseStatusDisplay('資料庫中沒有檔案，請先執行 python init_db.py');
            }
        } catch (error) {
            this.updateDatabaseStatusDisplay('無法檢查資料庫狀態');
        }
    }
    
    updateDatabaseStatusDisplay(message) {
        const databaseStatus = document.getElementById('databaseStatusInfo');
        if (databaseStatus) {
            databaseStatus.innerHTML = `
                <div class="d-flex align-items-center">
                    <i class="fas fa-database text-primary me-2"></i>
                    <span>${message}</span>
                </div>
            `;
        }
    }

    async handleQuery() {
        const query = this.queryInput.value.trim();
        
        if (!query) {
            this.showError('請輸入查詢內容');
            return;
        }

        // 顯示載入狀態
        this.showLoading();
        
        try {
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });

            const data = await response.json();
            
            if (data.success) {
                this.displayResults(data);
            } else {
                this.showError(data.error || '查詢失敗');
            }
        } catch (error) {
            console.error('查詢錯誤:', error);
            this.showError('網路錯誤，請稍後再試');
        } finally {
            this.hideLoading();
        }
    }

    showLoading() {
        this.loadingSection.style.display = 'block';
        this.resultsSection.style.display = 'none';
        this.errorSection.style.display = 'none';
        this.queryBtn.disabled = true;
        this.queryBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 查詢中...';
    }

    hideLoading() {
        this.loadingSection.style.display = 'none';
        this.queryBtn.disabled = false;
        this.queryBtn.innerHTML = '<i class="fas fa-paper-plane"></i> 查詢';
        this.validateInput();
    }

    displayResults(data) {
        // 隱藏錯誤訊息
        this.errorSection.style.display = 'none';
        
        // 顯示查詢問題
        this.displayQuery.textContent = data.query;
        
        // 顯示 AI 回答
        this.answerContent.innerHTML = this.formatAnswer(data.answer);
        
        // 顯示語音播放按鈕
        this.playAudioBtn.style.display = 'inline-block';
        this.updateAudioButtonState();
        
        // 顯示相關資料（如果有）
        if (data.has_context && data.retrieved_chunks && data.retrieved_chunks.length > 0) {
            this.displayContext(data.retrieved_chunks);
            this.contextDisplay.style.display = 'block';
        } else {
            this.contextDisplay.style.display = 'none';
        }
        
        // 更新資料庫狀態
        this.updateDatabaseStatus(data.has_context);
        
        // 顯示結果區域
        this.resultsSection.style.display = 'block';
        this.resultsSection.classList.add('fade-in');
        
        // 滾動到結果區域
        this.resultsSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }

    formatAnswer(answer) {
        // 將換行符轉換為 HTML 換行
        return answer.replace(/\n/g, '<br>');
    }

    displayContext(chunks) {
        let contextHTML = '';
        
        chunks.forEach((chunk, index) => {
            const similarity = (chunk.score * 100).toFixed(1);
            const sourceFile = chunk.source_file || '未知來源';
            const text = chunk.text.length > 200 
                ? chunk.text.substring(0, 200) + '...' 
                : chunk.text;
            
            contextHTML += `
                <div class="context-item">
                    <div class="context-item-header">
                        <span><i class="fas fa-file-alt"></i> ${sourceFile}</span>
                        <span><i class="fas fa-percentage"></i> 相似度: ${similarity}%</span>
                    </div>
                    <div class="context-item-content">
                        ${text}
                    </div>
                </div>
            `;
        });
        
        this.contextContent.innerHTML = contextHTML;
    }

    updateDatabaseStatus(hasContext) {
        const statusBadge = this.databaseStatus.querySelector('.status-badge');
        
        if (statusBadge) {
            if (hasContext) {
                statusBadge.className = 'status-badge found';
                this.statusText.textContent = '在資料庫中找到相關資訊';
            } else {
                statusBadge.className = 'status-badge not-found';
                this.statusText.textContent = '資料庫中沒有相關資訊';
            }
        }
    }

    showError(message) {
        // 停止語音播放
        this.stopAudio();
        
        this.errorMessage.textContent = message;
        this.errorSection.style.display = 'block';
        this.resultsSection.style.display = 'none';
        this.loadingSection.style.display = 'none';
        
        // 隱藏語音播放按鈕
        this.playAudioBtn.style.display = 'none';
        
        // 滾動到錯誤訊息
        this.errorSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }

    // 語音播放相關方法
    toggleAudioPlayback() {
        if (this.isPlaying) {
            this.stopAudio();
        } else {
            this.playAudio();
        }
    }

    playAudio() {
        const answerText = this.answerContent.textContent || this.answerContent.innerText;
        
        if (!answerText) {
            console.warn('沒有可播放的文字內容');
            return;
        }

        // 停止當前播放
        this.stopAudio();

        // 創建新的語音合成
        this.currentUtterance = new SpeechSynthesisUtterance(answerText);
        
        // 設定語音參數
        this.currentUtterance.lang = 'zh-TW'; // 繁體中文
        this.currentUtterance.rate = 0.9; // 語速稍慢
        this.currentUtterance.pitch = 1.0; // 音調正常
        this.currentUtterance.volume = 1.0; // 音量最大

        // 標記為手動停止
        this.manuallyStopped = false;

        // 事件處理
        this.currentUtterance.onstart = () => {
            this.isPlaying = true;
            this.updateAudioButtonState();
        };

        this.currentUtterance.onend = () => {
            if (!this.manuallyStopped) {
                this.isPlaying = false;
                this.updateAudioButtonState();
            }
        };

        this.currentUtterance.onerror = (event) => {
            console.error('語音播放錯誤:', event);
            this.isPlaying = false;
            this.updateAudioButtonState();
            
            // 只有在非手動停止的情況下才顯示錯誤
            if (!this.manuallyStopped && event.error !== 'canceled') {
                this.showError('語音播放失敗，請檢查瀏覽器設定');
            }
        };

        // 開始播放
        this.speechSynthesis.speak(this.currentUtterance);
    }

    stopAudio() {
        this.manuallyStopped = true;
        if (this.currentUtterance) {
            this.speechSynthesis.cancel();
            this.currentUtterance = null;
        }
        this.isPlaying = false;
        this.updateAudioButtonState();
    }

    updateAudioButtonState() {
        if (this.isPlaying) {
            this.playAudioBtn.classList.add('playing');
            this.playAudioBtn.innerHTML = '<i class="fas fa-stop"></i> 停止播放';
        } else {
            this.playAudioBtn.classList.remove('playing');
            this.playAudioBtn.innerHTML = '<i class="fas fa-volume-up"></i> 播放語音';
        }
    }

    // 工具方法：防抖動
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// 頁面載入完成後初始化應用
document.addEventListener('DOMContentLoaded', () => {
    window.ragApp = new RAGApp();
    
    // 初始化語音播放按鈕狀態
    window.ragApp.playAudioBtn.style.display = 'none';
    
    // 添加一些動畫效果
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // 觀察需要動畫的元素
    document.querySelectorAll('.query-container, .result-container, .loading-container').forEach(el => {
        observer.observe(el);
    });
});

// 全域錯誤處理
window.addEventListener('error', (event) => {
    console.error('全域錯誤:', event.error);
    if (window.ragApp) {
        window.ragApp.showError('系統發生錯誤，請重新整理頁面');
    }
});

// 網路狀態監聽
window.addEventListener('online', () => {
    console.log('網路已連接');
    if (window.ragApp) {
        window.ragApp.checkSystemStatus();
    }
});

window.addEventListener('offline', () => {
    console.log('網路已斷開');
    if (window.ragApp) {
        window.ragApp.showError('網路連接已斷開，請檢查網路設定');
    }
});

// 頁面離開時停止語音播放
window.addEventListener('beforeunload', () => {
    if (window.ragApp && window.ragApp.isPlaying) {
        window.ragApp.stopAudio();
    }
}); 