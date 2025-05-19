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
    # logのリスト（後で面接評価を取得するために使用）
    logs = []
    def log_json(step, content):
        logs.append({"step": step, "content": content})
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps({"step": step, "content": content}, ensure_ascii=False) + '\n')
    def log_md(step, content):
        with open(log_md_path, 'a', encoding='utf-8') as f:
            f.write(f'### {step}\n')
            if isinstance(content, dict):
                for k, v in content.items():
                    f.write(f'- **{k}**: {json.dumps(v, ensure_ascii=False, indent=2) if isinstance(v, (dict, list)) else v}\n')
            else:
                # まず会話パートの発言ごとに分割する正規化処理
                conversation_speakers = ["seeker:", "seekerAI:", "HR:", "EmployerAgent:"]
                # 1行に複数発言が含まれている場合も分割
                def split_conversation(text):
                    import re
                    # 先頭以外の発言ラベルの前に改行を挿入
                    pattern = r'(?<!^)(' + '|'.join(re.escape(s) for s in conversation_speakers) + r')'
                    return re.sub(pattern, r'\n\1', text)
                normalized_content = split_conversation(str(content))
                lines = normalized_content.split('\n')
                
                # 会話パートかどうか判定
                is_conversation = any(
                    l.strip().startswith(tuple(conversation_speakers))
                    for l in lines if l.strip()
                )
                # 構造化テキストかどうか判定（面接回答、評価など）
                is_structured = any(
                    l.strip().startswith(("**回答:", "**評価:", "**エピソード", "【", "回答:", "評価:", "理由:", "成果:", "コメント:"))
                    for l in lines if l.strip()
                )
                # 箇条書きリストかどうか判定
                is_list = all(
                    l.strip().startswith(('-', '・', '*', '1.', '2.', '3.')) or not l.strip()
                    for l in lines if l.strip()
                )
                # セクション構造を持つかどうか判定
                has_sections = any(
                    '【' in l and '】' in l
                    for l in lines if l.strip()
                )
                out = ''
                if is_conversation:
                    for para in lines:
                        if para.strip():
                            out += f'{para.strip()}  \n\n'
                elif is_structured:
                    for para in lines:
                        if para.strip():
                            if para.strip().startswith(('**', '【')) or ':' in para.strip():
                                out += f'{para.strip()}  \n\n'
                            else:
                                out += f'{para.strip()}  \n'
                elif has_sections:
                    for para in lines:
                        if para.strip():
                            if '【' in para and '】' in para:
                                out += f'{para.strip()}  \n\n'
                            else:
                                out += f'{para.strip()}  \n'
                elif is_list:
                    for para in lines:
                        if para.strip():
                            out += f'{para.strip()}\n'
                else:
                    for para in lines:
                        if para.strip():
                            out += f'{para.strip()}\n\n'
                out = re.sub(r'\n{3,}', '\n\n', out)
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

    # エージェント初期化（seeker_agentを先に）
    seeker_agent = SeekerAgent()
    simulated_hr = SimulatedHR(llm=seeker_agent.llm)
    employer_agent = EmployerAgent()

    hr_needs = simulated_hr.provide_needs()
    log_json("0.1. SimulatedHRの求人要望", hr_needs)
    log_md("0.1. SimulatedHRの求人要望", hr_needs)

    # HRとEmployerAgentの会話を生成
    with open("prompts/hr_employer_conversation.txt", encoding="utf-8") as f:
        hr_emp_conv_prompt = f.read().strip()
    hr_emp_conv_prompt_filled = hr_emp_conv_prompt.format(hr_needs=json.dumps(hr_needs, ensure_ascii=False, indent=2))
    # LLMで会話生成（seeker_agentを流用）
    hr_emp_conversation = await seeker_agent.llm.generate_content_async(hr_emp_conv_prompt_filled)
    log_json("0.1.5. HRとEmployerAgentの会話", hr_emp_conversation)
    log_md("0.1.5. HRとEmployerAgentの会話", hr_emp_conversation)

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
        application_reason = await simulated_seeker.application_reason(seeker_profile, job_list[0])
        print("\n【応募理由・AI推薦付き履歴書】")
        print(application_reason)
        log_json(step, application_reason)
        log_md(step, application_reason)

        if any(kw in job_intent for kw in ["見送", "応募しない", "辞退", "やめる", "考えたい"]):
            print("応募辞退のためシミュレーションを終了します。")
            return
                
        # --- 書類選考プロセス（新フロー） ---
        step = step_title("履歴書提出")
        resume = seeker_agent.generate_resume(seeker_profile)
        print("\n【履歴書・職務経歴書】")
        print(resume)
        log_json(step, resume)
        log_md(step, resume)

        step = step_title("empaiによる書類審査")
        empai_judgement = await employer_agent.screen_resume_llm(resume)
        print("\n【empaiの書類審査】")
        print(empai_judgement["raw"])
        log_json(step, empai_judgement)
        log_md(step, empai_judgement["raw"])

        step = step_title("simhrの意見")
        simhr_opinion = await simulated_hr.opine_on_resume_screening(empai_judgement)
        print("\n【simhrの意見】")
        print(simhr_opinion["raw"])
        log_json(step, simhr_opinion)
        log_md(step, simhr_opinion["raw"])

        # --- 最終合否決定 ---
        step = step_title("書類選考・最終判定")
        # シンプルなロジック例：empaiが合格でsimhrが賛成→合格、それ以外は不合格
        if empai_judgement["decision"] == "合格" and simhr_opinion["opinion"] == "賛成":
            final_result = "合格"
            final_reason = f"empai・simhrともに合格判断。理由: {empai_judgement['reason']} / {simhr_opinion['comment']}"
        else:
            final_result = "不合格"
            final_reason = f"empaiまたはsimhrが不合格・反対判断。理由: {empai_judgement['reason']} / {simhr_opinion['comment']}"
        print(f"\n【書類選考・最終判定】{final_result}\n{final_reason}")
        log_json(step, {"result": final_result, "reason": final_reason})
        log_md(step, f"合否: {final_result}\n理由: {final_reason}")
        # 不合格の場合は終了
        if final_result == "不合格":
            print("書類選考で不合格のため、シミュレーションを終了します。")
            return
        
        # 合格の場合は面接プロセスに進む
        print("書類選考に合格しました。面接プロセスに進みます。")

        # --- 面接プロセス多段階化 ---
        interview_stages = ["一次面接", "二次面接", "最終面接"]
        for stage in interview_stages:
            print(f"\n【{stage}】")
            question = await interviewer.generate_question(job_list[0], stage=stage, seeker_profile=seeker_profile, resume=resume)
            print("【面接質問】")
            print(question)
            log_json(step_title(f"{stage} 質問"), question)
            log_md(step_title(f"{stage} 質問"), question)

            answer = await simulated_seeker.answer_interview(question, seeker_profile=seeker_profile)
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
        # 面接評価リストを作成
        interview_evaluations = []
        for stage in interview_stages:
            for item in logs:
                if item.get("step", "").endswith(f"{stage} 評価"):
                    interview_evaluations.append(item["content"])
        
        # 面接評価と求職者プロフィールに基づく動的オファー生成
        offer = await employer_agent.generate_initial_offer(
            seeker_profile=seeker_profile,
            job=job_list[0],
            interview_evaluations=interview_evaluations
        )
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

        # --- 受諾判断（対話形式） ---
        step = step_title("オファー受諾判断プロセス")
        offer_decision_result = await simulated_seeker.decide_offer(
            offer=offer,
            seeker_profile=seeker_profile,
            job=job_list[0],
            interview_evaluations=interview_evaluations
        )
        
        # 会話と決断を表示
        print("\n【オファー受諾判断の会話】")
        print(offer_decision_result["conversation"])
        log_json(step, offer_decision_result)
        log_md(step, offer_decision_result["conversation"])
        
        # 最終決断のみ分けて表示
        final_decision = "受諾" if offer_decision_result["decision"] else "辞退"
        print(f"\n【最終決断】{final_decision}")
        log_json(step_title("最終決断"), final_decision)
        log_md(step_title("最終決断"), final_decision)
    else:
        print("求人の話を聞きたい意思が示されなかったため、シミュレーションを終了します。")
        return
        
    # シミュレーション完了後、examples/logsにサンプルログをコピー
    print("\n【シミュレーション完了】")
    print(f"ログは logs/simulation_log_{now_str}.md と logs/simulation_log_{now_str}.jsonl に保存されました")
    
    # examples/logsディレクトリの作成とログファイルのコピー
    try:
        # examples/logsディレクトリが存在しない場合は作成
        os.makedirs('examples/logs', exist_ok=True)
        
        # 最新ログをコピー
        import shutil
        shutil.copy(log_md_path, 'examples/logs/latest_simulation.md')
        shutil.copy(log_path, 'examples/logs/latest_simulation.jsonl')
        
        print("\n【サンプルログを更新】")
        print("examples/logs/latest_simulation.md と examples/logs/latest_simulation.jsonl を更新しました")
        print("※このサンプルログはGitHubリポジトリに含まれます。個人情報が含まれていないか確認してください。")
    except Exception as e:
        print(f"\n【サンプルログ更新エラー】: {e}")
        print("examples/logsへのコピーに失敗しました。")

if __name__ == "__main__":
    asyncio.run(main()) 