from agents.base_agent import BaseAgent
import random

class SimulatedSeeker(BaseAgent):
    def __init__(self, name: str = "SimulatedSeeker", description: str = "求職者の人格・感情を再現するエージェント"):
        super().__init__(name, description)
        with open("prompts/seeker_motivation.txt", encoding="utf-8") as f:
            self.motivation_prompt_template = f.read().strip()
        with open("prompts/seeker_answer_interview.txt", encoding="utf-8") as f:
            self.answer_interview_prompt_template = f.read().strip()

    async def generate_motivation(self, job: dict) -> str:
        # 志望動機をQwen3で生成
        prompt = self.motivation_prompt_template.format(job_title=job['title'], company=job['company'])
        return await self.llm.generate_content_async(prompt)

    async def answer_interview(self, question: str) -> str:
        # 面接質問への応答をQwen3で生成
        prompt = self.answer_interview_prompt_template.format(question=question)
        return await self.llm.generate_content_async(prompt)

    async def decide_offer(self, offer: dict) -> bool:
        # オファー受諾判断（ランダム例）
        return random.choice([True, False])

    async def self_introduction(self) -> str:
        with open("prompts/seeker_self_introduction.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template
        intro = await self.llm.generate_content_async(prompt)
        return intro.strip()

    async def job_question(self, job_proposal: str) -> str:
        with open("prompts/seeker_job_question.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template.format(job_proposal=job_proposal)
        question = await self.llm.generate_content_async(prompt)
        return question.strip()

    async def job_final_decision(self, job_proposal: str) -> str:
        with open("prompts/seeker_job_final_decision.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template.format(job_proposal=job_proposal)
        decision = await self.llm.generate_content_async(prompt)
        return decision.strip()

    async def start_conversation(self, seeker_profile: dict) -> str:
        with open("prompts/seeker_life_topic.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template.format(seeker_profile=seeker_profile)
        conversation = await self.llm.generate_content_async(prompt)
        return conversation.strip()

    async def reply_in_conversation(self, history: str) -> str:
        with open("prompts/seeker_reply.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template.format(history=history)
        reply = await self.llm.generate_content_async(prompt)
        return reply.strip()

    async def job_intent(self, job_pitch: str) -> str:
        with open("prompts/seeker_job_intent.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template.format(job_pitch=job_pitch)
        intent = await self.llm.generate_content_async(prompt)
        return intent.strip()

    async def application_reason(self, job_intent: str) -> str:
        with open("prompts/seeker_application_reason.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template.format(job_intent=job_intent)
        reason = await self.llm.generate_content_async(prompt)
        return reason.strip() 