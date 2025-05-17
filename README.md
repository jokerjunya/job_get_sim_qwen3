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

## ディレクトリ構成

- `agents/job_simulation/` : エージェント実装（SeekerAgent, EmployerAgent, SimulatedSeeker, SimulatedInterviewer）
- `prompts/`   : プロンプト管理用テキスト（例: `seeker_self_introduction.txt`, `interviewer_question_stage1.txt` など）
- `data/`      : シミュレーション用データ（`seekers.json`, `jobs.json`）
- `logs/`      : ログファイル（md/jsonl形式で自動生成）
- `scripts/`   : 補助スクリプト（例: `run_conversation.py`）
- `run_simulation.py` : メイン実行スクリプト
- `requirements.txt` : 依存パッケージ

---

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

## 主要ファイル例

### prompts/
- `seeker_self_introduction.txt` : 求職者の自己紹介プロンプト
- `interviewer_question_stage1.txt` : 一次面接用質問プロンプト
- `offer_negotiation_seeker.txt` : 求職者の交渉リクエスト生成用
- ...他にも各プロセスごとに細分化

### data/
- `seekers.json` : 求職者プロフィール例
- `jobs.json` : 求人データ（5件以上の多様な職種・条件）

### agents/job_simulation/
- `seeker_agent.py` : 求職者エージェント
- `employer_agent.py` : 企業エージェント
- `simulated_seeker.py` : シミュレート求職者
- `simulated_interviewer.py` : シミュレート面接官

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