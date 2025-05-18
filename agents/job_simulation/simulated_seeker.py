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

    async def application_reason(self, seeker_profile: dict, job: dict) -> str:
        with open("prompts/seeker_application_reason.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        # 必要な値を抽出
        seeker_name = seeker_profile.get("name", "")
        current_job = seeker_profile.get("current_job", {})
        current_company = current_job.get("company", "")
        current_role = current_job.get("role", "")
        current_period = current_job.get("period", "")
        skills = seeker_profile.get("skills", [])
        skill1 = skills[0] if len(skills) > 0 else ""
        skill2 = skills[1] if len(skills) > 1 else ""
        values = ", ".join(seeker_profile.get("values", []))
        pr = f"{seeker_name}は{current_company}で{current_role}として活躍し、{skill1}などのスキルを活かしてきました。{values}を大切にし、現場の課題解決やチームでの協働に強みがあります。新しい環境でも自律的に挑戦し、社会に貢献したいと考えています。"
        job_position = job.get("position", "")
        job_company = job.get("company", "")
        job_mission = job.get("mission", "")
        job_culture = ", ".join(job.get("culture_keywords", []))
        job_persona = job.get("persona", "")
        # 推しポイント（例：成長意欲や協調性など）
        push_point = "成長意欲と協調性、困難な状況でもやり抜く粘り強さ"
        prompt = prompt_template.format(
            seeker_name=seeker_name,
            current_company=current_company,
            current_role=current_role,
            current_period=current_period,
            skill1=skill1,
            skill2=skill2,
            values=values,
            pr=pr,
            job_position=job_position,
            job_company=job_company,
            job_mission=job_mission,
            job_culture=job_culture,
            job_persona=job_persona,
            push_point=push_point
        )
        reason = await self.llm.generate_content_async(prompt)
        return reason.strip() 