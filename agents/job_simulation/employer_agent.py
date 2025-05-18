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

    async def generate_initial_offer(self, seeker_profile: dict, job: dict, interview_evaluations: list = None) -> dict:
        """
        面接評価や求職者のスキル/経験を反映した初回オファーを生成する。
        
        Args:
            seeker_profile: 求職者プロフィール
            job: 求人情報
            interview_evaluations: 面接評価のリスト
            
        Returns:
            dict: 初回オファー（年収、入社日など）
        """
        # 基本オファー
        base_offer = {
            "年収": job.get("salary", 500),  # 求人の最低年収を基準
            "入社日": "2024-07-01",         # デフォルト入社日
            "役職": "一般社員",              # デフォルト役職
            "勤務形態": job.get("work_style", "フルタイム") # 求人の勤務形態
        }
        
        # 評価スコア計算
        evaluation_score = 0
        if interview_evaluations:
            # 面接評価からポジティブなキーワードをカウント
            positive_keywords = ["優れた", "高い", "素晴らしい", "適切", "強み", "合格", "推薦"]
            for evaluation in interview_evaluations:
                for keyword in positive_keywords:
                    if keyword in evaluation:
                        evaluation_score += 1
        
        # スキルマッチ度
        skill_match = 0
        if seeker_profile and "skills" in seeker_profile and "tech_stack" in job:
            skill_match = sum(1 for skill in seeker_profile["skills"] if skill in job["tech_stack"])
        
        # 経験値評価
        experience_score = 0
        if seeker_profile and "current_job" in seeker_profile:
            # 経験年数を考慮
            experience_years = seeker_profile.get("experience_years", 0)
            if experience_years > 10:
                experience_score = 3
            elif experience_years > 5:
                experience_score = 2
            elif experience_years > 2:
                experience_score = 1
            
            # 役職経験も考慮
            if "role" in seeker_profile["current_job"]:
                if "リーダー" in seeker_profile["current_job"]["role"] or "マネージャー" in seeker_profile["current_job"]["role"]:
                    experience_score += 1
        
        # 総合評価に基づいて年収調整
        total_score = evaluation_score + skill_match + experience_score
        
        # 年収調整（基本年収 + 評価によるボーナス）
        base_salary = base_offer["年収"]
        if total_score >= 8:  # 非常に高評価
            base_offer["年収"] = int(base_salary * 1.3)  # 30%増
            base_offer["役職"] = "シニアポジション"
        elif total_score >= 5:  # 高評価
            base_offer["年収"] = int(base_salary * 1.15)  # 15%増
        elif total_score >= 3:  # 良好
            base_offer["年収"] = int(base_salary * 1.05)  # 5%増
        
        # 希望年収も考慮
        hope_salary = seeker_profile.get("hope_conditions", {}).get("min_salary", 0)
        if hope_salary > 0 and base_offer["年収"] < hope_salary * 0.8:
            # 希望より20%以上低い場合は調整（ただし予算の範囲内で）
            base_offer["年収"] = min(int(hope_salary * 0.8), int(base_salary * 1.3))
        
        # 役職調整（経験やスキルに基づいて）
        if seeker_profile.get("tags", []) and ("リーダーシップ" in seeker_profile["tags"] or "マネジメント経験" in seeker_profile["tags"]):
            if total_score >= 5:
                base_offer["役職"] = "マネージャー"
        
        # 初期オファーのログ
        print(f"初期オファー生成 - 評価スコア: {total_score}, 年収: {base_offer['年収']}, 役職: {base_offer['役職']}")
        
        return base_offer

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

    async def screen_resume_llm(self, resume: str) -> dict:
        """
        LLMを使って書類審査（合否＋理由）を行う。
        """
        with open("prompts/employer_resume_screening.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template.format(resume=resume)
        result = await self.llm.generate_content_async(prompt)
        # シンプルなパース（合否・理由）
        lines = [l.strip() for l in result.split("\n") if l.strip()]
        judgement = {"raw": result, "decision": None, "reason": None}
        for l in lines:
            if l.startswith("合否:"):
                if "合格" in l:
                    judgement["decision"] = "合格"
                elif "不合格" in l:
                    judgement["decision"] = "不合格"
            if l.startswith("理由:"):
                judgement["reason"] = l.replace("理由:", "").strip()
        return judgement 