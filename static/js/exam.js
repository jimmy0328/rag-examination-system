// 考試系統 JavaScript

class ExamSystem {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.loadFiles();
        this.currentQuestions = [];
        this.userAnswers = {};
    }

    initializeElements() {
        // 檔案選擇元素
        this.fileSelect = document.getElementById('fileSelect');
        this.questionCount = document.getElementById('questionCount');
        this.generateExamBtn = document.getElementById('generateExamBtn');
        
        // 區域元素
        this.fileSelectionSection = document.getElementById('fileSelectionSection');
        this.loadingSection = document.getElementById('loadingSection');
        this.examSection = document.getElementById('examSection');
        this.resultsSection = document.getElementById('resultsSection');
        this.errorSection = document.getElementById('errorSection');
        
        // 考試元素
        this.questionsContainer = document.getElementById('questionsContainer');
        this.currentQuestionSpan = document.getElementById('currentQuestion');
        this.totalQuestionsSpan = document.getElementById('totalQuestions');
        this.submitExamBtn = document.getElementById('submitExamBtn');
        
        // 結果元素
        this.statisticsContainer = document.getElementById('statisticsContainer');
        this.detailedResults = document.getElementById('detailedResults');
        this.newExamBtn = document.getElementById('newExamBtn');
        
        // 錯誤元素
        this.errorMessage = document.getElementById('errorMessage');
    }

    bindEvents() {
        // 生成考試按鈕
        this.generateExamBtn.addEventListener('click', () => this.generateExam());
        
        // 提交答案按鈕
        this.submitExamBtn.addEventListener('click', () => this.submitExam());
        
        // 重新考試按鈕
        this.newExamBtn.addEventListener('click', () => this.resetExam());
        
        // 檔案選擇變更
        this.fileSelect.addEventListener('change', () => this.validateForm());
    }

    async loadFiles() {
        try {
            const response = await fetch('/exam/files');
            const data = await response.json();
            
            if (data.success) {
                this.populateFileSelect(data.files);
            } else {
                this.showError('載入檔案清單失敗: ' + data.error);
            }
        } catch (error) {
            this.showError('載入檔案清單時發生錯誤: ' + error.message);
        }
    }

    populateFileSelect(files) {
        this.fileSelect.innerHTML = '<option value="">請選擇檔案...</option>';
        
        files.forEach(file => {
            const option = document.createElement('option');
            option.value = file;
            // 根據文件類型顯示不同的名稱
            const isPdf = file.toLowerCase().endsWith('.pdf');
            const displayName = file.replace(/\.(txt|pdf)$/i, '');
            option.textContent = `${displayName} (${isPdf ? 'PDF' : 'TXT'})`;
            this.fileSelect.appendChild(option);
        });
    }

    validateForm() {
        const fileSelected = this.fileSelect.value !== '';
        this.generateExamBtn.disabled = !fileSelected;
        
        if (fileSelected) {
            this.generateExamBtn.classList.remove('btn-secondary');
            this.generateExamBtn.classList.add('btn-primary');
        } else {
            this.generateExamBtn.classList.remove('btn-primary');
            this.generateExamBtn.classList.add('btn-secondary');
        }
    }

    async generateExam() {
        const fileName = this.fileSelect.value;
        const numQuestions = parseInt(this.questionCount.value);
        
        if (!fileName) {
            this.showError('請選擇檔案');
            return;
        }

        this.showLoading();
        
        try {
            const response = await fetch('/exam/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    file_name: fileName,
                    num_questions: numQuestions
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentQuestions = data.questions;
                this.displayExam();
            } else {
                this.showError(data.error || '生成考試失敗');
            }
        } catch (error) {
            this.showError('生成考試時發生錯誤: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    displayExam() {
        this.fileSelectionSection.style.display = 'none';
        this.examSection.style.display = 'block';
        
        this.totalQuestionsSpan.textContent = this.currentQuestions.length;
        this.currentQuestionSpan.textContent = '1';
        
        this.renderQuestions();
    }

    renderQuestions() {
        this.questionsContainer.innerHTML = '';
        
        this.currentQuestions.forEach((question, index) => {
            const questionCard = this.createQuestionCard(question, index + 1);
            this.questionsContainer.appendChild(questionCard);
        });
    }

    createQuestionCard(question, questionNumber) {
        const card = document.createElement('div');
        card.className = 'question-card';
        
        const questionType = this.getQuestionTypeText(question.type);
        const questionTypeClass = `question-type-${question.type}`;
        
        card.innerHTML = `
            <div class="question-header">
                <h5>第 ${questionNumber} 題</h5>
                <span class="question-type-badge ${questionTypeClass}">${questionType}</span>
            </div>
            <div class="question-content">
                <p class="mb-3">${question.question}</p>
                ${this.createAnswerInput(question, questionNumber)}
            </div>
        `;
        
        // 綁定事件
        this.bindQuestionEvents(card, question, questionNumber);
        
        return card;
    }

    getQuestionTypeText(type) {
        const typeMap = {
            'choice': '選擇題',
            'fill': '填空題',
            'short': '簡答題',
            'true_false': '是非題'
        };
        return typeMap[type] || '未知類型';
    }

    createAnswerInput(question, questionNumber) {
        const questionId = question.id;
        
        switch (question.type) {
            case 'choice':
                return `
                    <ul class="options-list" data-question-id="${questionId}">
                        ${question.options.map((option, index) => `
                            <li data-value="${option.charAt(0)}" data-question-id="${questionId}">
                                ${option}
                            </li>
                        `).join('')}
                    </ul>
                `;
            
            case 'fill':
                return `
                    <input type="text" 
                           class="answer-input" 
                           data-question-id="${questionId}"
                           placeholder="請填入答案...">
                `;
            
            case 'short':
                return `
                    <textarea class="answer-input" 
                              data-question-id="${questionId}"
                              rows="4"
                              placeholder="請寫下您的答案..."></textarea>
                `;
            
            case 'true_false':
                return `
                    <ul class="options-list" data-question-id="${questionId}">
                        <li data-value="正確" data-question-id="${questionId}">正確</li>
                        <li data-value="錯誤" data-question-id="${questionId}">錯誤</li>
                    </ul>
                `;
            
            default:
                return `
                    <input type="text" 
                           class="answer-input" 
                           data-question-id="${questionId}"
                           placeholder="請填入答案...">
                `;
        }
    }

    bindQuestionEvents(card, question, questionNumber) {
        const questionId = question.id;
        
        // 選擇題和是非題的點擊事件
        const options = card.querySelectorAll('.options-list li');
        options.forEach(option => {
            option.addEventListener('click', () => {
                // 移除同組其他選項的選中狀態
                const questionOptions = card.querySelectorAll(`[data-question-id="${questionId}"]`);
                questionOptions.forEach(opt => opt.classList.remove('selected'));
                
                // 選中當前選項
                option.classList.add('selected');
                
                // 儲存答案
                this.userAnswers[questionId] = option.dataset.value;
            });
        });
        
        // 填空題和簡答題的輸入事件
        const inputs = card.querySelectorAll('.answer-input');
        inputs.forEach(input => {
            input.addEventListener('input', (e) => {
                this.userAnswers[questionId] = e.target.value;
            });
        });
    }

    async submitExam() {
        // 檢查是否所有題目都已回答
        const unansweredQuestions = this.currentQuestions.filter(q => 
            !this.userAnswers[q.id] || this.userAnswers[q.id].trim() === ''
        );
        
        if (unansweredQuestions.length > 0) {
            this.showError(`還有 ${unansweredQuestions.length} 題未回答，請完成所有題目`);
            return;
        }

        this.showLoading();
        
        try {
            const response = await fetch('/exam/grade', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    questions: this.currentQuestions,
                    answers: this.userAnswers
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.displayResults(data.results, data.statistics);
            } else {
                this.showError(data.error || '評分失敗');
            }
        } catch (error) {
            this.showError('評分時發生錯誤: ' + error.message);
        } finally {
            this.hideLoading();
        }
    }

    displayResults(results, statistics) {
        this.examSection.style.display = 'none';
        this.resultsSection.style.display = 'block';
        
        this.renderStatistics(statistics);
        this.renderDetailedResults(results);
    }

    renderStatistics(statistics) {
        const accuracy = statistics.accuracy.toFixed(1);
        const averageScore = statistics.average_score.toFixed(1);
        
        this.statisticsContainer.innerHTML = `
            <div class="col-md-3">
                <div class="statistics-card text-center">
                    <div class="stat-number">${statistics.total_questions}</div>
                    <div class="text-muted">總題數</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="statistics-card text-center">
                    <div class="stat-number">${statistics.correct_answers}</div>
                    <div class="text-muted">正確答案</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="statistics-card text-center">
                    <div class="stat-number">${accuracy}%</div>
                    <div class="text-muted">正確率</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="statistics-card text-center">
                    <div class="stat-number">${averageScore}</div>
                    <div class="text-muted">平均分數</div>
                </div>
            </div>
        `;
    }

    renderDetailedResults(results) {
        this.detailedResults.innerHTML = '';
        
        results.forEach((result, index) => {
            const resultCard = this.createResultCard(result, index + 1);
            this.detailedResults.insertAdjacentHTML('beforeend', resultCard);
        });
    }

    createResultCard(result, questionNumber) {
        const isCorrect = result.is_correct;
        const resultClass = isCorrect ? 'result-correct' : 'result-incorrect';
        const resultIcon = isCorrect ? 'fa-check-circle' : 'fa-times-circle';
        const resultText = isCorrect ? '正確' : '錯誤';
        
        return `
            <div class="result-item ${resultClass}">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6>第 ${questionNumber} 題</h6>
                    <span class="badge ${isCorrect ? 'bg-success' : 'bg-danger'}">
                        <i class="fas ${resultIcon}"></i> ${resultText}
                    </span>
                </div>
                <p><strong>題目：</strong>${result.question.question}</p>
                <p><strong>您的答案：</strong>${result.user_answer || '未作答'}</p>
                <p><strong>正確答案：</strong>${result.correct_answer}</p>
                <p><strong>解析：</strong>${result.explanation}</p>
                <p><strong>得分：</strong>${result.score} 分</p>
            </div>
        `;
    }

    resetExam() {
        this.currentQuestions = [];
        this.userAnswers = {};
        
        this.resultsSection.style.display = 'none';
        this.fileSelectionSection.style.display = 'block';
        
        this.validateForm();
    }

    showLoading() {
        this.loadingSection.style.display = 'block';
        this.fileSelectionSection.style.display = 'none';
        this.examSection.style.display = 'none';
        this.resultsSection.style.display = 'none';
        this.errorSection.style.display = 'none';
    }

    hideLoading() {
        this.loadingSection.style.display = 'none';
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorSection.style.display = 'block';
        this.hideLoading();
        
        // 滾動到錯誤訊息
        this.errorSection.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
    }
}

// 頁面載入完成後初始化考試系統
document.addEventListener('DOMContentLoaded', () => {
    window.examSystem = new ExamSystem();
}); 