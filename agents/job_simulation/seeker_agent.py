from agents.base_agent import BaseAgent

class SeekerAgent(BaseAgent):
    def __init__(self, name: str = "SeekerAgent", description: str = "求職者の意思決定を行うエージェント"):
        super().__init__(name, description)
        with open("prompts/seeker_reason.txt", encoding="utf-8") as f:
            self.reason_prompt_template = f.read().strip()
        with open("prompts/seeker_offer_decision.txt", encoding="utf-8") as f:
            self.offer_decision_prompt_template = f.read().strip()

    async def evaluate_jobs(self, seeker_profile: dict, job_list: list) -> dict:
        # 新しい構造に対応したスコアリング例
        best_job = job_list[0]
        best_score = 0
        for job in job_list:
            score = 0
            # 年収・働き方・カルチャーはhope_conditionsでOK
            if job.get("salary", 0) >= seeker_profile["hope_conditions"]["min_salary"]:
                score += 1
            if job.get("work_style") == seeker_profile["hope_conditions"]["work_style"]:
                score += 1
            if any(skill in job.get("tech_stack", []) for skill in seeker_profile.get("skills", [])):
                score += 1
            if any(kw in job.get("culture_keywords", []) for kw in seeker_profile["hope_conditions"].get("culture_keywords", [])):
                score += 1
            if score > best_score:
                best_score = score
                best_job = job
        # Qwen3で志望理由を生成（contextやvaluesも含めて渡す）
        prompt = self.reason_prompt_template.format(seeker_profile=seeker_profile, best_job=best_job)
        reason = await self.llm.generate_content_async(prompt)
        return {
            "seeker_id": seeker_profile["id"],
            "application_decision": {
                "job_id": best_job["id"],
                "reason": reason
            }
        }

    async def evaluate_offer(self, seeker_profile: dict, job_profile: dict, offer: dict, interview_log: dict) -> dict:
        # 最終判断プロンプト
        prompt = self.offer_decision_prompt_template.format(
            seeker_profile=seeker_profile,
            job_profile=job_profile,
            offer=offer,
            interview_log=interview_log
        )
        decision = await self.llm.generate_content_async(prompt)
        status = "accept" if "accept" in decision or "受諾" in decision else "reject"
        return {
            "final_decision": {"status": status, "reason": decision}
        }

    def generate_resume(self, seeker_profile: dict) -> str:
        with open("prompts/seeker_resume.txt", encoding="utf-8") as f:
            resume_prompt = f.read().strip()
        # contextやcurrent_job、skills、valuesなどを含めて文字列化
        resume_str = f"【氏名】{seeker_profile['name']}\n【年齢】{seeker_profile['age']}歳\n"
        resume_str += f"【現職】{seeker_profile['current_job']['company']} / {seeker_profile['current_job']['role']}（{seeker_profile['current_job']['period']}）\n{seeker_profile['current_job']['description']}\n"
        resume_str += "【職歴】\n"
        for wh in seeker_profile.get('work_history', []):
            resume_str += f"- {wh['company']} / {wh['role']}（{wh['period']}）: {wh['description']}\n"
        resume_str += f"【スキル】{', '.join(seeker_profile.get('skills', []))}\n"
        resume_str += f"【価値観】{', '.join(seeker_profile.get('values', []))}\n"
        resume_str += f"【タグ】{', '.join(seeker_profile.get('tags', []))}\n"
        resume_str += f"【自己紹介・人生ストーリー】\n{seeker_profile['context']}\n"
        resume_str += f"【希望条件】年収{seeker_profile['hope_conditions']['min_salary']}万円以上 / {seeker_profile['hope_conditions']['work_style']} / カルチャー: {', '.join(seeker_profile['hope_conditions'].get('culture_keywords', []))}\n"
        return resume_str

    async def request_offer_change(self, offer: dict) -> str:
        with open("prompts/offer_negotiation_seeker.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template.format(offer=offer)
        request = await self.llm.generate_content_async(prompt)
        return request.strip()

    async def propose_job(self, self_intro: str, job_list: list) -> str:
        with open("prompts/seekeragent_job_proposal.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template.format(self_intro=self_intro, job_list=job_list)
        proposal = await self.llm.generate_content_async(prompt)
        return proposal.strip()

    async def explain_job_detail(self, job_proposal: str, job_question: str) -> str:
        with open("prompts/seekeragent_job_detail.txt", encoding="utf-8") as f:
            prompt_template = f.read().strip()
        prompt = prompt_template.format(job_proposal=job_proposal, job_question=job_question)
        detail = await self.llm.generate_content_async(prompt)
        return detail.strip() 