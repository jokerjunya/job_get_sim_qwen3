from agents.qwen3_setup import setup_qwen3
setup_qwen3()

import asyncio
from agents.conversation_role_a_agent import ConversationRoleAAgent
from agents.conversation_role_b_agent import ConversationRoleBAgent

async def main():
    agent_a = ConversationRoleAAgent()
    agent_b = ConversationRoleBAgent()

    message = "こんにちは、はじめまして。"
    print(f"A: {message}")

    for i in range(3):  # 3ターン会話
        response_b = await agent_b.respond(message)
        print(f"B: {response_b}")
        response_a = await agent_a.respond(response_b)
        print(f"A: {response_a}")
        message = response_a

if __name__ == "__main__":
    asyncio.run(main()) 