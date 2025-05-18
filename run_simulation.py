import asyncio
import json
import os
import datetime
import re
from agents.job_simulation.seeker_agent import SeekerAgent
from agents.job_simulation.employer_agent import EmployerAgent
from agents.job_simulation.simulated_seeker import SimulatedSeeker
from agents.job_simulation.simulated_interviewer import SimulatedInterviewer
from agents.job_simulation.simulated_hr import SimulatedHR

async def main():
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
                lines = str(content).split('\n')
                # 会話パートかどうか判定
                is_conversation = all(
                    l.strip().startswith(("seeker:", "seekerAI:")) or not l.strip()
                    for l in lines if l.strip()
                )
                # 箇条書きリストかどうか判定
                is_list = all(
                    l.strip().startswith('-') or not l.strip()
                    for l in lines if l.strip()
                )
                out = ''
                if is_conversation or is_list:
                    for para in lines:
                        if para.strip():
                            out += f'{para.strip()}\n'
                else:
                    for para in lines:
                        if para.strip():
                            out += f'{para.strip()}\n\n'
                # 連続する空行を1つに正規化
                out = re.sub(r'\n{2,}', '\n', out)
                f.write(out)
            f.write('\n')
    def step_title(title):
        nonlocal step_counter
        s = f"{step_counter}. {title}"
        step_counter += 1
        return s

    def format_job_posting_md(job):
        # 基本情報
        s = '**【基本情報】**\n'
        s += f'- ポジション: {job.get("position", "")}' + '\n'
        s += f'- 会社: {job.get("company", "")}' + '\n'
        s += f'- 背景: {job.get("background", "")}' + '\n'
        s += f'- 年収: {job.get("salary", "")}万円〜' + '\n'
        s += f'- 働き方: {job.get("work_style", "")}' + '\n'
        # スキル・条件
        s += '\n**【スキル・条件】**\n'
        if job.get("tech_stack"):
            s += '- 技術スタック:\n'
            for skill in job["tech_stack"]:
                s += f'    - {skill}\n'
        # カルチャー
        if job.get("culture_keywords"):
            s += '- カルチャーキーワード:\n'
            for kw in job["culture_keywords"]:
                s += f'    - {kw}\n'
        # 特徴・ミッション
        s += '\n**【特徴・ミッション】**\n'
        if job.get("mission"):
            s += f'- ミッション: {job["mission"]}\n'
        if job.get("team"):
            s += f'- チーム: {job["team"]}\n'
        if job.get("growth"):
            s += f'- 成長機会: {job["growth"]}\n'
        if job.get("unique"):
            s += f'- 独自の魅力: {job["unique"]}\n'
        if job.get("persona"):
            s += f'- 求める人物像: {job["persona"]}\n'
        return s

    # --- 新規：求人作成フェーズ ---
    simulated_hr = SimulatedHR()
    employer_agent = EmployerAgent()
    hr_needs = simulated_hr.provide_needs()
    log_json("0.1. SimulatedHRの求人要望", hr_needs)
    log_md("0.1. SimulatedHRの求人要望", hr_needs)
    job_posting = employer_agent.create_job_posting(simulated_hr)
    log_json("0.2. EmployerAgentが生成した求人票", job_posting)
    log_md("0.2. EmployerAgentが生成した求人票", format_job_posting_md(job_posting))
    print("\n【SimulatedHRとEmployerAgentによる新規求人作成】")
    print(job_posting)

    # データ読み込み
    with open('data/seekers.json', encoding='utf-8') as f:
        seekers = json.load(f)
    with open('data/jobs.json', encoding='utf-8') as f:
        jobs = json.load(f)

    seeker_profile = seekers[0]
    # job_listを新規求人のみとする
    job_list = [job_posting]

    # エージェント初期化
    seeker_agent = SeekerAgent()
    simulated_seeker = SimulatedSeeker()
    interviewer = SimulatedInterviewer()

    # --- seekerとseekerAIの会話をまとめて生成・表示 ---
    conversation_example = await simulated_seeker.start_conversation(seeker_profile)
    print("\n【転職相談の会話】")
    print(conversation_example)
    log_json("1. 転職相談の会話", conversation_example)
    log_md("1. 転職相談の会話", conversation_example)

    # seekerが求人の話を聞きたい意思を示したら求人提案フローへ
    lines = [l.strip() for l in conversation_example.strip().split('\n') if l.strip()]
    seeker_lines = [l for l in lines if l.startswith("seeker:")]
    last_seeker_line = seeker_lines[-1] if seeker_lines else ""

    # 「求人の話を聞きたい」意思を示すキーワード
    hear_keywords = [
        "ぜひ聞かせて", "興味ある", "聞いてみたい", "その話、詳しく", "話を聞きたい", "求人の詳細", "どんな求人", "教えて", "説明して", "知りたい", "求人について", "求人を教えて", "求人の話を聞きたい", "求人の詳細を知りたい", "詳しく聞かせて"
    ]
    if any(kw in last_seeker_line for kw in hear_keywords):
        # 求人提案フロー
        step = step_title("求人概要提示")
        job = job_list[0]  # 1件のみ前提
        job_summary = await seeker_agent.propose_job_summary(job)
        print("\n【キャリアアドバイザーの求人概要】")
        print(job_summary)
        log_json(step, job_summary)
        log_md(step, job_summary)

        step = step_title("求人推しプレゼン")
        job_pitch = await seeker_agent.propose_job_pitch(seeker_profile, job)
        print("\n【キャリアアドバイザーの推しポイント】")
        print(job_pitch)
        log_json(step, job_pitch)
        log_md(step, job_pitch)

        # --- 応募意思確認 ---
        step = step_title("応募意思確認")
        job_intent = await simulated_seeker.job_intent(job_pitch)
        print("\n【求職者の応募意思】")
        print(job_intent)
        log_json(step, job_intent)
        log_md(step, job_intent)

        # --- 応募理由（履歴書＋AI推薦コメント一体型）生成 ---
        step = step_title("応募理由・AI推薦付き履歴書")
        application_reason = await simulated_seeker.application_reason(seeker_profile, job)
        print("\n【応募理由・AI推薦付き履歴書】")
        print(application_reason)
        log_json(step, application_reason)
        log_md(step, application_reason)

        if any(kw in job_intent for kw in ["見送", "応募しない", "辞退", "やめる", "考えたい"]):
            print("応募辞退のためシミュレーションを終了します。")
            return
        # 以降のフローは必要に応じて追加
        return

    # 以降のフローは必要に応じて分岐・省略
    return

    # 2. 求人提案（新フロー）
    step = step_title("求人概要提示")
    job = job_list[0]  # 1件のみ前提
    job_summary = await seeker_agent.propose_job_summary(job)
    print("\n【キャリアアドバイザーの求人概要】")
    print(job_summary)
    log_json(step, job_summary)
    log_md(step, job_summary)

    step = step_title("求人推しプレゼン")
    job_pitch = await seeker_agent.propose_job_pitch(seeker_profile, job)
    print("\n【キャリアアドバイザーの推しポイント】")
    print(job_pitch)
    log_json(step, job_pitch)
    log_md(step, job_pitch)

    step = step_title("応募意思確認")
    job_intent = await simulated_seeker.job_intent(job_pitch)
    print("\n【求職者の応募意思】")
    print(job_intent)
    log_json(step, job_intent)
    log_md(step, job_intent)

    step = step_title("応募理由生成")
    application_reason = await simulated_seeker.application_reason(job_intent)
    print("\n【応募判断理由】")
    print(application_reason)
    log_json(step, application_reason)
    log_md(step, application_reason)

    if any(kw in job_intent for kw in ["見送", "応募しない", "辞退", "やめる", "考えたい"]):
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