from agents.base_agent import BaseAgent
import random
import json

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

    async def answer_interview(self, question: str, seeker_profile: dict = None) -> str:
        # 面接質問への応答をQwen3で生成
        # 応募者情報を要約して埋め込む
        seeker_info = ""
        if seeker_profile:
            name = seeker_profile.get("name", "")
            values = ", ".join(seeker_profile.get("values", []))
            skills = ", ".join(seeker_profile.get("skills", []))
            current_job = seeker_profile.get("current_job", {})
            current_position = current_job.get("role", "")
            current_company = current_job.get("company", "")
            experience = seeker_profile.get("experience", "")
            tags = ", ".join(seeker_profile.get("tags", []))
            
            seeker_info = f"""
あなたは以下の特徴を持つ求職者です：
- 名前: {name}
- 現職: {current_company} {current_position}
- スキル: {skills}
- 価値観: {values}
- 経験: {experience}
- 特徴: {tags}

あなたの特徴・経歴・価値観に基づいて、具体的なエピソードや実際の経験を交えながら回答してください。
"""
            
        prompt = self.answer_interview_prompt_template.format(
            question=question,
            seeker_info=seeker_info
        )
        return await self.llm.generate_content_async(prompt)

    async def decide_offer(self, offer: dict, seeker_profile: dict = None, job: dict = None, interview_evaluations: list = None) -> bool:
        """
        オファー受諾判断を対話形式で行う。
        「問い × 間 × 例」のフレームワークを使って、納得感のある意思決定プロセスを表現する。
        
        Args:
            offer: オファー内容の辞書（年収、入社日など）
            seeker_profile: 求職者プロフィール
            job: 求人情報
            interview_evaluations: 面接評価のリスト
            
        Returns:
            bool: Trueなら受諾、Falseなら辞退
        """
        with open("prompts/seeker_offer_conversation.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        
        # 迷いスコアの計算
        hesitation_score = 0
        if seeker_profile:
            # 希望年収と実際のオファー年収の差
            hope_salary = seeker_profile.get("hope_conditions", {}).get("min_salary", 0)
            offer_salary = offer.get("年収", 0)
            if hope_salary > 0 and offer_salary > 0:
                salary_gap = (hope_salary - offer_salary) / hope_salary  # 相対的な差
                if salary_gap > 0.2:  # 希望より20%以上低い
                    hesitation_score += 2
                elif salary_gap > 0:  # 少しでも低い
                    hesitation_score += 1
            
            # 価値観との一致度
            if job and "culture_keywords" in job:
                values_match = sum(1 for v in seeker_profile.get("values", []) if v in job["culture_keywords"])
                if values_match == 0:
                    hesitation_score += 1
                
            # 面接の印象
            if interview_evaluations:
                negative_count = sum(1 for eval in interview_evaluations if "不合格" in eval or "見送り" in eval)
                if negative_count > 0:
                    hesitation_score += 1
        
        # 迷いの度合いに応じたターン数の決定
        if hesitation_score >= 3:
            turns = "many"  # 多数のターン（5回以上）
        elif hesitation_score >= 1:
            turns = "some"  # 適度なターン（3-4回）
        else:
            turns = "few"   # 少数のターン（1-2回）
        
        prompt = prompt_template.format(
            offer=json.dumps(offer, ensure_ascii=False),
            seeker_profile=json.dumps(seeker_profile, ensure_ascii=False) if seeker_profile else "{}",
            job=json.dumps(job, ensure_ascii=False) if job else "{}",
            interview_evaluations=json.dumps(interview_evaluations, ensure_ascii=False) if interview_evaluations else "[]",
            hesitation_score=hesitation_score,
            turns=turns
        )
        
        conversation = await self.llm.generate_content_async(prompt)
        
        # 会話から最終判断を抽出
        decision_text = conversation.strip().lower()
        # 最後のseekerとseekerAIの発言をチェック
        final_lines = [line.strip().lower() for line in conversation.strip().split('\n') if line.strip()]
        # 最後の発言が「受諾」または「辞退」を明示的に含むかチェック
        final_statements = []
        for line in final_lines[-5:]:  # 最後の5行程度をチェック
            if "受諾" in line or "accept" in line or "受け入れ" in line or "決めました" in line:
                final_statements.append("accept")
            elif "辞退" in line or "reject" in line or "見送" in line:
                final_statements.append("reject")
                
        # 最終判断の決定（デフォルトは会話全体から判断）
        final_decision = True  # デフォルトは受諾
        if final_statements:
            # 明示的な表明があれば最後の表明を採用
            final_decision = final_statements[-1] == "accept"
        else:
            # 明示的な表明がなければ会話全体から判断
            final_decision = "受諾" in decision_text or "accept" in decision_text or "受け入れ" in decision_text
            if "辞退" in decision_text or "reject" in decision_text or "見送" in decision_text:
                final_decision = False
        
        # 最終判断を確認（ログ表示）
        print(f"決断抽出: {'受諾' if final_decision else '辞退'}")
        
        return {
            "decision": final_decision,
            "conversation": conversation.strip()
        }

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