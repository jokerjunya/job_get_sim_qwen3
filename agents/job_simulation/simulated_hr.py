class SimulatedHR:
    """
    企業の人事担当（人間役）をシミュレートするクラス。
    求人の意図や要望を持ち、EmployerAgentと会話しながら求人票を作成する。
    """
    def __init__(self, name: str = "SimulatedHR"):
        self.name = name
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