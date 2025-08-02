#!/usr/bin/env python3
"""
RAG 系統啟動腳本
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """檢查環境設定"""
    print("🔍 檢查環境設定...")
    
    # 載入環境變數
    load_dotenv()
    
    # 檢查必要的環境變數
    required_vars = {
        'PINECONE_API_KEY': 'Pinecone API 金鑰',
        'GEMINI_API_KEY': 'Gemini API 金鑰'
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value == f'your_{var.lower()}_here':
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        print("❌ 缺少必要的環境變數:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n請編輯 .env 檔案並填入正確的 API 金鑰")
        return False
    
    print("✅ 環境變數檢查通過")
    return True

def main():
    """主函數"""
    print("=" * 60)
    print("🚀 RAG 智能問答系統")
    print("=" * 60)
    
    # 檢查環境
    if not check_environment():
        sys.exit(1)
    
    # 檢查依賴
    try:
        import flask
        import pinecone
        import sentence_transformers
        import google.generativeai
        print("✅ 所有依賴已安裝")
    except ImportError as e:
        print(f"❌ 缺少依賴: {e}")
        print("請執行: pip install -r requirements.txt")
        sys.exit(1)
    
    # 啟動應用程式
    print("\n🌐 啟動 Flask 應用程式...")
    print("=" * 60)
    
    # 設定 Flask 環境變數
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'True'
    
    # 導入並啟動應用程式
    try:
        from app import app
        print("✅ 應用程式載入成功")
        print("🌍 訪問地址: http://localhost:5002")
        print("=" * 60)
        app.run(debug=True, host='0.0.0.0', port=5002)
    except Exception as e:
        print(f"❌ 應用程式啟動失敗: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 