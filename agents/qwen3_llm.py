import requests
import json
import re

class Qwen3Llm:
    """
    Qwen3 LLMラッパークラス
    
    🔧 Thinking機能: OFFに設定済み
    - Qwen3のthinking機能は"think": Falseパラメータで無効化
    - 生成速度の向上とレスポンスの簡潔化を実現
    - <think>タグが含まれる場合は正規表現で除去
    """
    def __init__(self, model="ollama/qwen3:30b-a3b", api_url="http://localhost:11434/api/generate"):
        self.model = model
        self.api_url = api_url

    async def generate_content_async(self, prompt, agent_name=None, show_progress=True, progress_callback=None, **kwargs):
        import asyncio
        
        def sync_request():
            # 日本語応答を強制するプロンプト指示を追加
            enhanced_prompt = f"{prompt}\n\n※必ず日本語で回答してください。英語や中国語は使用しないでください。"
            
            # 進捗表示開始
            if show_progress and agent_name:
                print(f"🤖 {agent_name}が回答を生成中", end="", flush=True)
                if progress_callback:
                    progress_callback(f"🤖 {agent_name}が回答を生成中")
            elif show_progress:
                print("🤖 AI回答を生成中", end="", flush=True)
                if progress_callback:
                    progress_callback("🤖 AI回答を生成中")
            
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model.split("/")[-1],
                    "prompt": enhanced_prompt,
                    "stream": True,
                    "think": False,
                    **kwargs
                },
                stream=True
            )
            
            full_response = ""
            dot_count = 0
            
            try:
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            if 'response' in chunk:
                                full_response += chunk['response']
                                
                                # 進捗表示（ドット追加）
                                if show_progress:
                                    dot_count += 1
                                    if dot_count % 10 == 0:  # 10チャンクごとにドットを表示
                                        print(".", end="", flush=True)
                                
                                if chunk.get('done', False):
                                    break
                        except json.JSONDecodeError:
                            continue
            finally:
                # 完了メッセージ
                if show_progress:
                    print(" ✅完了", flush=True)
                    if progress_callback:
                        progress_callback("")  # 進捗表示をクリア
            
            # thinking部分を除去
            full_response = re.sub(r'<think>.*?</think>', '', full_response, flags=re.DOTALL)
            
            # 追加の不要な英語・中国語パターンを除去
            full_response = re.sub(r'Okay.*?\.', '', full_response, flags=re.DOTALL)
            full_response = re.sub(r'好的.*?。', '', full_response, flags=re.DOTALL)
            full_response = re.sub(r'Wait.*?\.', '', full_response, flags=re.DOTALL)
            full_response = re.sub(r'Let me.*?\.', '', full_response, flags=re.DOTALL)
            
            return full_response.strip()
        
        # 非同期実行
        return await asyncio.get_event_loop().run_in_executor(None, sync_request) 