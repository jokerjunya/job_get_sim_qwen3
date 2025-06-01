from agents.base_agent import BaseAgent
from .schedule_agent import ScheduleAgent

class SimulatedInterviewer(BaseAgent):
    def __init__(self, name: str = "SimulatedInterviewer", description: str = "面接官をシミュレートするエージェント", info: dict = None):
        super().__init__(name, description)
        with open("prompts/interviewer_evaluate.txt", encoding="utf-8") as f:
            self.evaluate_prompt_template = f.read().strip()
        
        # 面接官情報を保持（jobs.jsonから渡される）
        self.info = info or {}
        
        # 日程調整エージェントのインスタンス化
        self.schedule_agent = ScheduleAgent()

    async def generate_question(self, job: dict, stage: str = None, seeker_profile: dict = None, resume: str = None) -> str:
        # 面接ステージごとにプロンプトを切り替え
        if stage == "一次面接":
            prompt_path = "prompts/interviewer_question_stage1.txt"
        elif stage == "二次面接":
            prompt_path = "prompts/interviewer_question_stage2.txt"
        elif stage == "最終面接":
            prompt_path = "prompts/interviewer_question_stage3.txt"
        else:
            prompt_path = "prompts/interviewer_question.txt"
        with open(prompt_path, encoding="utf-8") as f:
            question_prompt_template = f.read().strip()
        # 応募者情報を要約して埋め込む
        seeker_info = ""
        if seeker_profile:
            values = ", ".join(seeker_profile.get("values", []))
            skills = ", ".join(seeker_profile.get("skills", []))
            current_job = seeker_profile.get("current_job", {})
            current_position = current_job.get("role", "")
            current_company = current_job.get("company", "")
            tags = ", ".join(seeker_profile.get("tags", []))
            seeker_info = f"応募者情報: {seeker_profile.get('name', '')}、現職: {current_company} {current_position}、スキル: {skills}、価値観: {values}、特徴: {tags}"
            
        # 履歴書情報があれば追加
        resume_info = f"\n\n応募者の履歴書:\n{resume}" if resume else ""
            
        prompt = question_prompt_template.format(
            job_title=job['title'], 
            company=job['company'],
            seeker_info=seeker_info,
            resume=resume_info
        )
        return await self.llm.generate_content_async(prompt, agent_name="SimulatedInterviewer（面接官AI）")

    async def evaluate_answer(self, answer: str) -> str:
        # 求職者の回答をQwen3で評価
        prompt = self.evaluate_prompt_template.format(answer=answer)
        return await self.llm.generate_content_async(prompt, agent_name="SimulatedInterviewer（面接官AI）") 
    
    def schedule_interview(self, seeker_data: dict, stage: str = "一次面接", company_name: str = "", position: str = "") -> dict:
        """
        面接の日程調整を行う（新しいschedule_interviewメソッドを使用）
        
        Args:
            seeker_data: 求職者データ（availabilityフィールドを含む）
            stage: 面接ステージ（"一次面接"、"二次面接"、"最終面接"など）
            company_name: 会社名（メール送信時に使用）
            position: 職種（メール送信時に使用）
            
        Returns:
            調整結果の詳細辞書 または None
        """
        
        # ステージ情報を表示
        print(f"📅 {stage}の日程調整を開始します...")
        
        result = self.schedule_agent.schedule_interview(
            seeker_data=seeker_data,
            interviewer_info=self.info,
            company_name=company_name,
            position=position
        )
        
        # 結果に応じた出力
        if result["status"] == "auto_scheduled":
            print(f"✅ 自動調整成功: {result['message']}")
            return result["scheduled_slot"]
        
        elif result["status"] == "email_sent":
            print(f"📧 メール送信完了: {result['message']}")
            print("面接官からの返信をお待ちください。")
            # メール送信の場合はrequest_idも含めて返す
            return {
                "status": "email_sent",
                "request_id": result["request_id"],
                "candidate_slots": result["candidate_slots"]
            }
        
        elif result["status"] == "failed":
            print(f"❌ 日程調整失敗: {result['message']}")
            print("=" * 50)
            return None
        
        else:
            print(f"⚠️ 不明なステータス: {result}")
            return None
    
    # 後方互換性のため旧メソッド名も残す
    def schedule_first_interview(self, seeker_data: dict, company_name: str = "", position: str = "") -> dict:
        """後方互換性のための旧メソッド名（一次面接専用）"""
        return self.schedule_interview(seeker_data, "一次面接", company_name, position) 