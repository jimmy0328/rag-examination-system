# Google Colab 文字處理與 Pinecone 向量儲存程式
# 請在 Google Colab 中執行此程式

# 1. 安裝必要的套件
# !pip install pinecone sentence-transformers langchain-text-splitters openai tiktoken

# 2. 匯入必要的函式庫
import os
import uuid
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec, CloudProvider, AwsRegion
import time
import PyPDF2
import pdfplumber

# 3. 設定 API 金鑰和環境變數
from dotenv import load_dotenv
load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = "us-east-1"

# 4. 初始化 Pinecone 客戶端
pc = Pinecone(api_key=PINECONE_API_KEY)

# 5. 設定索引名稱和維度
INDEX_NAME = "text-chunks-index"
DIMENSION = 384  # sentence-transformers/all-MiniLM-L6-v2 的向量維度

# 6. 創建或連接 Pinecone 索引
def create_or_connect_index():
    """創建或連接到 Pinecone 索引"""
    try:
        # 檢查索引是否已存在
        existing_indexes = pc.list_indexes()
        if INDEX_NAME not in [idx.name for idx in existing_indexes]:
            print(f"創建新索引: {INDEX_NAME}")
            pc.create_index(
                name=INDEX_NAME,
                dimension=DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=CloudProvider.AWS,
                    region=AwsRegion.US_EAST_1
                )
            )
            # 等待索引初始化完成
            time.sleep(10)
        else:
            print(f"索引 {INDEX_NAME} 已存在，正在連接...")
        
        # 連接到索引
        index = pc.Index(INDEX_NAME)
        print(f"成功連接到索引: {INDEX_NAME}")
        return index
    except Exception as e:
        print(f"創建或連接索引時發生錯誤: {str(e)}")
        return None

# 7. 初始化文字嵌入模型
print("正在載入嵌入模型...")
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
print("嵌入模型載入完成!")

# 8. 文字分塊函式
def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
    """
    將文字分割成較小的塊
    
    Args:
        text: 輸入文字
        chunk_size: 每個塊的最大字符數
        chunk_overlap: 塊之間的重疊字符數
    
    Returns:
        分割後的文字塊列表
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", "。", ".", "!", "?", ";", ",", " ", ""]
    )
    
    chunks = text_splitter.split_text(text)
    return chunks

# 9. 生成向量函式
def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    為文字列表生成嵌入向量
    
    Args:
        texts: 文字列表
    
    Returns:
        嵌入向量列表
    """
    embeddings = embedding_model.encode(texts, convert_to_numpy=True)
    return embeddings.tolist()

# 10. 讀取文字檔案函式
def read_text_file(file_path: str) -> str:
    """
    讀取文字檔案
    
    Args:
        file_path: 檔案路徑
    
    Returns:
        檔案內容
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print(f"錯誤: 找不到檔案 {file_path}")
        return ""
    except Exception as e:
        print(f"讀取檔案時發生錯誤: {str(e)}")
        return ""

# 10.1. 讀取 PDF 檔案函式
def read_pdf_file(file_path: str) -> str:
    """
    讀取 PDF 檔案
    
    Args:
        file_path: PDF 檔案路徑
    
    Returns:
        PDF 內容文字
    """
    try:
        content = ""
        
        # 嘗試使用 pdfplumber (更好的文字提取)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        content += page_text + "\n"
            print(f"使用 pdfplumber 成功讀取 PDF: {file_path}")
        except Exception as e:
            print(f"pdfplumber 讀取失敗，嘗試使用 PyPDF2: {str(e)}")
            
            # 備用方案：使用 PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        content += page_text + "\n"
            print(f"使用 PyPDF2 成功讀取 PDF: {file_path}")
        
        return content.strip()
        
    except FileNotFoundError:
        print(f"錯誤: 找不到檔案 {file_path}")
        return ""
    except Exception as e:
        print(f"讀取 PDF 檔案時發生錯誤: {str(e)}")
        return ""

# 10.2. 通用檔案讀取函式
def read_file(file_path: str) -> str:
    """
    根據檔案副檔名讀取檔案內容
    
    Args:
        file_path: 檔案路徑
    
    Returns:
        檔案內容
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    
    if file_extension == '.pdf':
        return read_pdf_file(file_path)
    elif file_extension == '.txt':
        return read_text_file(file_path)
    else:
        print(f"不支援的檔案格式: {file_extension}")
        return ""

# 11. 儲存到 Pinecone 函式
def store_to_pinecone(index, chunks: List[str], embeddings: List[List[float]], 
                     metadata_list: List[Dict[str, Any]] = None):
    """
    將向量和元數據儲存到 Pinecone
    
    Args:
        index: Pinecone 索引物件
        chunks: 文字塊列表
        embeddings: 嵌入向量列表
        metadata_list: 元數據列表
    """
    if metadata_list is None:
        metadata_list = [{"text": chunk} for chunk in chunks]
    
    # 準備要上傳的向量
    vectors_to_upsert = []
    for i, (chunk, embedding, metadata) in enumerate(zip(chunks, embeddings, metadata_list)):
        vector_id = str(uuid.uuid4())
        vectors_to_upsert.append({
            "id": vector_id,
            "values": embedding,
            "metadata": {
                **metadata,
                "text": chunk,
                "chunk_index": i
            }
        })
    
    # 批次上傳向量 (每批100個)
    batch_size = 100
    for i in range(0, len(vectors_to_upsert), batch_size):
        batch = vectors_to_upsert[i:i + batch_size]
        try:
            index.upsert(vectors=batch)
            print(f"成功上傳批次 {i//batch_size + 1}/{(len(vectors_to_upsert)-1)//batch_size + 1}")
        except Exception as e:
            print(f"上傳批次時發生錯誤: {str(e)}")

# 12. 主要處理函式
def process_file(file_path: str, chunk_size: int = 500, chunk_overlap: int = 50):
    """
    處理檔案的主要函式（支援 TXT 和 PDF）
    
    Args:
        file_path: 檔案路徑
        chunk_size: 分塊大小
        chunk_overlap: 分塊重疊
    """
    print("="*50)
    print("開始處理檔案...")
    print("="*50)
    
    # 創建或連接索引
    index = create_or_connect_index()
    if index is None:
        print("無法創建或連接到 Pinecone 索引，程式終止")
        return
    
    # 讀取檔案
    print(f"正在讀取檔案: {file_path}")
    text_content = read_file(file_path)
    if not text_content:
        print("檔案內容為空或讀取失敗")
        return
    
    print(f"檔案讀取成功，總字符數: {len(text_content)}")
    
    # 文字分塊
    print("正在進行文字分塊...")
    chunks = chunk_text(text_content, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    print(f"分塊完成，總共生成 {len(chunks)} 個文字塊")
    
    # 生成嵌入向量
    print("正在生成嵌入向量...")
    embeddings = generate_embeddings(chunks)
    print(f"向量生成完成，向量維度: {len(embeddings[0])}")
    
    # 準備元數據
    metadata_list = [
        {
            "source_file": os.path.basename(file_path),
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "text_length": len(chunk)
        }
        for chunk in chunks
    ]
    
    # 儲存到 Pinecone
    print("正在儲存到 Pinecone...")
    store_to_pinecone(index, chunks, embeddings, metadata_list)
    
    # 驗證儲存結果
    stats = index.describe_index_stats()
    print(f"儲存完成！索引統計: {stats}")
    
    print("="*50)
    print("處理完成！")
    print("="*50)

# 13. 查詢函式 (用於測試)
def query_similar_texts(query_text: str, top_k: int = 5):
    """
    查詢相似文字
    
    Args:
        query_text: 查詢文字
        top_k: 返回最相似的前k個結果
    """
    try:
        index = pc.Index(INDEX_NAME)
        
        # 生成查詢向量
        query_embedding = embedding_model.encode([query_text]).tolist()[0]
        
        # 執行查詢
        results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        print(f"查詢: '{query_text}'")
        print("-" * 50)
        
        for i, match in enumerate(results['matches']):
            print(f"結果 {i+1} (相似度: {match['score']:.4f}):")
            print(f"文字: {match['metadata']['text'][:200]}...")
            print(f"來源: {match['metadata'].get('source_file', 'Unknown')}")
            print("-" * 30)
            
    except Exception as e:
        print(f"查詢時發生錯誤: {str(e)}")

# 14. 使用範例
if __name__ == "__main__":
    # 使用方法 1: 處理單個文字檔案
    # 請將 'your_text_file.txt' 替換為您的實際檔案路徑
    # process_text_file('your_text_file.txt', chunk_size=500, chunk_overlap=50)
    
    # 使用方法 2: 創建測試文字檔案並處理
    # 創建一個測試文字檔案
    test_content = """
    這是一個測試文件的內容。人工智慧是現代科技發展的重要領域之一。
    機器學習技術讓電腦能夠從資料中學習規律，並做出預測或決策。
    深度學習是機器學習的一個子領域，它使用神經網路來模擬人腦的運作方式。
    自然語言處理技術讓電腦能夠理解和生成人類語言。
    向量資料庫是儲存和檢索高維向量資料的專門資料庫系統。
    Pinecone 是一個流行的向量資料庫服務，專為機器學習應用而設計。
    """
    
    # 寫入測試檔案
    with open('test_document.txt', 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # 處理測試檔案
    print("正在處理測試檔案...")
    process_text_file('test_document.txt', chunk_size=200, chunk_overlap=20)
    
    # 測試查詢
    print("\n" + "="*50)
    print("測試查詢功能...")
    print("="*50)
    query_similar_texts("機器學習", top_k=3)

print("\n" + "="*60)
print("程式載入完成！")
print("="*60)
print("使用說明:")
print("1. 執行 process_text_file('your_file.txt') 來處理您的文字檔案")
print("2. 執行 query_similar_texts('您的查詢') 來搜尋相似文字")
print("3. 請確保將 'your_file.txt' 替換為您實際的檔案路徑")
print("="*60)