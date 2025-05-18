# 転職プロセスAIシミュレーション（Qwen3 + Ollama）

このプロジェクトは「AIエージェント同士のみで転職プロセスを再現し、クオリティを高める」ことを目的としています。求人検索・書類選考・面接・条件交渉・意思決定まで、現実的な転職活動の流れを段階的に自動化・高品質化します。

---

## 主な特徴・進捗
- **求人検索・情報収集**：自己紹介→求人提案→質問→詳細説明→応募判断の流れを再現
- **書類選考**：履歴書生成・合否判定をAIで自動化
- **面接プロセス多段階化**：一次・二次・最終面接で質問・回答・評価・合否判定を記録
- **条件交渉・オファー調整**：最大3ラウンドまで年収等の交渉・合意内容もログ化
- **プロンプト一元管理**：`prompts/`配下で全プロンプトを管理
- **ログ出力**：各ステップの出力・合否・交渉内容を`logs/`にmd/jsonlで記録
- **求人データ多様化**：`data/jobs.json`に5件以上の求人例

---

## ディレクトリ構成（2024/05時点 最新）

- `agents/`
  - `job_simulation/` : 転職プロセスの主要エージェント実装
    - `seeker_agent.py` : 求職者AI（意思決定・履歴書生成・志望理由など）
    - `employer_agent.py` : 企業AI（求人生成・書類選考・オファー調整など）
    - `simulated_seeker.py` : シミュレート求職者（会話・感情・応募意思など）
    - `simulated_hr.py` : シミュレート人事（企業要望・求人要件提示）
    - `simulated_interviewer.py` : シミュレート面接官（質問生成・評価）
  - `conversation_roles/` : 会話エージェントA/B（ロールプレイ・対話実験用）
  - `base_agent.py` : エージェント共通基盤
  - `qwen3_llm.py` : Qwen3 LLMラッパー
  - `qwen3_setup.py` : LLMセットアップ補助
- `prompts/`   : 全プロンプト管理（用途・呼び出しタイミングは下記表参照）
- `data/`      : シミュレーション用データ
  - `seekers.json` : 求職者プロフィール例
  - `jobs.json` : 求人データ（多様な職種・条件）
- `logs/`      : シミュレーションごとの出力ログ（md/jsonl形式で自動生成）
- `scripts/`   : 補助スクリプト
  - `run_conversation.py` : 会話ラリーや個別テスト用
- `run_simulation.py` : メイン実行スクリプト（転職プロセス全体を自動進行）
- `test_qwen3_adk.py`, `test_qwen3_agent.py` : テスト・動作検証用スクリプト
- `requirements.txt` : 依存パッケージ
- `.gitignore` : Git管理除外設定

---

## 全体フロー（概要）

1. **SimulatedHR/EmployerAgentによる求人作成**
2. **SimulatedSeeker/SeekerAgentによる転職相談・求人提案・推しポイント生成**
3. **応募意思確認・志望理由生成**
4. **書類選考・履歴書生成・合否判定**
5. **面接（一次・二次・最終）質問・回答・評価**
6. **オファー交渉（最大3ラウンド）・受諾判断**
7. **全ステップの出力・会話・合否・交渉内容をログ化**

---

## 主要ファイル・役割（抜粋）

- `agents/job_simulation/seeker_agent.py` : 求職者AIの意思決定・履歴書・志望理由・求人評価など
- `agents/job_simulation/employer_agent.py` : 企業AIの求人生成・書類選考・オファー調整
- `agents/job_simulation/simulated_seeker.py` : シミュレート求職者の会話・感情・応募意思
- `agents/job_simulation/simulated_hr.py` : 企業人事の要望・求人要件提示
- `agents/job_simulation/simulated_interviewer.py` : 面接官の質問・評価
- `prompts/` : 全プロンプト（用途・呼び出しタイミングは下記表）
- `data/seekers.json` : 求職者プロフィール例
- `data/jobs.json` : 求人データ
- `logs/` : シミュレーションごとの詳細ログ
- `run_simulation.py` : 全体フローの自動進行・ログ出力
- `scripts/run_conversation.py` : 会話ラリーや個別テスト用

---

## プロンプトファイル一覧・用途・呼び出しタイミング

本プロジェクトで使用されているプロンプトファイルと、その用途・呼び出しタイミング・呼び出し元をまとめます。

| ファイル名 | 用途・内容 | 呼び出しタイミング・フェーズ | 呼び出し元クラス/メソッド |
|---|---|---|---|
| **seekeragent_job_pitch.txt** | キャリアアドバイザーAIが求職者に求人を"推す"推薦文を生成。冒頭サマリー・箇条書き・原体験・キャッチーフレーズで構成。 | 求人提案フェーズで「推しポイント」生成時 | SeekerAgent.propose_job_pitch |
| **seeker_job_intent.txt** | 求職者が推しポイントを受けて応募意思を返答。迷い・ワクワク・照れ・冗談など感情を交えた短文。 | 推しポイント提示後、応募意思確認時 | SimulatedSeeker.job_intent |
| **seeker_motivation.txt** | 求職者が求人に応募する志望動機を生成（200字以内）。 | 志望動機生成フェーズ | SimulatedSeeker.generate_motivation |
| **seeker_answer_interview.txt** | 面接質問に対する求職者の回答を生成。 | 面接プロセスで各質問に回答時 | SimulatedSeeker.answer_interview |
| **seeker_self_introduction.txt** | 求職者の自己紹介文を生成。 | シミュレーション開始時や履歴書作成時 | SimulatedSeeker.self_introduction |
| **seeker_job_question.txt** | 求人提案を受けた求職者が気になる点を質問。 | 求人提案後、詳細質問時 | SimulatedSeeker.job_question |
| **seeker_application_reason.txt** | 応募意思返答をもとに、なぜ応募する/しないか理由を生成。 | 応募意思確認後、理由生成時 | SimulatedSeeker.application_reason |
| **seeker_job_final_decision.txt** | 求職者が最終的に応募するかどうかを決定。 | 応募判断フェーズ | SimulatedSeeker.job_final_decision |
| **seeker_life_topic.txt** | seekerとseekerAIの転職相談会話例（5往復）を生成。 | シミュレーション冒頭、会話例生成時 | SimulatedSeeker.start_conversation |
| **seekeragent_job_proposal.txt** | キャリアアドバイザーAIが求職者の自己紹介をもとに求人を提案。 | 求人提案フェーズ | SeekerAgent.propose_job |
| **seekeragent_job_summary.txt** | 求人情報をもとに、求職者向けに分かりやすく求人概要を説明。 | 求人概要提示フェーズ | SeekerAgent.propose_job_summary |
| **seekeragent_job_detail.txt** | 求職者からの質問に対し、求人の詳細を説明。 | 求人詳細説明フェーズ | SeekerAgent.explain_job_detail |
| **seeker_reason.txt** | 求職者AIが求人を評価し、なぜ応募するのが良いか志望理由を生成。 | 求人評価・応募判断フェーズ | SeekerAgent.evaluate_jobs |
| **seeker_resume.txt** | seekerの履歴書・職務経歴書を自動生成。 | 書類選考フェーズ | SeekerAgent.generate_resume |
| **offer_negotiation_seeker.txt** | オファー内容に対する求職者のリクエストを生成。 | オファー交渉（求職者側） | SeekerAgent.request_offer_change |
| **offer_negotiation_employer.txt** | 求職者リクエストを受けた企業側のオファー再提示を生成。 | オファー交渉（企業側） | EmployerAgent.update_offer |
| **seeker_offer_decision.txt** | オファー内容・面接印象をもとに最終受諾判断を生成。 | オファー受諾判断フェーズ | SeekerAgent.evaluate_offer |
| **interviewer_question_stage1.txt** | 一次面接用の質問を生成。 | 一次面接フェーズ | SimulatedInterviewer.generate_question |
| **interviewer_question_stage2.txt** | 二次面接用の質問を生成。 | 二次面接フェーズ | SimulatedInterviewer.generate_question |
| **interviewer_question_stage3.txt** | 最終面接用の質問を生成。 | 最終面接フェーズ | SimulatedInterviewer.generate_question |
| **interviewer_question.txt** | その他面接用の質問を生成。 | 面接プロセス（汎用） | SimulatedInterviewer.generate_question |
| **interviewer_evaluate.txt** | 面接回答の評価コメントを生成。 | 各面接回答後 | SimulatedInterviewer.evaluate_answer |
| **role_a_system.txt** | 会話エージェントAのシステムプロンプト。 | 会話エージェントAの初期化時 | ConversationRoleAAgent |
| **role_b_system.txt** | 会話エージェントBのシステムプロンプト。 | 会話エージェントBの初期化時 | ConversationRoleBAgent |

> ※用途や呼び出しタイミングは、今後のフロー追加・変更時に随時更新してください。

## セットアップ手順

### 1. Python環境
- Python 3.8以降を推奨
- 仮想環境推奨（例: `python -m venv .venv` → `source .venv/bin/activate`）

### 2. 依存パッケージのインストール
```sh
pip install -r requirements.txt
```

### 3. Ollama + Qwen3のセットアップ
- [Ollama公式](https://ollama.com/)からOllamaをインストール
- Qwen3モデル（例: `qwen3:30b`）をダウンロード
```sh
ollama run qwen3:30b
```
- サーバーが`http://localhost:11434`で起動していればOK

---

## 実行方法

```sh
python run_simulation.py
```
- ログは`logs/simulation_log_YYYYMMDD_HHMMSS.md`/`.jsonl`として自動保存されます
- シミュレーションは自己紹介→求人提案→質問→詳細説明→応募判断→書類選考→面接（3段階）→条件交渉→受諾判断まで自動で進行します

---

## 依存パッケージ
- google-adk
- litellm
- requests

---

## 注意事項
- `.venv/`や`logs/`などは`.gitignore`で除外してください
- `data/`内に個人情報や公開できないデータが含まれていないかご注意ください
- モデルサイズ・PCスペックにご注意ください（Qwen3:30Bは高スペック推奨）

---

## 今後の課題・拡張
- プロンプトや判定ロジックのさらなる現実化・高品質化
- 求人データのさらなる多様化
- ユーザー（人間）介入ポイントや入社後フォローなどの拡張

---

## ライセンス
- 本リポジトリはMITライセンスです 