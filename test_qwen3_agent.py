import asyncio
import uuid
import requests
import json
import re
from google.adk.agents import LlmAgent
from google.adk.models import LLMRegistry, BaseLlm
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions.in_memory_session_service import InMemorySessionService

class Qwen3Llm(BaseLlm):
    @staticmethod
    def supported_models():
        return [r"ollama/qwen3:30b-a3b"]

    async def generate_content_async(self, prompt, **kwargs):
        def sync_request():
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen3:30b-a3b",
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
            return result
        return await asyncio.to_thread(sync_request)

LLMRegistry.register(Qwen3Llm)

async def main():
    session_service = InMemorySessionService()
    app_name = "qwen3_app"
    user_id = "user1"
    session = session_service.create_session(app_name=app_name, user_id=user_id)
    agent = LlmAgent(
        name="qwen3_agent",
        model="ollama/qwen3:30b-a3b"
    )
    ctx = InvocationContext(
        session_service=session_service,
        invocation_id="e-" + str(uuid.uuid4()),
        agent=agent,
        session=session
    )
    # コーディング支援用プロンプト
    prompt = 'Debug this Python code: prnt("Hello, World!")'
    llm = Qwen3Llm(model="ollama/qwen3:30b-a3b")
    result = await llm.generate_content_async(prompt)
    result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL)
    print("result:", result.strip())

if __name__ == "__main__":
    asyncio.run(main())