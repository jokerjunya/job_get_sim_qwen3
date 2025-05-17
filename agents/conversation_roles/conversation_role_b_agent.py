from agents.base_agent import BaseAgent

class ConversationRoleBAgent(BaseAgent):
    def __init__(self, name: str = "RoleB", description: str = "会話エージェントBの役割"):
        super().__init__(name, description)
        with open("prompts/role_b_system.txt", encoding="utf-8") as f:
            self.system_prompt = f.read().strip()
    
    async def respond(self, message: str) -> str:
        prompt = f"{self.system_prompt}\n\n求職者からのメッセージ: {message}\nあなたの返答:"
        return await self.llm.generate_content_async(prompt) 