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