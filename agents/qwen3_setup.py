import os

def setup_qwen3():
    # Qwen3 APIキーやエンドポイントの設定（必要に応じて編集）
    os.environ.setdefault("QWEN3_API_KEY", "your-key")
    os.environ.setdefault("QWEN3_API_URL", "http://localhost:11434/api/generate")
    # 他に必要な初期化があればここに追加 