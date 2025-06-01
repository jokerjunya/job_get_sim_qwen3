from agents.base_agent import BaseAgent

class SimulatedHR(BaseAgent):
    """
    企業の人事担当（人間役）をシミュレートするクラス。
    求人の意図や要望を持ち、EmployerAgentと会話しながら求人票を作成する。
    """
    def __init__(self, name: str = "SimulatedHR", description: str = "企業の人事担当者をシミュレートするエージェント"):
        super().__init__(name, description)
        # デフォルトの基本要望（フォールバック用）
        self.basic_needs = {
            "position": "AI/MLエンジニア",
            "background": "急成長中のAIプロダクト開発で機械学習基盤を構築・運用",
            "skills": ["Python", "TensorFlow", "AWS", "Docker"],
            "work_style": "リモート可",
            "min_salary": 700,
            "culture_keywords": ["挑戦", "自律", "チームワーク"]
        }
        # 動的な要望（求人パターンベース）
        self.dynamic_needs = None

    def set_needs_from_job_pattern(self, job_pattern: dict):
        """求人パターンに基づいてHR要望を動的に設定"""
        if not job_pattern:
            return
            
        # 年収レンジから最低年収を抽出
        salary_range = job_pattern.get('conditions', {}).get('salary_range', '500-700万円')
        import re
        numbers = re.findall(r'\d+', salary_range)
        min_salary = int(numbers[0]) if numbers else 500
        
        self.dynamic_needs = {
            "position": job_pattern.get('position', 'エンジニア'),
            "background": f"{job_pattern.get('industry', '成長')}業界で{job_pattern.get('mission', '事業を推進')}",
            "skills": job_pattern.get('requirements', {}).get('skills', ['プログラミング']),
            "work_style": job_pattern.get('conditions', {}).get('work_style', 'ハイブリッド'),
            "min_salary": min_salary,
            "culture_keywords": job_pattern.get('culture', ['成長', 'チームワーク'])
        }

    def provide_needs(self) -> dict:
        """
        EmployerAgentからの質問に対して、求人の要望・意図を返す。
        動的要望が設定されている場合はそれを、そうでなければデフォルトを返す。
        """
        return self.dynamic_needs if self.dynamic_needs else self.basic_needs

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