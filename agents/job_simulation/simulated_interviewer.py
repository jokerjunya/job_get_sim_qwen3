from agents.base_agent import BaseAgent

class SimulatedInterviewer(BaseAgent):
    def __init__(self, name: str = "SimulatedInterviewer", description: str = "面接官の役割を担うエージェント"):
        super().__init__(name, description)
        with open("prompts/interviewer_evaluate.txt", encoding="utf-8") as f:
            self.evaluate_prompt_template = f.read().strip()

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
        return await self.llm.generate_content_async(prompt)

    async def evaluate_answer(self, answer: str) -> str:
        # 求職者の回答をQwen3で評価
        prompt = self.evaluate_prompt_template.format(answer=answer)
        return await self.llm.generate_content_async(prompt) 