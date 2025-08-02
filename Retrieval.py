# RAG檢索與Gemini查詢系統
# 用於從Pinecone向量資料庫檢索相關內容並使用Gemini LLM生成回答

import os
import json
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import google.generativeai as genai
import time

class RAGRetriever:
    """
    RAG (Retrieval-Augmented Generation) 檢索器
    結合Pinecone向量搜尋和Gemini LLM生成回答
    """
    
    def __init__(self, 
                 pinecone_api_key: str,
                 gemini_api_key: str,
                 pinecone_env: str = "us-east-1",
                 index_name: str = "text-chunks-index"):
        """
        初始化RAG檢索器
        
        Args:
            pinecone_api_key: Pinecone API金鑰
            gemini_api_key: Gemini API金鑰
            pinecone_env: Pinecone環境
            index_name: Pinecone索引名稱
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
        """初始化Pinecone客戶端"""
        try:
            self.pc = Pinecone(api_key=self.pinecone_api_key)
            self.index = self.pc.Index(self.index_name)
            print(f"✅ Pinecone初始化成功，連接到索引: {self.index_name}")
        except Exception as e:
            print(f"❌ Pinecone初始化失敗: {str(e)}")
            raise
    
    def _initialize_gemini(self):
        """初始化Gemini LLM"""
        try:
            genai.configure(api_key=self.gemini_api_key)
            # 使用免費的gemini-1.5-flash模型
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Gemini LLM初始化成功")
        except Exception as e:
            print(f"❌ Gemini初始化失敗: {str(e)}")
            raise
    
    def _initialize_embedding_model(self):
        """初始化嵌入模型"""
        try:
            print("正在載入嵌入模型...")
            self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            print("✅ 嵌入模型載入完成")
        except Exception as e:
            print(f"❌ 嵌入模型載入失敗: {str(e)}")
            raise
    
    def retrieve_similar_chunks(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        從Pinecone檢索最相似的文字塊
        
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
        生成發送給Gemini的提示詞
        
        Args:
            query: 用戶查詢
            context: 檢索到的上下文
        
        Returns:
            完整的提示詞
        """
        prompt = f"""
你是一個專業的AI助手。請根據以下提供的上下文資訊來回答用戶的問題。

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
        向Gemini發送查詢並獲取回答
        
        Args:
            prompt: 完整的提示詞
            max_retries: 最大重試次數
        
        Returns:
            Gemini的回答
        """
        for attempt in range(max_retries):
            try:
                print(prompt)
                response = self.model.generate_content(prompt)
                
                if response.text:
                    return response.text
                else:
                    print(f"⚠️ Gemini回應為空，嘗試 {attempt + 1}/{max_retries}")
                    
            except Exception as e:
                print(f"❌ Gemini查詢失敗 (嘗試 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # 等待2秒後重試
                    
        return "抱歉，無法從Gemini獲取回答。請稍後再試。"
    
    def rag_query(self, query: str, top_k: int = 3, verbose: bool = True) -> Dict[str, Any]:
        """
        執行完整的RAG查詢流程
        
        Args:
            query: 用戶查詢
            top_k: 檢索的文字塊數量
            verbose: 是否顯示詳細過程
        
        Returns:
            包含檢索結果和LLM回答的字典
        """
        if verbose:
            print("=" * 60)
            print(f"🔍 開始RAG查詢: {query}")
            print("=" * 60)
        
        # 1. 檢索相關文字塊
        if verbose:
            print("📖 正在檢索相關文字塊...")
        retrieved_chunks = self.retrieve_similar_chunks(query, top_k)
        
        if not retrieved_chunks:
            return {
                'query': query,
                'retrieved_chunks': [],
                'context': "沒有找到相關的上下文資訊。",
                'answer': "抱歉，沒有找到相關的資訊來回答您的問題。",
                'success': False
            }
        
        # 2. 格式化上下文
        context = self.format_context(retrieved_chunks)
        
        if verbose:
            print("📋 檢索到的上下文:")
            print("-" * 40)
            for i, chunk in enumerate(retrieved_chunks, 1):
                print(f"{i}. 相似度: {chunk['score']:.4f}")
                print(f"   來源: {chunk['source_file']}")
                print(f"   內容預覽: {chunk['text'][:100]}...")
                print()
        
        # 3. 生成提示詞
        prompt = self.generate_prompt(query, context)
        
        # 4. 查詢Gemini LLM
        if verbose:
            print("🤖 正在向Gemini LLM發送查詢...")
        answer = self.query_gemini(prompt)
        
        # 5. 整理結果
        result = {
            'query': query,
            'retrieved_chunks': retrieved_chunks,
            'context': context,
            'answer': answer,
            'success': True
        }
        
        if verbose:
            print("=" * 60)
            print("🎯 最終回答:")
            print("=" * 60)
            print(answer)
            print("=" * 60)
        
        return result
    
    def batch_query(self, queries: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
        """
        批量執行RAG查詢
        
        Args:
            queries: 查詢列表
            top_k: 每個查詢檢索的文字塊數量
        
        Returns:
            查詢結果列表
        """
        results = []
        for i, query in enumerate(queries, 1):
            print(f"\n處理查詢 {i}/{len(queries)}: {query}")
            result = self.rag_query(query, top_k, verbose=False)
            results.append(result)
            time.sleep(1)  # 避免API速率限制
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], filename: str = "rag_results.json"):
        """
        儲存查詢結果到JSON檔案
        
        Args:
            results: 查詢結果列表
            filename: 儲存檔案名
        """
        try:
            # 清理結果以便JSON序列化
            clean_results = []
            for result in results:
                clean_result = {
                    'query': result['query'],
                    'answer': result['answer'],
                    'retrieved_chunks': [
                        {
                            'score': chunk['score'],
                            'text': chunk['text'],
                            'source_file': chunk['source_file']
                        }
                        for chunk in result['retrieved_chunks']
                    ],
                    'success': result['success']
                }
                clean_results.append(clean_result)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(clean_results, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 結果已儲存到 {filename}")
            
        except Exception as e:
            print(f"❌ 儲存結果時發生錯誤: {str(e)}")

def main():
    """主要執行函式"""
    # API金鑰配置
    PINECONE_API_KEY = "PineconeAPIKey"
    GEMINI_API_KEY = "GeminiAPIKey"
    
    # 初始化RAG檢索器
    try:
        rag = RAGRetriever(
            pinecone_api_key=PINECONE_API_KEY,
            gemini_api_key=GEMINI_API_KEY,
            pinecone_env="us-east-1",
            index_name="text-chunks-index"
        )
        
        print("🚀 RAG系統初始化完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ RAG系統初始化失敗: {str(e)}")
        return
    
    # 互動式查詢模式
    print("💬 進入互動式查詢模式 (輸入 'quit' 退出)")
    print("=" * 60)
    
    while True:
        try:
            query = input("\n請輸入您的問題: ").strip()
            
            if query.lower() in ['quit', 'exit', '退出']:
                print("👋 感謝使用RAG查詢系統！")
                break
            
            if not query:
                print("⚠️ 請輸入有效的問題")
                continue
            
            # 執行RAG查詢
            result = rag.rag_query(query, top_k=3, verbose=True)
            
            # 詢問是否儲存結果
            save_choice = input("\n是否要儲存此次查詢結果？(y/n): ").strip().lower()
            if save_choice in ['y', 'yes', '是']:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"rag_result_{timestamp}.json"
                rag.save_results([result], filename)
                
        except KeyboardInterrupt:
            print("\n👋 程式已中斷，感謝使用！")
            break
        except Exception as e:
            print(f"❌ 查詢過程中發生錯誤: {str(e)}")

# 使用範例
def example_usage():
    """使用範例"""
    # API金鑰配置
    PINECONE_API_KEY = "PineconeAPIKey"
    GEMINI_API_KEY = "GeminiAPIKey"
    
    # 初始化RAG檢索器
    rag = RAGRetriever(
        pinecone_api_key=PINECONE_API_KEY,
        gemini_api_key=GEMINI_API_KEY
    )
    
    # 單一查詢範例
    query = "什麼是機器學習？"
    result = rag.rag_query(query, top_k=3, verbose=True)
    
    # 批量查詢範例
    queries = [
        "什麼是深度學習？",
        "向量資料庫的作用是什麼？",
        "人工智慧的發展趨勢如何？"
    ]
    
    batch_results = rag.batch_query(queries, top_k=3)
    rag.save_results(batch_results, "batch_results.json")

if __name__ == "__main__":
    # 執行主程式 (互動式模式)
    main()
    
    # 或者執行使用範例
    # example_usage()