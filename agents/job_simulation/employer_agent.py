from agents.base_agent import BaseAgent

class EmployerAgent(BaseAgent):
    def __init__(self, name: str = "EmployerAgent", description: str = "企業の意思決定を行うエージェント"):
        super().__init__(name, description)

    async def evaluate_applicant(self, applicant_profile: dict, job: dict) -> dict:
        # 新しい構造に対応したスコアリング例
        score = 0
        if any(skill in applicant_profile.get("skills", []) for skill in job.get("tech_stack", [])):
            score += 1
        if job.get("work_style") == applicant_profile["hope_conditions"]["work_style"]:
            score += 1
        if job.get("salary", 0) >= applicant_profile["hope_conditions"]["min_salary"]:
            score += 1
        # 価値観やタグも加点要素にできる
        if any(kw in job.get("culture_keywords", []) for kw in applicant_profile["hope_conditions"].get("culture_keywords", [])):
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

    def create_job_posting(self, hr_agent) -> dict:
        """
        SimulatedHRから要望を受け取り、求人票（dict）を生成して返す。
        仕事内容・ミッション・チーム・成長機会・独自の魅力・求める人物像なども自動生成して付与する。
        """
        needs = hr_agent.provide_needs()
        # --- リッチな項目の自動生成 ---
        # 仕事内容・ミッション
        mission = f"{needs.get('position', 'ポジション')}として、{needs.get('background', '新規事業')}に挑戦し、社会に新しい価値を生み出す役割です。"
        # チーム・社風
        team = f"{', '.join(needs.get('culture_keywords', []))}を大切にする多様なメンバーが活躍中。協力し合いながら成長できる環境です。"
        # 成長機会
        growth = f"{needs.get('skills', ['多様なスキル'])}を活かしつつ、最先端のAI技術やクラウド開発に携わりながらスキルアップできます。"
        # 独自の魅力
        unique = f"フルリモート可、柔軟な働き方、挑戦を後押しするカルチャーなど、他社にはない魅力が多数。"
        # 求める人物像
        persona = f"{', '.join(needs.get('skills', []))}の経験があり、{', '.join(needs.get('culture_keywords', []))}を大切にできる方を歓迎します。"

        job_posting = {
            "id": f"job_{self.name}",
            "title": needs.get("position"),
            "position": needs.get("position"),
            "company": "Simulated Company",
            "background": needs.get("background"),
            "tech_stack": needs.get("skills", []),
            "work_style": needs.get("work_style"),
            "salary": needs.get("min_salary"),
            "culture_keywords": needs.get("culture_keywords", []),
            "created_by": self.name,
            # 追加リッチ項目
            "mission": mission,
            "team": team,
            "growth": growth,
            "unique": unique,
            "persona": persona
        }
        return job_posting 