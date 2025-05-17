from agents.base_agent import BaseAgent

class EmployerAgent(BaseAgent):
    def __init__(self, name: str = "EmployerAgent", description: str = "企業の意思決定を行うエージェント"):
        super().__init__(name, description)

    async def evaluate_applicant(self, applicant_profile: dict, job: dict) -> dict:
        # シンプルな評価例
        score = 0
        if any(skill in applicant_profile["skills"] for skill in job.get("tech_stack", [])):
            score += 1
        if job.get("work_style") == applicant_profile["hope_conditions"]["work_style"]:
            score += 1
        if job.get("salary", 0) >= applicant_profile["hope_conditions"]["min_salary"]:
            score += 1
        return {"score": score, "decision": score >= 2}

    def screen_resume(self, resume: str):
        # TODO: 後でLLMによる内容評価・フィードバック生成に拡張
        # まずは必ず合格・簡単なフィードバックを返す
        return True, "書類選考合格です。次のステップへ進みます。"

    async def update_offer(self, offer: dict, request: str) -> str:
        with open("prompts/offer_negotiation_employer.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template.format(offer=offer, request=request)
        new_offer = await self.llm.generate_content_async(prompt)
        return new_offer.strip() 