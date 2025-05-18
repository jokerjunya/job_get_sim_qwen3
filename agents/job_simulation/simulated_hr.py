class SimulatedHR:
    """
    企業の人事担当（人間役）をシミュレートするクラス。
    求人の意図や要望を持ち、EmployerAgentと会話しながら求人票を作成する。
    """
    def __init__(self, name: str = "SimulatedHR", llm=None):
        self.name = name
        self.llm = llm
        # 例: どんな人材が欲しいか、どんな背景で採用したいか等の初期要望
        self.basic_needs = {
            "position": "AIエンジニア",
            "background": "新規AIプロダクト開発のための増員",
            "skills": ["Python", "LLM", "クラウド経験"],
            "work_style": "フルリモート可",
            "min_salary": 700,
            "culture_keywords": ["自律性", "挑戦", "チームワーク"]
        }

    def provide_needs(self) -> dict:
        """
        EmployerAgentからの質問に対して、求人の要望・意図を返す。
        """
        return self.basic_needs 

    async def opine_on_resume_screening(self, empai_judgement: dict) -> dict:
        """
        empaiの判定・理由を読んで、人事視点で意見・コメントを返す（LLM利用）。
        """
        with open("prompts/hr_resume_screening_opinion.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template.format(empai_judgement=empai_judgement["raw"])
        result = await self.llm.generate_content_async(prompt)
        # シンプルなパース（意見・コメント）
        lines = [l.strip() for l in result.split("\n") if l.strip()]
        opinion = {"raw": result, "opinion": None, "comment": None}
        for l in lines:
            if l.startswith("意見:"):
                if "賛成" in l:
                    opinion["opinion"] = "賛成"
                elif "反対" in l:
                    opinion["opinion"] = "反対"
            if l.startswith("コメント:"):
                opinion["comment"] = l.replace("コメント:", "").strip()
        return opinion 