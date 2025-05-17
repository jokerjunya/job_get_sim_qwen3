import asyncio
import json
import os
import datetime
from agents.job_simulation.seeker_agent import SeekerAgent
from agents.job_simulation.employer_agent import EmployerAgent
from agents.job_simulation.simulated_seeker import SimulatedSeeker
from agents.job_simulation.simulated_interviewer import SimulatedInterviewer

async def main():
    # データ読み込み
    with open('data/seekers.json', encoding='utf-8') as f:
        seekers = json.load(f)
    with open('data/jobs.json', encoding='utf-8') as f:
        jobs = json.load(f)

    seeker_profile = seekers[0]
    job_list = jobs

    # エージェント初期化
    seeker_agent = SeekerAgent()
    employer_agent = EmployerAgent()
    simulated_seeker = SimulatedSeeker()
    interviewer = SimulatedInterviewer()

    now_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs('logs', exist_ok=True)
    log_path = f'logs/simulation_log_{now_str}.jsonl'
    log_md_path = f'logs/simulation_log_{now_str}.md'
    step_counter = 1
    def log_json(step, content):
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"step": step, "content": content}, ensure_ascii=False) + '\n')
    def log_md(step, content):
        with open(log_md_path, 'a', encoding='utf-8') as f:
            f.write(f'### {step}\n')
            if isinstance(content, dict):
                for k, v in content.items():
                    f.write(f'- **{k}**: {json.dumps(v, ensure_ascii=False, indent=2) if isinstance(v, (dict, list)) else v}\n')
            else:
                # 長文は段落分け
                for para in str(content).split('\n'):
                    if para.strip():
                        f.write(f'{para.strip()}\n\n')
            f.write('\n')

    # ステップごとにstep_counterを使って番号付与
    def step_title(title):
        nonlocal step_counter
        s = f"{step_counter}. {title}"
        step_counter += 1
        return s

    # --- 求人検索・情報収集ステップ ---
    # 1. 自己紹介
    step = step_title("自己紹介")
    self_intro = await simulated_seeker.self_introduction()
    print("\n【求職者の自己紹介】")
    print(self_intro)
    log_json(step, self_intro)
    log_md(step, self_intro)

    # 2. 求人提案
    step = step_title("求人提案")
    job_proposal = await seeker_agent.propose_job(self_intro, job_list)
    print("\n【キャリアアドバイザーの求人提案】")
    print(job_proposal)
    log_json(step, job_proposal)
    log_md(step, job_proposal)

    # 3. 求職者の質問
    step = step_title("求人に関する質問")
    job_question = await simulated_seeker.job_question(job_proposal)
    print("\n【求職者の質問】")
    print(job_question)
    log_json(step, job_question)
    log_md(step, job_question)

    # 4. 求人詳細説明
    step = step_title("求人詳細説明")
    job_detail = await seeker_agent.explain_job_detail(job_proposal, job_question)
    print("\n【キャリアアドバイザーの詳細説明】")
    print(job_detail)
    log_json(step, job_detail)
    log_md(step, job_detail)

    # 5. 最終応募判断
    step = step_title("最終応募判断")
    final_decision = await simulated_seeker.job_final_decision(job_proposal)
    print("\n【求職者の最終応募判断】")
    print(final_decision)
    log_json(step, final_decision)
    log_md(step, final_decision)
    if "応募しません" in final_decision:
        print("応募辞退のためシミュレーションを終了します。")
        return

    # --- 書類選考プロセス ---
    step = step_title("履歴書提出")
    resume = seeker_agent.generate_resume(seeker_profile)
    print("\n【履歴書・職務経歴書】")
    print(resume)
    log_json(step, resume)
    log_md(step, resume)

    step = step_title("書類選考結果")
    result, feedback = employer_agent.screen_resume(resume)
    print("\n【書類選考結果】")
    print(feedback)
    log_json(step, feedback)
    log_md(step, feedback)
    if not result:
        print("書類選考不合格のため終了します。")
        return

    # 求職者が求人を評価
    step = step_title("応募判断")
    job_eval = await seeker_agent.evaluate_jobs(seeker_profile, job_list)
    print("\n【求職者の応募判断】")
    print(job_eval)
    log_json(step, job_eval)
    log_md(step, job_eval)

    # 志望動機生成
    motivation = await simulated_seeker.generate_motivation(job_list[0])
    print("\n【志望動機】")
    print(motivation)
    log_json(step_title("志望動機"), motivation)
    log_md(step_title("志望動機"), motivation)

    # 企業が応募者を評価
    employer_eval = await employer_agent.evaluate_applicant(seeker_profile, job_eval)
    print("\n【企業の応募者評価】")
    print(employer_eval)
    log_json(step_title("企業評価"), employer_eval)
    log_md(step_title("企業評価"), employer_eval)

    # --- 面接プロセス多段階化 ---
    interview_stages = ["一次面接", "二次面接", "最終面接"]
    for stage in interview_stages:
        print(f"\n【{stage}】")
        question = await interviewer.generate_question(job_list[0], stage=stage)
        print("【面接質問】")
        print(question)
        log_json(step_title(f"{stage} 質問"), question)
        log_md(step_title(f"{stage} 質問"), question)

        answer = await simulated_seeker.answer_interview(question)
        print("【面接回答】")
        print(answer)
        log_json(step_title(f"{stage} 回答"), answer)
        log_md(step_title(f"{stage} 回答"), answer)

        evaluation = await interviewer.evaluate_answer(answer)
        print("【面接官の評価】")
        print(evaluation)
        # 合否判定ロジック（例：評価コメントに"高い"や"合格"があれば合格、それ以外は不合格）
        if any(ng in evaluation for ng in ["不合格", "見送り", "reject"]):
            judge = "不合格"
        else:
            judge = "合格"
        print(f"【{stage}判定】{judge}")
        log_json(step_title(f"{stage} 判定"), judge)
        log_md(step_title(f"{stage} 判定"), judge)
        log_json(step_title(f"{stage} 評価"), evaluation)
        log_md(step_title(f"{stage} 評価"), evaluation)
        if judge == "不合格":
            print(f"{stage}で不合格のため終了します。")
            return

    # --- オファー交渉ステップ ---
    # 初回オファー（例：年収・入社日）
    offer = {"年収": 500, "入社日": "2024-07-01"}
    print("\n【初回オファー提示】")
    print(offer)
    log_json(step_title("初回オファー提示"), offer)
    log_md(step_title("初回オファー提示"), offer)

    max_rounds = 3
    for round_num in range(1, max_rounds + 1):
        print(f"\n【オファー交渉ラウンド{round_num}】")
        request = await seeker_agent.request_offer_change(offer)
        print("求職者リクエスト:", request)
        log_json(step_title(f"交渉ラウンド{round_num} 求職者リクエスト"), request)
        log_md(step_title(f"交渉ラウンド{round_num} 求職者リクエスト"), request)
        if request == "特にありません":
            print("合意に達しました。")
            log_json(step_title(f"交渉ラウンド{round_num} 合意"), offer)
            log_md(step_title(f"交渉ラウンド{round_num} 合意"), offer)
            break
        offer = await employer_agent.update_offer(offer, request)
        print("企業再提示:", offer)
        log_json(step_title(f"交渉ラウンド{round_num} 企業再提示"), offer)
        log_md(step_title(f"交渉ラウンド{round_num} 企業再提示"), offer)
        if round_num == max_rounds:
            print("最大ラウンドに達したため、現状オファーで最終判断します。")
            log_json(step_title(f"交渉ラウンド{round_num} 打ち切り"), offer)
            log_md(step_title(f"交渉ラウンド{round_num} 打ち切り"), offer)

    # --- 受諾判断 ---
    offer_decision = await simulated_seeker.decide_offer(offer)
    print("\n【オファー受諾判断】")
    print("受諾" if offer_decision else "辞退")
    log_json(step_title("オファー受諾判断"), "受諾" if offer_decision else "辞退")
    log_md(step_title("オファー受諾判断"), "受諾" if offer_decision else "辞退")

if __name__ == "__main__":
    asyncio.run(main()) 