import requests
import json
import re

class Qwen3Llm:
    def __init__(self, model="ollama/qwen3:30b-a3b", api_url="http://localhost:11434/api/generate"):
        self.model = model
        self.api_url = api_url

    async def generate_content_async(self, prompt, **kwargs):
        import asyncio
        def sync_request():
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model.split("/")[-1],
                    "prompt": prompt,
                    "options": kwargs
                },
                stream=True
            )
            result = ""
            for line in response.iter_lines():
                if line:
                    try:
                        decoded = line.decode('utf-8')
                        data = json.loads(decoded)
                        if "response" in data and data["response"]:
                            result += data["response"]
                    except Exception:
                        continue
            # <think> ... </think> を除去
            result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL)
            return result.strip()
        return await asyncio.to_thread(sync_request) 