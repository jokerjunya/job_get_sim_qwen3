# 転職プロセスAIシミュレーション（Qwen3 + Ollama）

## 🎯 プロジェクト概要

**AIエージェント同士だけで転職活動の全プロセスを自動再現するシミュレーションシステム**

このプロジェクトは、現実の転職活動で起こる複雑なやり取りを、複数のAIエージェントが役割分担して自動的に進行させます。人間の介入なしに、求人作成から内定承諾まで全てが自動で完結します。

### ✨ 何ができるのか

- 🤖 **完全自動進行**: 求職者AI、企業AI、面接官AIが自律的に転職プロセスを進行
- 🎲 **毎回違うドラマ**: ランダムに選ばれる求職者×求人の組み合わせで、毎回異なるストーリーが展開
- 📊 **リアルタイム可視化**: ブラウザで進行状況をライブ表示（自動更新）
- 📝 **詳細ログ出力**: 全ての会話・判断・評価をMarkdown/JSON/HTML形式で記録

### 🎭 登場するAI役職

| AI役職 | 役割 |
|--------|------|
| **求職者AI** | キャリアアドバイザーとして求人提案・推薦文作成・履歴書生成・志望動機作成 |
| **シミュレート求職者** | 実際の転職者の人格・感情を再現し、面接回答・オファー判断・迷いの表現 |
| **企業AI** | 人事担当者として求人作成・書類選考・オファー調整・交渉対応 |
| **シミュレートHR** | 企業の採用方針決定・面接評価への意見・人事視点での判断 |
| **面接官AI** | 一次・二次・最終面接で質問生成・回答評価を実施 |

### 🚀 簡単スタート

```bash
# 1. Ollamaインストール & Qwen3モデル準備
ollama run qwen3:30b  # または qwen3:8b (軽量版)

# 2. 依存関係インストール
pip install -r requirements.txt

# 3. シミュレーション実行
python run_simulation.py

# 4. ブラウザでリアルタイム表示
# logs/simulation_log_YYYYMMDD_HHMMSS.html を開く
```

### 📋 転職プロセスの流れ

1. **🎲 ランダム組み合わせ選択** → 求職者タイプ×求人パターンをAIが選択
2. **🏢 求人票作成** → 企業AIが詳細な求人票を自動生成  
3. **💼 求人提案** → 求職者AIが魅力的な推薦文を作成
4. **📄 書類選考** → 履歴書生成→企業AI・HR AIの二段階評価
5. **🎤 面接（3回）** → 一次・二次・最終面接で質問・回答・評価
6. **💰 オファー交渉** → 条件提示→交渉→最大3ラウンド
7. **✅ 最終判断** → 「問い×間×例」フレームワークで受諾/辞退決定

---

## 📊 実行例・出力イメージ

実行すると以下のような形でAI同士の転職ドラマが進行します：

```
🎲 今回の組み合わせ: 
求職者「中堅プロジェクトマネージャー（35歳・家族重視）」
求人「金融大手企業のITプロジェクトマネージャー」

🏢 企業AI: 「安定性と成長機会を両立できるポジションを用意しました」
💼 求職者AI: 「あなたの家族への想いが活かせる、腰を据えて働ける環境です」
🎤 面接官AI: 「プロジェクト管理で最も苦労した経験を教えてください」
💰 企業AI: 「年収650万円、リモートワーク週3日でいかがでしょうか」
✅ シミュレート求職者: 「家族との時間も確保できそう...よし、受諾します！」
```

---

## 🆕 最新機能・改善（2025/01版）

### 🎲 多様性機能の大幅強化（NEW!）
- **ランダム求職者選択**：毎回異なるタイプの求職者がシミュレーションに参加
- **多様な求職者パターン**：若手エンジニア、中堅PM、キャリアチェンジ志向、シニアアーキテクトなど6タイプ
- **インテリジェント求人マッチング**：求職者の特性（年齢、スキル、価値観）に基づく適切な求人選択
- **動的求人生成**：業界・企業タイプ別の現実的な求人パターンから具体的な求人票を自動生成
- **マッチングスコア算出**：年齢適合性、スキル重複度、価値観一致度を総合評価

### リアルタイムHTML可視化機能
- **自動更新HTMLログ**：シミュレーション進行をブラウザでリアルタイム可視化
- **プログレスバー表示**：各ステップの進行状況を視覚的に表示
- **ライブタイムスタンプ**：現在時刻の自動更新
- **アニメーション効果**：現在実行中のステップが光り、完了したステップが緑色に変化
- **自動スクロール**：新しいコンテンツが追加されると自動で画面下部へスクロール
- **シミュレーション情報表示**：選択された求職者と求人の組み合わせをリアルタイム表示

### ユーザーエクスペリエンス向上
- **リアルタイムプログレス表示**：LLM生成中に「🤖 エージェント名が回答を生成中...」のアニメーション表示
- **生成完了通知**：「✅完了」表示で生成完了を明確に通知  
- **AIエージェント名の可視化**：各エージェントが識別しやすい日本語名で表示
- **12秒の無言状態解消**：以前の無音待機から視覚的フィードバックへ大幅改善

---

## 主な特徴・進捗
- **🎲 多様性とリアリティの向上**：毎回異なる組み合わせで、よくいる求職者×よくある求人のパターンを再現
- **求人作成プロセスの自動化・多層化**：SimulatedHR（企業人事AI）が企業要望・求人要件を提示し、EmployerAgentがそれをもとにミッション・チーム・成長機会・独自の魅力・求める人物像などを含むリッチな求人票を自動生成。生成・やりとりはすべてログ化。
- **HR-Employer会話の追加**：求人作成過程をより透明化するため、HR担当者とEmployerAgentの会話シーンを追加。現実的な要件確認プロセスを再現。
- **書類選考プロセスの複層化**：書類選考をEmployerAgentとSimulatedHRの二段階評価システムに拡張し、より公平で多角的な評価を実現。
- **履歴書+AI推薦の一体型出力**：応募者の履歴書と客観的AI視点からの推薦コメントを統合し、より総合的な評価を提供。
- **オファー判断の深化**：「問い × 間 × 例」フレームワークを導入し、迷いスコアに基づく自然な意思決定プロセスを再現。
- **推しポイント・応募意思返答の高品質化**：推しポイントは「冒頭サマリー→箇条書き→原体験→キャッチーフレーズ」の4部構成。応募意思返答もカジュアル・短文・相棒感を徹底。
- **プロンプト・フロー管理の厳密化**：実際に使われているプロンプトのみを管理し、READMEで用途・呼び出しタイミングを明記。
- **全体フロー・ログの充実**：求人作成から意思決定・交渉・ログ出力まで、全プロセスをAIエージェント同士で自動進行・記録。
- **求人データ多様化**：`data/jobs.json`に多様な求人例を収録。
- **リアルタイムHTMLログ出力**：ブラウザで進行状況をリアルタイム可視化（2秒間隔自動更新）

---

## ディレクトリ構成（2025/01/18時点 最新）

- `agents/`
  - `job_simulation/` : 転職プロセスの主要エージェント実装
    - `data_manager.py` : **🆕** 求職者・求人データの管理とランダム選択・マッチング機能
    - `seeker_agent.py` : 求職者AI（意思決定・履歴書生成・志望理由など）
    - `employer_agent.py` : 企業AI（求人生成・書類選考・オファー調整など）
    - `simulated_seeker.py` : シミュレート求職者（会話・感情・応募意思など）
    - `simulated_hr.py` : シミュレート人事（企業要望・求人要件提示）
    - `simulated_interviewer.py` : シミュレート面接官（質問生成・評価）
  - `conversation_roles/` : 会話エージェントA/B（ロールプレイ・対話実験用）
  - `base_agent.py` : エージェント共通基盤
  - `qwen3_llm.py` : Qwen3 LLMラッパー（リアルタイムプログレス表示対応）
  - `qwen3_setup.py` : LLMセットアップ補助
- `prompts/`   : 全プロンプト管理（用途・呼び出しタイミングは下記表参照）
- `data/`      : シミュレーション用データ
  - `seekers.json` : 求職者プロフィール例（山田太郎）
  - `seekers_patterns.json` : **🆕** 多様な求職者パターン（6タイプ）
  - `jobs.json` : 求人データ（多様な職種・条件）
  - `job_patterns.json` : **🆕** 求人パターンテンプレート（6業界・職種）
- `logs/`      : シミュレーションごとの出力ログ（md/jsonl/html形式で自動生成）
- `examples/`
  - `logs/` : サンプルシミュレーションログ（動作例として参照可能）
- `scripts/`   : 補助スクリプト
  - `run_conversation.py` : 会話ラリーや個別テスト用
- `run_simulation.py` : メイン実行スクリプト（転職プロセス全体を自動進行・リアルタイム可視化）
- `test_diversity.py` : **🆕** 多様性機能のテストスクリプト
- `test_qwen3_adk.py`, `test_qwen3_agent.py` : テスト・動作検証用スクリプト
- `requirements.txt` : 依存パッケージ
- `.gitignore` : Git管理除外設定

---

## 全体フロー（概要）

1. **🎲 DataManagerによるランダム選択**：毎回異なる求職者と求人パターンを選択
2. **📊 マッチングスコア算出**：求職者特性と求人要件の適合度を評価
3. **🏢 動的求人生成**：選択されたパターンから具体的な求人票を生成
4. **SimulatedHR（企業人事AI）が企業要望・求人要件を提示**
5. **HR担当者とEmployerAgentが会話形式で要件を確認**
6. **EmployerAgentが要件をもとにリッチな求人票を自動生成**
7. **SeekerAgent/SimulatedSeekerが求人提案・推しポイント生成・応募意思返答**
8. **書類選考・履歴書生成・empai/simhrによる二段階合否判定**
9. **面接（一次・二次・最終）質問・回答・評価**
10. **オファー提示・交渉（最大3ラウンド）・「問い × 間 × 例」による受諾判断**
11. **全ステップの出力・会話・合否・交渉内容をログ化**
12. **🆕 HTML形式でのリアルタイム可視化・プログレス表示**

---

## 🎲 多様性機能の詳細

### 求職者パターン（6タイプ）
1. **若手フロントエンドエンジニア（25歳）**：成長志向、トレンド敏感、年収重視
2. **中堅プロジェクトマネージャー（35歳）**：家族重視、安定志向、将来不安
3. **営業からITへのキャリアチェンジ（28歳）**：挑戦志向、学習意欲、多様性重視
4. **シニアアーキテクト（42歳）**：技術重視、責任志向、国際経験
5. **データアナリスト（30歳）**：事業理解、スキルアップ、バランス重視

### 求人パターン（6業界）
1. **EdTechスタートアップ**：フロントエンドエンジニア、急成長、社会貢献
2. **金融大手企業**：ITプロジェクトマネージャー、安定性、DX推進
3. **戦略コンサル**：データアナリスト、成果主義、グローバル
4. **SaaSベンチャー**：フルスタックエンジニア、技術重視、スピード感
5. **大手IT企業**：ソリューションアーキテクト、技術追求、大規模システム
6. **EC企業**：マーケティングエンジニア、未経験歓迎、学習支援

### マッチングアルゴリズム
- **年齢適合性**：ポジションレベルとの整合性を評価
- **スキルマッチング**：保有スキルと求められるスキルの重複度
- **価値観適合性**：個人の価値観と企業カルチャーの一致度
- **キャリアチェンジ考慮**：未経験歓迎求人への特別配点

### 動的求人生成
- **業界別会社名生成**：EdTech → 「エデュ株式会社」、金融 → 「フィン株式会社」など
- **年収レンジからの抽出**：「400-550万円」→ 実際の金額をランダム決定
- **面接官情報の自動付与**：既存データからの流用またはデフォルト設定

---

## プロンプトファイル一覧・用途・呼び出しタイミング

本プロジェクトで使用されているプロンプトファイルと、その用途・呼び出しタイミング・呼び出し元をまとめます。

| ファイル名 | 用途・内容 | 呼び出しタイミング・フェーズ | 呼び出し元クラス/メソッド |
|---|---|---|---|
| **hr_employer_conversation.txt** | HR担当者とEmployerAgentの求人要件に関する自然会話を生成。 | 求人要件確認フェーズ | run_simulation.py |
| **employer_resume_screening.txt** | 企業側（empai）による履歴書の評価・合否判定を生成。 | 書類選考フェーズ | EmployerAgent.screen_resume_llm |
| **hr_resume_screening_opinion.txt** | 人事側（simhr）による書類選考結果への意見を生成。 | 書類選考フェーズ | SimulatedHR.opine_on_resume_screening |
| **seeker_offer_conversation.txt** | 「問い × 間 × 例」フレームワークによるオファー判断の対話形式決定過程。 | オファー受諾判断フェーズ | SimulatedSeeker.decide_offer |
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

## セットアップ手順（詳細）

### 1. リポジトリのクローンとディレクトリ移動

```sh
git clone https://github.com/yourusername/ADK_qwen3.git
cd ADK_qwen3
```

### 2. Python仮想環境の作成・有効化

#### Mac/Linux
```sh
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows
```sh
python -m venv .venv
.venv\Scripts\activate
```
> 仮想環境を使うことで、他のプロジェクトと依存関係が混ざらず安全です。

---

### 3. 依存パッケージのインストール

```sh
pip install -r requirements.txt
```
- 主な依存パッケージ
  - `google-adk`：Google ADKエージェント基盤
  - `litellm`：Ollama等のLLM APIラッパー
  - `requests`：API通信
  - `tqdm`：プログレスバー表示
- インストール時にエラーが出る場合は、`pip`のバージョンを最新化してください。

---

### 4. Ollamaのインストール・確認

#### インストール済みの場合
```sh
ollama --version
ollama list
```
- バージョンが表示され、モデル一覧が確認できればOK

#### 新規インストール

##### Mac
1. [Ollama公式サイト](https://ollama.com/)から「Download for macOS」をクリックし、ダウンロードした`.dmg`を開いて`Ollama`アプリを`Applications`にドラッグ。
2. 初回起動時に権限付与が必要な場合は指示に従う。

##### Linux
```sh
curl -fsSL https://ollama.com/install.sh | sh
```
- インストール後、`ollama --version`でバージョンが表示されればOK。

##### Windows（プレビュー）
1. [Ollama公式サイト](https://ollama.com/)から「Download for Windows (Preview)」をクリックし、インストーラー（.exe）を実行。
2. WSL2（Windows Subsystem for Linux）が必要。インストーラーの指示に従いセットアップ。

---

### 5. Qwen3モデルの準備

#### 推奨モデル（性能重視）
```sh
ollama run qwen3:30b
```
- 約18GB、32GB以上RAM推奨
- 高品質な応答が期待できます

#### 軽量モデル（メモリ制約がある場合）
```sh
ollama run qwen3:8b
```
- 約5GB、16GB RAM推奨

#### 超軽量モデル（低スペックPC用）
```sh
ollama run qwen3:4b
```
- 約2.5GB、8GB RAM推奨

> 初回実行時に自動でモデルがダウンロードされます。ダウンロード時間はネットワーク速度に依存します。

---

### 6. APIサーバー起動確認

- Ollamaは`ollama run ...`でモデルを起動すると自動でAPIサーバー（`http://localhost:11434`）が立ち上がります。
- 別ターミナルで接続確認：
```sh
curl http://localhost:11434
```
- `Ollama is running`というレスポンスが返ればOK。

---

### 7. シミュレーションの実行

```sh
python run_simulation.py
```

#### 出力ファイル
- **Markdownログ**：`logs/simulation_log_YYYYMMDD_HHMMSS.md`
- **JSONLログ**：`logs/simulation_log_YYYYMMDD_HHMMSS.jsonl` 
- **🆕 HTMLログ**：`logs/simulation_log_YYYYMMDD_HHMMSS.html`（ブラウザで開くとリアルタイム表示）

#### 進行状況の確認方法
1. **ターミナル**：リアルタイムプログレス表示とログ出力
2. **🆕 ブラウザ**：生成されたHTMLファイルをブラウザで開くと自動更新される可視化画面

---

### 8. よくあるトラブル・FAQ

#### RAM不足でモデルが起動しない
- より小さいモデル（`qwen3:4b`や`qwen3:8b`）を使用
- 他のアプリを終了してメモリを解放
- 仮想メモリの設定を確認

#### Ollamaコマンドが見つからない
- ターミナルやPCを再起動
- パス設定を確認（特にWindows）
- 公式ドキュメントのトラブルシューティング参照

#### APIエラーや接続不可
- `ollama run qwen3:30b`でモデルを起動し直し
- `http://localhost:11434`にアクセスして動作確認
- ファイアウォール設定を確認

#### 🆕 進行が遅い・反応しない
- GPUメモリ不足の可能性：より小さいモデルを試す
- プログレス表示で現在の処理状況を確認
- ブラウザのHTMLログで詳細な進行状況を確認

---

### 9. 🆕 HTMLリアルタイム表示の使い方

1. シミュレーション開始後、`logs/`フォルダに生成されたHTMLファイルをブラウザで開く
2. **自動更新**：2秒間隔で自動的にページが更新され、最新の進行状況を表示
3. **ステップ表示**：
   - グレー：未実行
   - 青色で光る：実行中  
   - 緑色：完了
4. **プログレスバー**：LLM生成中はアニメーション付きプログレスバーを表示
5. **自動スクロール**：新しいコンテンツが追加されると自動でスクロール

---

## 実行方法

### 基本実行
```sh
python run_simulation.py
```

### テスト実行（動作確認用）
```sh
python test_qwen3_agent.py
```

### 会話のみのテスト
```sh
python scripts/run_conversation.py
```

---

## 出力・ログファイル

### ログファイル形式
- **Markdown（.md）**：人間が読みやすい形式
- **JSONL（.jsonl）**：機械処理用の構造化データ
- **🆕 HTML（.html）**：ブラウザでのリアルタイム可視化用

### ログ保存場所
- **メインログ**：`logs/simulation_log_YYYYMMDD_HHMMSS.*`
- **サンプルログ**：`examples/logs/`（参考用として保持）

---

## 🆕 主な改善点・技術的な特徴

### ユーザーエクスペリエンス
- **無音時間の解消**：以前の12秒無言状態→リアルタイムプログレス表示
- **視覚的フィードバック**：ターミナル + HTML両方での進行状況表示
- **エージェント可視化**：各AIエージェントの名称と役割を明確化

### 技術的改善
- **ストリーミング対応**：Ollama APIからのストリーミングレスポンス対応
- **非同期処理**：プログレス表示とLLM生成の並行処理
- **HTMLテンプレート**：CSS3アニメーション、レスポンシブデザイン対応
- **エラーハンドリング**：接続エラー、生成エラーの適切な処理

---

## 依存パッケージ
- google-adk
- litellm  
- requests
- tqdm（プログレスバー表示用）

---

## 注意事項
- `/logs/`ディレクトリは`.gitignore`で除外されています（各自のシミュレーション結果はローカルに保存）
- サンプルシミュレーション結果は`examples/logs/`で参照可能です
- `data/`内に個人情報や公開できないデータが含まれていないかご注意ください
- モデルサイズ・PCスペックにご注意ください（Qwen3:30Bは高スペック推奨）
- 🆕 HTMLファイルは自動更新されるため、ブラウザで開いたままにしておくとリアルタイム表示できます

---

## 今後の課題・拡張

### 短期的改善
- **プログレス表示の詳細化**：各ステップの進行率表示
- **エラー回復機能**：APIエラー時の自動リトライ機能
- **設定ファイル化**：モデル名、更新間隔等の設定外部化

### 中長期的拡張
- **入社後フォローの追加**：オファー受諾後の入社準備、オンボーディング、配属先とのマッチングなど、入社後の適応プロセスをシミュレーション
- **ユーザー（人間）介入ポイントの追加**：シミュレーション中に特定のポイントで人間が介入できるインタラクティブモードの実装
- **より複雑な交渉シナリオ**：多段階の条件交渉、複数オファー比較、カウンターオファーなど、より現実的な交渉フローの実装
- **面接官の多様化**：部門長、同僚、CEO、技術面接官など、異なる視点からの面接評価の追加
- **WebUI化**：ブラウザ完結型のインターフェース実装

---

## ライセンス

本プロジェクトはMITライセンスで提供されています。 