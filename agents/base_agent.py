from agents.qwen3_llm import Qwen3Llm

class BaseAgent:
    def __init__(self, name: str, description: str, model: str = "ollama/qwen3:30b-a3b"):
        self.name = name
        self.description = description
        self.model = model
        self.llm = Qwen3Llm(model=model) 