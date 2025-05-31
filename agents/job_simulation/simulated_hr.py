from agents.base_agent import BaseAgent

class SimulatedHR(BaseAgent):
    """
    企業の人事担当（人間役）をシミュレートするクラス。
    求人の意図や要望を持ち、EmployerAgentと会話しながら求人票を作成する。
    """
    def __init__(self, name: str = "SimulatedHR", description: str = "企業の人事担当者をシミュレートするエージェント"):
        super().__init__(name, description)
        # 例: どんな人材が欲しいか、どんな背景で採用したいか等の初期要望
        self.basic_needs = {
            "position": "AI/MLエンジニア",
            "background": "急成長中のAIプロダクト開発で機械学習基盤を構築・運用",
            "skills": ["Python", "TensorFlow", "AWS", "Docker"],
            "work_style": "リモート可",
            "min_salary": 700,
            "culture_keywords": ["挑戦", "自律", "チームワーク"]
        }

    def provide_needs(self) -> dict:
        """
        EmployerAgentからの質問に対して、求人の要望・意図を返す。
        """
        return self.basic_needs 

    def provide_additional_requirements(self) -> dict:
        """追加の要件や詳細情報を提示"""
        return {
            "experience_years": 3,
            "education": "理系大学卒業以上",
            "language": "日本語ネイティブ、英語読み書き",
            "team_size": 5,
            "reporting_to": "ML部門長"
        }

    async def opine_on_resume_screening(self, resume: str, employer_decision: dict) -> dict:
        """書類選考結果に対するHR側の意見"""
        with open("prompts/hr_resume_screening_opinion.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template.format(resume=resume, empai_judgement=employer_decision)
        result = await self.llm.generate_content_async(prompt, agent_name="SimulatedHR（人事AI）")
        # パース（agree/disagreeと理由）
        lines = [l.strip() for l in result.split("\n") if l.strip()]
        opinion = {"raw": result, "stance": None, "reason": None}
        for l in lines:
            if l.startswith("意見:"):
                if "賛成" in l or "同意" in l:
                    opinion["stance"] = "agree"
                elif "反対" in l or "異議" in l:
                    opinion["stance"] = "disagree"
            if l.startswith("コメント:"):
                opinion["reason"] = l.replace("コメント:", "").strip()
        return opinion 