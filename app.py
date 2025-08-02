from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from rag_system import RAGSystem
import json
import random
from typing import List, Dict, Any

# 載入環境變數
load_dotenv()

app = Flask(__name__)

# 初始化 RAG 系統
rag_system = None
try:
    rag_system = RAGSystem(
        pinecone_api_key=os.getenv('PINECONE_API_KEY'),
        gemini_api_key=os.getenv('GEMINI_API_KEY'),
        pinecone_env=os.getenv('PINECONE_ENV', 'us-east-1'),
        index_name='text-chunks-index'
    )
    print("✅ RAG 系統初始化成功")
except Exception as e:
    print(f"❌ RAG 系統初始化失敗: {str(e)}")
    print("💡 請先執行 python init_db.py 來初始化資料庫")

@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')

@app.route('/exam')
def exam():
    """考試院頁面"""
    return render_template('exam.html')

@app.route('/read')
def read():
    """閱讀中心頁面"""
    return render_template('read.html')

@app.route('/query', methods=['POST'])
def query():
    """處理查詢請求"""
    try:
        data = request.get_json()
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return jsonify({
                'success': False,
                'error': '請輸入查詢內容'
            })
        
        if not rag_system:
            return jsonify({
                'success': False,
                'error': 'RAG 系統未正確初始化。請先執行 python init_db.py 來初始化資料庫。'
            })
        
        # 執行 RAG 查詢
        result = rag_system.query(user_query, top_k=3, similarity_threshold=0.4)
        
        return jsonify({
            'success': True,
            'query': user_query,
            'answer': result['answer'],
            'retrieved_chunks': result['retrieved_chunks'],
            'has_context': len(result['retrieved_chunks']) > 0
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'查詢過程中發生錯誤: {str(e)}'
        })

@app.route('/exam/files', methods=['GET'])
def list_exam_files():
    """取得 data 目錄下所有 txt 檔案名稱"""
    try:
        files = [f for f in os.listdir('data') if f.endswith('.txt')]
        return jsonify({'success': True, 'files': files})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/exam/generate', methods=['POST'])
def generate_exam():
    """根據指定檔案出題"""
    try:
        data = request.get_json()
        file_name = data.get('file_name')
        num_questions = data.get('num_questions', 5)
        if not file_name:
            return jsonify({'success': False, 'error': '請指定檔案名稱'})
        file_path = os.path.join('data', file_name)
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': '檔案不存在'})
        # 讀取檔案內容
        with open(file_path, 'r', encoding='utf-8') as f:
            file_text = f.read()
        # 切分內容
        chunks = [file_text[i:i+500] for i in range(0, len(file_text), 500)]
        if len(chunks) > num_questions:
            chunks = random.sample(chunks, num_questions)
        # 生成題目
        content_text = "\n\n".join([f"內容 {i+1}: {chunk}" for i, chunk in enumerate(chunks)])
        prompt = f"""
請基於以下內容生成 {num_questions} 道考試題目。每道題目包含：
1. 題目內容
2. 題目類型（choice: 選擇題, fill: 填空題, short: 簡答題, true_false: 是非題）
3. 正確答案
4. 選項（如果是選擇題）
5. 解析
內容：
{content_text}
請以 JSON 格式返回，格式如下：
{{
    "questions": [
        {{
            "id": 1,
            "type": "choice",
            "question": "題目內容",
            "options": ["A. 選項1", "B. 選項2", "C. 選項3", "D. 選項4"],
            "correct_answer": "A",
            "explanation": "解析說明"
        }}
    ]
}}
"""
        response = rag_system.model.generate_content(prompt)
        response_text = response.text
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            result = json.loads(json_str)
            questions = result.get('questions', [])
            for i, question in enumerate(questions):
                question['id'] = i + 1
            return jsonify({'success': True, 'questions': questions, 'total_questions': len(questions)})
        except Exception as e:
            return jsonify({'success': False, 'error': f'題目解析失敗: {str(e)}', 'raw': response_text})
    except Exception as e:
        return jsonify({'success': False, 'error': f'生成考試時發生錯誤: {str(e)}'})

@app.route('/exam/grade', methods=['POST'])
def grade_exam():
    """評分考試"""
    try:
        data = request.get_json()
        questions = data.get('questions', [])
        answers = data.get('answers', {})
        
        if not questions:
            return jsonify({'success': False, 'error': '沒有題目可以評分'})
        
        results = []
        total_score = 0
        correct_count = 0
        
        for question in questions:
            question_id = question['id']
            user_answer = answers.get(str(question_id), '').strip()
            correct_answer = question['correct_answer']
            question_type = question['type']
            
            # 評分邏輯
            score = 0
            is_correct = False
            
            if question_type == 'choice':
                # 選擇題：完全匹配
                is_correct = user_answer == correct_answer
                score = 10 if is_correct else 0
                
            elif question_type == 'true_false':
                # 是非題：完全匹配
                is_correct = user_answer == correct_answer
                score = 10 if is_correct else 0
                
            elif question_type == 'fill':
                # 填空題：模糊匹配
                is_correct = fuzzy_match(user_answer, correct_answer)
                score = 10 if is_correct else 0
                
            elif question_type == 'short':
                # 簡答題：AI 評分
                score, is_correct = ai_grade_short_answer(
                    question['question'], 
                    correct_answer, 
                    user_answer
                )
            
            if is_correct:
                correct_count += 1
            total_score += score
            
            results.append({
                'question': question,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'score': score,
                'explanation': question.get('explanation', '')
            })
        
        # 計算統計資訊
        total_questions = len(questions)
        accuracy = (correct_count / total_questions) * 100 if total_questions > 0 else 0
        average_score = total_score / total_questions if total_questions > 0 else 0
        
        statistics = {
            'total_questions': total_questions,
            'correct_answers': correct_count,
            'accuracy': accuracy,
            'average_score': average_score
        }
        
        return jsonify({
            'success': True,
            'results': results,
            'statistics': statistics
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'評分時發生錯誤: {str(e)}'})

@app.route('/read/content', methods=['POST'])
def read_content():
    """讀取檔案內容"""
    try:
        data = request.get_json()
        file_name = data.get('file_name')
        
        if not file_name:
            return jsonify({'success': False, 'error': '請指定檔案名稱'})
        
        file_path = os.path.join('data', file_name)
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': '檔案不存在'})
        
        # 讀取檔案內容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'content': content,
            'file_name': file_name
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'讀取檔案時發生錯誤: {str(e)}'})

def fuzzy_match(user_answer: str, correct_answer: str) -> bool:
    """模糊匹配填空題答案"""
    if not user_answer or not correct_answer:
        return False
    
    user_clean = user_answer.lower().strip()
    correct_clean = correct_answer.lower().strip()
    
    # 完全匹配
    if user_clean == correct_clean:
        return True
    
    # 包含關係
    if user_clean in correct_clean or correct_clean in user_clean:
        return True
    
    # 相似度檢查（簡單版本）
    if len(user_clean) > 2 and len(correct_clean) > 2:
        # 計算共同字符數
        common_chars = sum(1 for c in user_clean if c in correct_clean)
        similarity = common_chars / max(len(user_clean), len(correct_clean))
        return similarity > 0.7
    
    return False

def ai_grade_short_answer(question: str, correct_answer: str, user_answer: str) -> tuple:
    """使用 AI 評分簡答題"""
    try:
        prompt = f"""
請評分以下簡答題：

題目：{question}
標準答案：{correct_answer}
學生答案：{user_answer}

請根據答案的準確性、完整性和相關性進行評分。
評分標準：
- 完全正確且完整：10分
- 大部分正確：7-9分
- 部分正確：4-6分
- 相關但不準確：1-3分
- 完全錯誤或無關：0分

請只返回分數（0-10的整數），不要其他文字。
"""
        
        response = rag_system.model.generate_content(prompt)
        score_text = response.text.strip()
        
        # 嘗試提取分數
        try:
            score = int(score_text)
            score = max(0, min(10, score))  # 確保分數在0-10範圍內
        except ValueError:
            # 如果無法解析分數，使用簡單的關鍵詞匹配
            score = simple_grade_short_answer(question, correct_answer, user_answer)
        
        is_correct = score >= 7  # 7分以上視為正確
        
        return score, is_correct
        
    except Exception as e:
        # 如果 AI 評分失敗，使用簡單評分
        score = simple_grade_short_answer(question, correct_answer, user_answer)
        is_correct = score >= 7
        return score, is_correct

def simple_grade_short_answer(question: str, correct_answer: str, user_answer: str) -> int:
    """簡單的簡答題評分（備用方案）"""
    if not user_answer or not correct_answer:
        return 0
    
    user_clean = user_answer.lower().strip()
    correct_clean = correct_answer.lower().strip()
    
    # 計算關鍵詞匹配
    correct_words = set(correct_clean.split())
    user_words = set(user_clean.split())
    
    if not correct_words:
        return 0
    
    common_words = correct_words.intersection(user_words)
    match_ratio = len(common_words) / len(correct_words)
    
    if match_ratio >= 0.8:
        return 10
    elif match_ratio >= 0.6:
        return 8
    elif match_ratio >= 0.4:
        return 6
    elif match_ratio >= 0.2:
        return 4
    else:
        return 2

@app.route('/health')
def health():
    """健康檢查端點"""
    return jsonify({
        'status': 'healthy',
        'rag_system_ready': rag_system is not None
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002) 