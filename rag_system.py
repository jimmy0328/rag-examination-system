import os
import json
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import google.generativeai as genai
import time

class RAGSystem:
    """
    RAG (Retrieval-Augmented Generation) 系統
    結合 Pinecone 向量搜尋和 Gemini LLM 生成回答
    """
    
    def __init__(self, 
                 pinecone_api_key: str,
                 gemini_api_key: str,
                 pinecone_env: str = "us-east-1",
                 index_name: str = "text-chunks-index"):
        """
        初始化 RAG 系統
        
        Args:
            pinecone_api_key: Pinecone API 金鑰
            gemini_api_key: Gemini API 金鑰
            pinecone_env: Pinecone 環境
            index_name: Pinecone 索引名稱
        """
        self.pinecone_api_key = pinecone_api_key
        self.gemini_api_key = gemini_api_key
        self.pinecone_env = pinecone_env
        self.index_name = index_name
        
        # 初始化組件
        self._initialize_pinecone()
        self._initialize_gemini()
        self._initialize_embedding_model()
    
    def _initialize_pinecone(self):
        """初始化 Pinecone 客戶端"""
        try:
            self.pc = Pinecone(api_key=self.pinecone_api_key)
            self.index = self.pc.Index(self.index_name)
            print(f"✅ Pinecone 初始化成功，連接到索引: {self.index_name}")
        except Exception as e:
            print(f"❌ Pinecone 初始化失敗: {str(e)}")
            raise
    
    def _initialize_gemini(self):
        """初始化 Gemini LLM"""
        try:
            genai.configure(api_key=self.gemini_api_key)
            # 使用免費的 gemini-1.5-flash 模型
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            print("✅ Gemini LLM 初始化成功")
        except Exception as e:
            print(f"❌ Gemini 初始化失敗: {str(e)}")
            raise
    
    def _initialize_embedding_model(self):
        """初始化嵌入模型"""
        try:
            print("正在載入嵌入模型...")
            self.embedding_model = SentenceTransformer('shibing624/text2vec-base-chinese')
            print("✅ 嵌入模型載入完成")
        except Exception as e:
            print(f"❌ 嵌入模型載入失敗: {str(e)}")
            raise
    
    def retrieve_similar_chunks(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        從 Pinecone 檢索最相似的文字塊
        
        Args:
            query: 查詢文字
            top_k: 檢索的文字塊數量
        
        Returns:
            相似文字塊列表
        """
        try:
            # 生成查詢向量
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # 執行向量搜尋
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # 提取相關信息
            retrieved_chunks = []
            for match in results['matches']:
                chunk_info = {
                    'id': match['id'],
                    'score': match['score'],
                    'text': match['metadata'].get('text', ''),
                    'source_file': match['metadata'].get('source_file', 'Unknown'),
                    'chunk_index': match['metadata'].get('chunk_index', -1),
                    'metadata': match['metadata']
                }
                retrieved_chunks.append(chunk_info)
            
            print(f"✅ 成功檢索到 {len(retrieved_chunks)} 個相關文字塊")
            return retrieved_chunks
            
        except Exception as e:
            print(f"❌ 檢索過程中發生錯誤: {str(e)}")
            return []
    
    def format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        格式化檢索到的文字塊作為上下文
        
        Args:
            chunks: 檢索到的文字塊列表
        
        Returns:
            格式化的上下文字串
        """
        if not chunks:
            return "沒有找到相關的上下文資訊。"
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_part = f"""
=== 相關資訊 {i} (相似度: {chunk['score']:.4f}) ===
來源: {chunk['source_file']}
內容: {chunk['text']}
"""
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    def generate_prompt(self, query: str, context: str) -> str:
        """
        生成發送給 Gemini 的提示詞
        
        Args:
            query: 用戶查詢
            context: 檢索到的上下文
        
        Returns:
            完整的提示詞
        """
        prompt = f"""
你是一個專業的 AI 助手。請根據以下提供的上下文資訊來回答用戶的問題。

<context>
{context}
</context>

用戶問題: {query}

請根據上述上下文資訊回答問題。如果上下文中沒有足夠的資訊來回答問題，請誠實地說明，並基於你的一般知識提供有幫助的回答。

回答要求：
1. 基於提供的上下文資訊進行回答
2. 如果上下文相關，請引用相關內容
3. 回答要準確、詳細且有幫助
4. 使用繁體中文回答
"""
        return prompt
    
    def query_gemini(self, prompt: str, max_retries: int = 3) -> str:
        """
        向 Gemini 發送查詢並獲取回答
        
        Args:
            prompt: 完整的提示詞
            max_retries: 最大重試次數
        
        Returns:
            Gemini 的回答
        """
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                
                if response.text:
                    return response.text
                else:
                    print(f"⚠️ Gemini 回應為空，嘗試 {attempt + 1}/{max_retries}")
                    
            except Exception as e:
                print(f"❌ Gemini 查詢失敗 (嘗試 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # 等待2秒後重試
                    
        return "抱歉，無法從 Gemini 獲取回答。請稍後再試。"
    
    def query(self, query: str, top_k: int = 3, similarity_threshold: float = 0.5) -> Dict[str, Any]:
        """
        執行完整的 RAG 查詢流程
        
        Args:
            query: 用戶查詢
            top_k: 檢索的文字塊數量
            similarity_threshold: 相似度閾值，低於此值視為不相關
        
        Returns:
            包含檢索結果和 LLM 回答的字典
        """
        print(f"🔍 開始 RAG 查詢: {query}")
        
        # 1. 檢索相關文字塊
        retrieved_chunks = self.retrieve_similar_chunks(query, top_k)
        
        # 2. 檢查是否有相關內容
        if not retrieved_chunks:
            return {
                'query': query,
                'retrieved_chunks': [],
                'context': "沒有找到相關的上下文資訊。",
                'answer': "抱歉，您查詢的內容不在我們的資料庫中。請嘗試使用其他關鍵字或重新描述您的問題。",
                'success': False,
                'has_context': False
            }
        
        # 3. 檢查最高相似度是否達到閾值
        max_similarity = max(chunk['score'] for chunk in retrieved_chunks)
        print(f"📊 最高相似度: {max_similarity:.4f} (閾值: {similarity_threshold})")
        
        if max_similarity < similarity_threshold:
            return {
                'query': query,
                'retrieved_chunks': retrieved_chunks,
                'context': "檢索到的內容相似度過低，可能與查詢不相關。",
                'answer': f"抱歉，您查詢的內容在我們的資料庫中沒有找到足夠相關的資訊（最高相似度: {max_similarity:.2f}）。請嘗試使用其他關鍵字或重新描述您的問題。",
                'success': False,
                'has_context': False
            }
        
        # 4. 格式化上下文
        context = self.format_context(retrieved_chunks)
        
        # 5. 生成提示詞
        prompt = self.generate_prompt(query, context)
        
        # 6. 查詢 Gemini LLM
        answer = self.query_gemini(prompt)
        
        # 7. 整理結果
        result = {
            'query': query,
            'retrieved_chunks': retrieved_chunks,
            'context': context,
            'answer': answer,
            'success': True,
            'has_context': True
        }
        
        return result 