from agents.base_agent import BaseAgent

class SimulatedInterviewer(BaseAgent):
    def __init__(self, name: str = "SimulatedInterviewer", description: str = "面接官の役割を担うエージェント"):
        super().__init__(name, description)
        with open("prompts/interviewer_evaluate.txt", encoding="utf-8") as f:
            self.evaluate_prompt_template = f.read().strip()

    async def generate_question(self, job: dict, stage: str = None) -> str:
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
        prompt = question_prompt_template.format(job_title=job['title'], company=job['company'])
        return await self.llm.generate_content_async(prompt)

    async def evaluate_answer(self, answer: str) -> str:
        # 求職者の回答をQwen3で評価
        prompt = self.evaluate_prompt_template.format(answer=answer)
        return await self.llm.generate_content_async(prompt) 