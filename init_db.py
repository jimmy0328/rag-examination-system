#!/usr/bin/env python3
"""
資料庫初始化腳本
用於將文件上傳到 Pinecone 向量資料庫
"""

import os
import sys
from dotenv import load_dotenv
from vectorStore import process_file, create_or_connect_index
from pinecone import Pinecone

def clear_index():
    """清除 Pinecone 索引中的所有向量"""
    print("🗑️  正在清除向量資料庫...")
    
    try:
        load_dotenv()
        pinecone_api_key = os.getenv('PINECONE_API_KEY')
        
        if not pinecone_api_key or pinecone_api_key == 'your_pinecone_api_key_here':
            print("❌ PINECONE_API_KEY 未設定")
            return False
        
        pc = Pinecone(api_key=pinecone_api_key)
        index_name = "text-chunks-index"
        
        # 檢查索引是否存在
        existing_indexes = pc.list_indexes()
        if index_name not in [idx.name for idx in existing_indexes]:
            print("ℹ️  索引不存在，無需清除")
            return True
        
        # 連接到索引
        index = pc.Index(index_name)
        
        # 獲取索引統計信息
        stats = index.describe_index_stats()
        total_vectors = stats.get('total_vector_count', 0)
        
        if total_vectors == 0:
            print("ℹ️  索引為空，無需清除")
            return True
        
        print(f"📊 發現 {total_vectors} 個向量，正在清除...")
        
        # 刪除索引並重新創建
        pc.delete_index(index_name)
        print("✅ 索引已刪除")
        
        # 等待刪除完成
        import time
        time.sleep(5)
        
        print("✅ 向量資料庫清除完成")
        return True
        
    except Exception as e:
        print(f"❌ 清除向量資料庫時發生錯誤: {str(e)}")
        return False

def main():
    """主函數"""
    print("=" * 60)
    print("🚀 RAG 系統資料庫初始化")
    print("=" * 60)
    
    # 載入環境變數
    load_dotenv()
    
    # 檢查環境變數
    pinecone_api_key = os.getenv('PINECONE_API_KEY')
    if not pinecone_api_key or pinecone_api_key == 'your_pinecone_api_key_here':
        print("❌ 請在 .env 檔案中設定有效的 PINECONE_API_KEY")
        return
    
    # 先清除向量資料庫
    if not clear_index():
        print("❌ 清除向量資料庫失敗，操作已取消")
        return
    
    # 檢查是否有文件需要處理
    files_to_process = []
    
    # 檢查支援的文件格式 (.txt 和 .pdf)
    for file in os.listdir('data'):
        if file.endswith(('.txt', '.pdf')):
            files_to_process.append(os.path.join('data', file))
    
    if not files_to_process:
        print("❌ 沒有找到任何支援的文件可以處理")
        print("請將您的 .txt 或 .pdf 文件放在 data/ 目錄中")
        return
    
    print(f"📁 找到 {len(files_to_process)} 個文件需要處理:")
    for file in files_to_process:
        print(f"   - {file}")
    
    # 確認是否繼續
    response = input("\n是否要開始處理這些文件？(y/n): ").strip().lower()
    if response not in ['y', 'yes', '是']:
        print("❌ 操作已取消")
        return
    
    # 處理每個文件
    for file in files_to_process:
        print(f"\n📖 正在處理文件: {file}")
        print("-" * 40)
        
        try:
            process_file(file, chunk_size=500, chunk_overlap=50)
            print(f"✅ {file} 處理完成")
        except Exception as e:
            print(f"❌ 處理 {file} 時發生錯誤: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎉 資料庫初始化完成！")
    print("=" * 60)
    print("現在您可以啟動 Flask 應用程式:")
    print("   python app.py")
    print("=" * 60)

def test_connection():
    """測試 Pinecone 連接"""
    print("🔍 測試 Pinecone 連接...")
    
    try:
        load_dotenv()
        pinecone_api_key = os.getenv('PINECONE_API_KEY')
        
        if not pinecone_api_key or pinecone_api_key == 'your_pinecone_api_key_here':
            print("❌ PINECONE_API_KEY 未設定")
            return False
        
        pc = Pinecone(api_key=pinecone_api_key)
        indexes = pc.list_indexes()
        
        print(f"✅ Pinecone 連接成功")
        print(f"📊 可用索引: {[idx.name for idx in indexes]}")
        return True
        
    except Exception as e:
        print(f"❌ Pinecone 連接失敗: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_connection()
    else:
        main() 