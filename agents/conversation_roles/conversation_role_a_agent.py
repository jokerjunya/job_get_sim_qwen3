from agents.base_agent import BaseAgent

class ConversationRoleAAgent(BaseAgent):
    def __init__(self, name: str = "RoleA", description: str = "会話エージェントAの役割"):
        super().__init__(name, description)
        with open("prompts/role_a_system.txt", encoding="utf-8") as f:
            self.system_prompt = f.read().strip()
    
    async def respond(self, message: str) -> str:
        prompt = f"{self.system_prompt}\n\nキャリアアドバイザーからのメッセージ: {message}\nあなたの返答:"
        return await self.llm.generate_content_async(prompt) 