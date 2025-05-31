from agents.base_agent import BaseAgent
import random
import json
import re

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
        return await self.llm.generate_content_async(prompt, agent_name="SimulatedSeeker（求職者）")

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
            seeker_profile=seeker_info
        )
        return await self.llm.generate_content_async(prompt, agent_name="SimulatedSeeker（求職者）")

    async def decide_offer(self, offer: dict, seeker_profile: dict = None, job: dict = None, interview_evaluations: list = None) -> dict:
        """
        オファー受諾判断を対話形式で行う。
        「問い × 間 × 例」のフレームワークを使って、納得感のある意思決定プロセスを表現する。
        
        Args:
            offer: オファー内容の辞書（年収、入社日など）
            seeker_profile: 求職者プロフィール
            job: 求人情報
            interview_evaluations: 面接評価のリスト
            
        Returns:
            dict: 決断結果と会話内容
        """
        with open("prompts/seeker_offer_conversation.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        
        # 迷いスコアの計算（より現実的で多角的に）
        hesitation_score = 0
        hesitation_factors = []  # 迷いの要因を記録
        
        if seeker_profile:
            # 1. 年収面での考慮（より細かく）
            hope_salary = seeker_profile.get("hope_conditions", {}).get("min_salary", 0)
            offer_salary = offer.get("年収", 0)
            if hope_salary > 0 and offer_salary > 0:
                salary_gap = (hope_salary - offer_salary) / hope_salary
                if salary_gap > 0.2:  # 希望より20%以上低い
                    hesitation_score += 3
                    hesitation_factors.append("年収が期待より大幅に低い")
                elif salary_gap > 0.1:  # 希望より10%以上低い
                    hesitation_score += 2
                    hesitation_factors.append("年収が期待より低い")
                elif salary_gap > 0:  # 少しでも低い
                    hesitation_score += 1
                    hesitation_factors.append("年収が期待をわずかに下回る")
                elif salary_gap <= -0.2:  # 希望より20%以上高い（逆に不安になる）
                    hesitation_score += 1
                    hesitation_factors.append("年収が高すぎて責任への不安")
            
            # 2. キャリア成長への不安（現職歴から推測）
            current_job = seeker_profile.get("current_job", {})
            current_period = current_job.get("period", "")
            if "現在" in current_period or "2024" in current_period:
                # 現職歴が短い（1-2年）場合は転職への不安
                hesitation_score += 1
                hesitation_factors.append("現職歴が短く転職への不安")
            
            # 3. ワークライフバランスへの懸念
            if "家族" in seeker_profile.get("context", "") or "子ども" in seeker_profile.get("context", ""):
                hesitation_score += 1
                hesitation_factors.append("家族との時間への配慮")
            
            # 4. 価値観の一致度（逆に一致しすぎても不安になる要因）
            if job and "culture_keywords" in job:
                seeker_values = seeker_profile.get("values", [])
                job_culture = job["culture_keywords"]
                values_match = sum(1 for v in seeker_values if v in job_culture)
                if values_match == 0:
                    hesitation_score += 2
                    hesitation_factors.append("価値観の不一致")
                elif values_match == len(seeker_values):  # 100%一致は逆に不安
                    hesitation_score += 0.5
                    hesitation_factors.append("価値観が一致しすぎることへの若干の不安")
                
            # 5. 面接での印象や不安要素
            if interview_evaluations:
                for eval in interview_evaluations:
                    if "課題" in eval or "改善" in eval:
                        hesitation_score += 0.5
                        hesitation_factors.append("面接で指摘された課題への不安")
            
            # 6. 新しい環境への適応不安（転職共通の不安）
            hesitation_score += 1
            hesitation_factors.append("新しい環境への適応への不安")
            
            # 7. 現職への愛着・義理（必ず発生する要因）
            hesitation_score += 1
            hesitation_factors.append("現職への愛着や同僚・会社への義理")
        
        # 迷いの度合いに応じたターン数の決定（調整）
        if hesitation_score >= 4:
            turns = "many"  # 多数のターン（5回以上）
        elif hesitation_score >= 2:
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
        
        conversation = await self.llm.generate_content_async(prompt, agent_name="SimulatedSeeker（求職者）")
        
        # より精密な決断抽出ロジック
        conversation_lines = conversation.strip().split('\n')
        final_decision = None
        decision_confidence = 0
        
        # 明示的な決断表現を探す（優先度高）
        accept_patterns = [
            r'受諾します', r'受け入れます', r'挑戦.*します', r'お受けします',
            r'受諾.*決めました', r'受けること.*決めました', r'やってみます'
        ]
        reject_patterns = [
            r'辞退します', r'見送.*します', r'お断りします', r'辞退.*決めました',
            r'見送.*決めました', r'今回.*見送', r'残る.*決めました'
        ]
        
        # 最後の5行を重点的にチェック
        for line in reversed(conversation_lines[-5:]):
            line_lower = line.lower().strip()
            
            # 受諾の明示的表現
            for pattern in accept_patterns:
                if re.search(pattern, line):
                    final_decision = True
                    decision_confidence = 3
                    break
            
            # 辞退の明示的表現  
            for pattern in reject_patterns:
                if re.search(pattern, line):
                    final_decision = False
                    decision_confidence = 3
                    break
                    
            if decision_confidence == 3:  # 明確な決断が見つかった
                break
        
        # 明示的な表現が見つからない場合、全体的なトーンから判断
        if decision_confidence < 3:
            conversation_text = conversation.lower()
            accept_words = conversation_text.count('受諾') + conversation_text.count('受け入れ') + conversation_text.count('挑戦')
            reject_words = conversation_text.count('辞退') + conversation_text.count('見送') + conversation_text.count('残る')
            
            if accept_words > reject_words:
                final_decision = True
                decision_confidence = 1
            elif reject_words > accept_words:
                final_decision = False
                decision_confidence = 1
            else:
                # デフォルトは受諾（迷いが少ない場合）
                final_decision = True if hesitation_score < 3 else False
                decision_confidence = 0
        
        # デバッグ情報の出力
        decision_text = "受諾" if final_decision else "辞退"
        confidence_text = ["推測", "傾向判断", "明確な表現", "明示的決断"][min(decision_confidence, 3)]
        print(f"決断抽出: {decision_text} (信頼度: {confidence_text}, スコア: {hesitation_score})")
        
        return {
            "decision": final_decision,
            "conversation": conversation.strip(),
            "hesitation_score": hesitation_score,
            "hesitation_factors": hesitation_factors,
            "decision_confidence": decision_confidence
        }

    async def self_introduction(self) -> str:
        with open("prompts/seeker_self_introduction.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template
        intro = await self.llm.generate_content_async(prompt, agent_name="SimulatedSeeker（求職者）")
        return intro.strip()

    async def job_question(self, job_proposal: str) -> str:
        with open("prompts/seeker_job_question.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template.format(job_proposal=job_proposal)
        question = await self.llm.generate_content_async(prompt, agent_name="SimulatedSeeker（求職者）")
        return question.strip()

    async def job_final_decision(self, job_proposal: str) -> str:
        with open("prompts/seeker_job_final_decision.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template.format(job_proposal=job_proposal)
        decision = await self.llm.generate_content_async(prompt, agent_name="SimulatedSeeker（求職者）")
        return decision.strip()

    async def start_conversation(self, seeker_profile: dict) -> str:
        with open("prompts/seeker_life_topic.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template.format(seeker_profile=seeker_profile)
        conversation = await self.llm.generate_content_async(prompt, agent_name="SimulatedSeeker（求職者）")
        return conversation.strip()

    async def reply_in_conversation(self, history: str) -> str:
        with open("prompts/seeker_reply.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template.format(history=history)
        reply = await self.llm.generate_content_async(prompt, agent_name="SimulatedSeeker（求職者）")
        return reply.strip()

    async def job_intent(self, job_pitch: str) -> str:
        with open("prompts/seeker_job_intent.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template.format(job_pitch=job_pitch)
        intent = await self.llm.generate_content_async(prompt, agent_name="SimulatedSeeker（求職者）")
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
        reason = await self.llm.generate_content_async(prompt, agent_name="SimulatedSeeker（求職者）")
        return reason.strip() 