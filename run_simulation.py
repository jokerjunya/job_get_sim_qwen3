import asyncio
import json
import os
import datetime
import re
import shutil
from agents.job_simulation.seeker_agent import SeekerAgent
from agents.job_simulation.employer_agent import EmployerAgent
from agents.job_simulation.simulated_seeker import SimulatedSeeker
from agents.job_simulation.simulated_interviewer import SimulatedInterviewer
from agents.job_simulation.simulated_hr import SimulatedHR
from agents.job_simulation.data_manager import DataManager

async def main():
    now_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    os.makedirs('logs', exist_ok=True)
    log_path = f'logs/simulation_log_{now_str}.jsonl'
    log_md_path = f'logs/simulation_log_{now_str}.md'
    log_html_path = f'logs/simulation_log_{now_str}.html'
    step_counter = 1
    # logのリスト（後で面接評価を取得するために使用）
    logs = []
    html_content = []  # HTMLコンテンツを保存するリスト
    current_progress = ""  # 現在の進捗状況
    completed_steps = []  # 完了したステップリスト
    is_simulation_completed = False  # シミュレーション完了フラグ
    
    # DataManagerを初期化
    data_manager = DataManager()
    
    # データの統計情報を表示
    stats = data_manager.get_stats()
    print("📊 データ統計情報:")
    print(f"  求職者数: {stats['seekers_count']}")
    print(f"  求人パターン数: {stats['job_patterns_count']}")
    print(f"  静的求人数: {stats['static_jobs_count']}")
    print(f"  求職者タイプ: {', '.join(set(stats['seeker_types']))}")
    print(f"  求人タイプ: {', '.join(set(stats['job_types']))}")
    print("")
    
    # ランダムに求職者と求人を選択
    seeker_profile, generated_job = data_manager.get_simulation_pair()
    
    print("🎲 今回のシミュレーション組み合わせ:")
    print(f"  求職者: {seeker_profile['name']} ({seeker_profile.get('age', '?')}歳)")
    print(f"  現職: {seeker_profile.get('current_job', {}).get('company', '?')} - {seeker_profile.get('current_job', {}).get('role', '?')}")
    print(f"  タグ: {', '.join(seeker_profile.get('tags', []))}")
    print(f"  求人: {generated_job['title']} at {generated_job['company']}")
    print(f"  業界: {generated_job.get('industry', '?')} / 企業タイプ: {generated_job.get('company_type', '?')}")
    print("")
    
    # リアルタイムHTML生成のための初期化
    def init_realtime_html():
        html_template = f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>転職AIエージェント リアルタイムログ</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="3">
  <style>
    body {{
      font-family: 'Helvetica Neue', 'Arial', 'Hiragino Sans', 'Noto Sans JP', sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      margin: 0;
      padding: 2em;
      min-height: 100vh;
      color: white;
    }}
    .container {{
      max-width: 800px;
      margin: 0 auto;
    }}
    .header {{
      text-align: center;
      margin-bottom: 2em;
    }}
    h1 {{
      font-size: 2.5em;
      margin-bottom: 0.5em;
      font-weight: 300;
    }}
    .subtitle {{
      font-size: 1.2em;
      opacity: 0.9;
    }}
    .simulation-info {{
      background: rgba(255,255,255,0.1);
      border-radius: 15px;
      padding: 1.5em;
      margin: 1em 0;
      backdrop-filter: blur(10px);
    }}
    .progress-container {{
      background: rgba(255,255,255,0.1);
      border-radius: 15px;
      padding: 2em;
      margin: 2em 0;
      backdrop-filter: blur(10px);
    }}
    .progress-bar {{
      background: rgba(255,255,255,0.2);
      border-radius: 10px;
      height: 8px;
      margin: 1em 0;
      overflow: hidden;
    }}
    .progress-fill {{
      background: linear-gradient(90deg, #00ff88, #00ccff);
      height: 100%;
      border-radius: 10px;
      transition: width 0.5s ease;
    }}
    .current-step {{
      font-size: 1.3em;
      font-weight: 500;
      margin: 1em 0;
      padding: 1em;
      background: rgba(255,255,255,0.15);
      border-radius: 10px;
      border-left: 4px solid #00ff88;
    }}
    .steps-list {{
      margin-top: 2em;
    }}
    .step-item {{
      display: flex;
      align-items: center;
      padding: 0.8em 0;
      border-bottom: 1px solid rgba(255,255,255,0.1);
    }}
    .step-status {{
      width: 24px;
      height: 24px;
      border-radius: 50%;
      margin-right: 1em;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.8em;
    }}
    .step-completed {{
      background: #00ff88;
      color: #000;
    }}
    .step-current {{
      background: #ffaa00;
      color: #000;
    }}
    .step-pending {{
      background: rgba(255,255,255,0.2);
      color: #fff;
    }}
    .step-text {{
      flex: 1;
    }}
    .loading-spinner {{
      width: 20px;
      height: 20px;
      border: 2px solid rgba(255,255,255,0.3);
      border-top: 2px solid white;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-left: 1em;
    }}
    @keyframes spin {{
      0% {{ transform: rotate(0deg); }}
      100% {{ transform: rotate(360deg); }}
    }}
    .completion-message {{
      text-align: center;
      font-size: 1.5em;
      margin: 2em 0;
      padding: 2em;
      background: rgba(0,255,136,0.2);
      border-radius: 15px;
      border: 2px solid #00ff88;
    }}
    .refresh-info {{
      text-align: center;
      opacity: 0.7;
      font-size: 0.9em;
      margin-top: 2em;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🤖 転職AIエージェント</h1>
      <div class="subtitle">リアルタイムシミュレーション</div>
    </div>
    
    <div class="simulation-info">
      <h3>🎲 今回のシミュレーション</h3>
      <p><strong>求職者:</strong> {seeker_profile['name']} ({seeker_profile.get('age', '?')}歳)</p>
      <p><strong>現職:</strong> {seeker_profile.get('current_job', {}).get('company', '?')} - {seeker_profile.get('current_job', {}).get('role', '?')}</p>
      <p><strong>特徴:</strong> {', '.join(seeker_profile.get('tags', []))}</p>
      <p><strong>求人:</strong> {generated_job['title']} at {generated_job['company']}</p>
      <p><strong>業界:</strong> {generated_job.get('industry', '?')} / {generated_job.get('company_type', '?')}</p>
    </div>
    
    <div class="progress-container">
      <div class="current-step">
        📍 シミュレーション開始準備中...
      </div>
      <div class="progress-bar">
        <div class="progress-fill" style="width: 0%"></div>
      </div>
      <div style="text-align: center; margin: 1em 0;">
        進捗: 0/20 ステップ (0.0%)
      </div>
      
      <div class="steps-list">
        <h3>実行ステップ</h3>
        <div class="step-item">
          <div class="step-status step-pending">1</div>
          <div class="step-text">準備中...</div>
        </div>
      </div>
      
      <div class="refresh-info">
        このページは3秒ごとに自動更新されます
      </div>
    </div>
  </div>
</body>
</html>'''
        
        with open(log_html_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        print(f"📱 リアルタイムHTMLログを開始: {log_html_path}")
        print(f"ブラウザで {os.path.abspath(log_html_path)} を開いてください")
    
    def update_progress(progress):
        nonlocal current_progress
        current_progress = progress
        update_realtime_html()
    
    # update_realtime_html関数を完全実装
    def update_realtime_html(is_completed=False):
        nonlocal is_simulation_completed
        if is_completed:
            is_simulation_completed = True
        
        # 動的な進捗計算
        completed_count = len(completed_steps)
        
        # 進行中でない場合、最低でも20ステップを予想
        # 完了済みの場合、実際のステップ数をそのまま使用
        if is_simulation_completed:
            total_steps = completed_count
            progress_percentage = 100
        else:
            # 実行中は実際のステップ数より多めに見積もり
            estimated_total = max(20, completed_count + 5)
            total_steps = estimated_total
            progress_percentage = min(95, (completed_count / total_steps) * 100)  # 95%まで
        
        # 現在のステップ判定
        current_step_text = current_progress if current_progress else "待機中..."
        
        # 完了時の処理
        if is_simulation_completed:
            current_step_text = "🎉 シミュレーション完了！"
        
        # 実際に実行されたステップリストを使用
        steps_html = ""
        for i, step_name in enumerate(completed_steps):
            status_class = "step-completed"
            status_icon = "✓"
            
            steps_html += f'''
            <div class="step-item">
              <div class="step-status {status_class}">{status_icon}</div>
              <div class="step-text">{step_name}</div>
            </div>'''
        
        # 現在進行中のステップがある場合
        if current_progress and not is_simulation_completed:
            steps_html += f'''
            <div class="step-item">
              <div class="step-status step-current">●</div>
              <div class="step-text">{current_progress} <div class="loading-spinner"></div></div>
            </div>'''
        
        # 完了時の特別メッセージ
        completion_html = ""
        if is_simulation_completed:
            completion_html = '''
            <div class="completion-message">
              🎉 転職シミュレーションが完了しました！<br>
              詳細なログは静的版HTMLファイルをご確認ください。
            </div>'''
        
        # HTMLテンプレート更新
        html_template = f'''<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>転職AIエージェント リアルタイムログ</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="3">
  <style>
    body {{
      font-family: 'Helvetica Neue', 'Arial', 'Hiragino Sans', 'Noto Sans JP', sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      margin: 0;
      padding: 2em;
      min-height: 100vh;
      color: white;
    }}
    .container {{
      max-width: 800px;
      margin: 0 auto;
    }}
    .header {{
      text-align: center;
      margin-bottom: 2em;
    }}
    h1 {{
      font-size: 2.5em;
      margin-bottom: 0.5em;
      font-weight: 300;
    }}
    .subtitle {{
      font-size: 1.2em;
      opacity: 0.9;
    }}
    .simulation-info {{
      background: rgba(255,255,255,0.1);
      border-radius: 15px;
      padding: 1.5em;
      margin: 1em 0;
      backdrop-filter: blur(10px);
    }}
    .progress-container {{
      background: rgba(255,255,255,0.1);
      border-radius: 15px;
      padding: 2em;
      margin: 2em 0;
      backdrop-filter: blur(10px);
    }}
    .progress-bar {{
      background: rgba(255,255,255,0.2);
      border-radius: 10px;
      height: 8px;
      margin: 1em 0;
      overflow: hidden;
    }}
    .progress-fill {{
      background: linear-gradient(90deg, #00ff88, #00ccff);
      height: 100%;
      border-radius: 10px;
      transition: width 0.5s ease;
    }}
    .current-step {{
      font-size: 1.3em;
      font-weight: 500;
      margin: 1em 0;
      padding: 1em;
      background: rgba(255,255,255,0.15);
      border-radius: 10px;
      border-left: 4px solid #00ff88;
    }}
    .steps-list {{
      margin-top: 2em;
    }}
    .step-item {{
      display: flex;
      align-items: center;
      padding: 0.8em 0;
      border-bottom: 1px solid rgba(255,255,255,0.1);
    }}
    .step-status {{
      width: 24px;
      height: 24px;
      border-radius: 50%;
      margin-right: 1em;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.8em;
    }}
    .step-completed {{
      background: #00ff88;
      color: #000;
    }}
    .step-current {{
      background: #ffaa00;
      color: #000;
    }}
    .step-pending {{
      background: rgba(255,255,255,0.2);
      color: #fff;
    }}
    .step-text {{
      flex: 1;
    }}
    .loading-spinner {{
      width: 20px;
      height: 20px;
      border: 2px solid rgba(255,255,255,0.3);
      border-top: 2px solid white;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      margin-left: 1em;
    }}
    @keyframes spin {{
      0% {{ transform: rotate(0deg); }}
      100% {{ transform: rotate(360deg); }}
    }}
    .completion-message {{
      text-align: center;
      font-size: 1.5em;
      margin: 2em 0;
      padding: 2em;
      background: rgba(0,255,136,0.2);
      border-radius: 15px;
      border: 2px solid #00ff88;
    }}
    .refresh-info {{
      text-align: center;
      opacity: 0.7;
      font-size: 0.9em;
      margin-top: 2em;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🤖 転職AIエージェント</h1>
      <div class="subtitle">リアルタイムシミュレーション</div>
    </div>
    
    <div class="simulation-info">
      <h3>🎲 今回のシミュレーション</h3>
      <p><strong>求職者:</strong> {seeker_profile['name']} ({seeker_profile.get('age', '?')}歳)</p>
      <p><strong>現職:</strong> {seeker_profile.get('current_job', {}).get('company', '?')} - {seeker_profile.get('current_job', {}).get('role', '?')}</p>
      <p><strong>特徴:</strong> {', '.join(seeker_profile.get('tags', []))}</p>
      <p><strong>求人:</strong> {generated_job['title']} at {generated_job['company']}</p>
      <p><strong>業界:</strong> {generated_job.get('industry', '?')} / {generated_job.get('company_type', '?')}</p>
    </div>
    
    <div class="progress-container">
      <div class="current-step">
        {current_step_text}
      </div>
      <div class="progress-bar">
        <div class="progress-fill" style="width: {progress_percentage}%"></div>
      </div>
      <div style="text-align: center; margin: 1em 0;">
        進捗: {completed_count}/{total_steps} ステップ ({progress_percentage:.1f}%)
      </div>
      
      {completion_html}
      
      <div class="steps-list">
        <h3>実行ステップ</h3>
        {steps_html}
      </div>
      
      <div class="refresh-info">
        このページは3秒ごとに自動更新されます
      </div>
    </div>
  </div>
</body>
</html>'''
        
        # リアルタイムHTMLファイルへの書き込み
        with open(log_html_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        # リアルタイム表示用の固定ファイルにもコピー
        with open('examples/logs/latest_simulation.html', 'w', encoding='utf-8') as f:
            f.write(html_template)
    
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
                
                # 会話テキストの整形 - 余分な装飾を削除
                def clean_conversation_text(text):
                    # 余分な「**」や改行を整理
                    text = re.sub(r'\*\*\s*\n*\s*', '**', text)
                    # 二重アスタリスクの間に余分な空白や改行がある場合を修正
                    text = re.sub(r'\*\*\s+([^*]+?)\s+\*\*', r'**\1**', text)
                    return text
                
                # 会話テキストを整形
                content_str = clean_conversation_text(str(content))
                normalized_content = split_conversation(content_str)
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
                            # 余分な「**」を削除
                            clean_para = re.sub(r'\*\*\s*\n*\s*', '', para.strip())
                            out += f'{clean_para}  \n\n'
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
    
    def log_html(step, content):
        # ステップ完了を記録
        completed_steps.append(step)
        
        # ステップの分類とメタデータを決定
        step_meta = classify_step(step, content)
        
        # セクション構造で生成
        html_section = f'''
<div class="content-section" data-view="{step_meta['view']}" data-process="{step_meta['process']}">
  <div class="section-header">
    <h2 class="section-title">{step}</h2>
    <div class="section-meta">
      <span class="meta-tag {step_meta['view']}">{step_meta['view_label']}</span>
      {f'<span class="meta-tag {step_meta["type"]}">{step_meta["type_label"]}</span>' if step_meta.get('type') else ''}
    </div>
  </div>
  <div class="section-content">
'''
        
        if isinstance(content, dict):
            html_section += '<ul>\n'
            for k, v in content.items():
                formatted_value = json.dumps(v, ensure_ascii=False, indent=2) if isinstance(v, (dict, list)) else v
                html_section += f'<li><strong>{k}</strong>: {formatted_value}</li>\n'
            html_section += '</ul>\n'
        else:
            content_str = str(content)
            
            # 会話形式の判定と処理
            if step_meta['type'] == 'conversation':
                html_section += generate_chat_html(content_str, step_meta)
            
            # カード形式の判定と処理
            elif step_meta['type'] in ['job-posting', 'resume', 'offer']:
                html_section += generate_card_html(content_str, step_meta)
            
            # 結果・判定の強調表示
            elif step_meta['type'] == 'decision':
                html_section += generate_result_html(content_str, step_meta)
            
            # 面接Q&A
            elif step_meta['type'] == 'interview':
                html_section += generate_interview_html(content_str, step_meta)
            
            # その他の通常コンテンツ
            else:
                html_section += f'<p>{content_str.replace("\n", "<br>\n")}</p>\n'
        
        html_section += '''
  </div>
</div>
'''
        
        # 既存のHTMLコンテンツの最後のステップを更新
        if html_content:
            html_content[-1] = html_content[-1].replace('current-step', 'completed-step')
        
        html_content.append(html_section)
        
        # 進捗表示をクリア
        update_progress("")
        
        # リアルタイムHTML更新
        update_realtime_html()
    
    def classify_step(step, content):
        """ステップを分類してメタデータを返す"""
        content_str = str(content).lower()
        step_lower = step.lower()
        
        # 基本分類
        meta = {
            'view': 'all',
            'view_label': '共通',
            'process': 'other',
            'type': 'text',
            'type_label': 'テキスト'
        }
        
        # プロセス分類
        if any(kw in step_lower for kw in ['転職相談', '会話']):
            meta['process'] = 'consultation'
        elif any(kw in step_lower for kw in ['求人', '概要', '推し']):
            meta['process'] = 'job-proposal'
        elif any(kw in step_lower for kw in ['書類', '選考', '履歴書']):
            meta['process'] = 'document-screening'
        elif any(kw in step_lower for kw in ['面接', 'interview']):
            meta['process'] = 'interview'
        elif any(kw in step_lower for kw in ['オファー', '交渉', 'offer']):
            meta['process'] = 'offer'
        elif any(kw in step_lower for kw in ['判断', '決断', '受諾', '辞退']):
            meta['process'] = 'final-decision'
        
        # 視点分類
        if any(kw in step_lower for kw in ['企業側', 'empai', 'simhr', 'hr', '企業判定']):
            meta['view'] = 'company'
            meta['view_label'] = '企業視点'
        elif any(kw in step_lower for kw in ['求職者側', 'seeker', '求職者判定']):
            meta['view'] = 'seeker'
            meta['view_label'] = '求職者視点'
        elif any(kw in step_lower for kw in ['判定', '合否', '決断', '結果']):
            meta['view'] = 'decision'
            meta['view_label'] = '判定・結果'
        
        # コンテンツタイプ分類
        if any(speaker in content_str for speaker in ['seeker:', 'seekerai:', 'hr:', 'empai:', '👤', '🎯', '👨‍💼', '👩‍💻', '🤖']):
            meta['type'] = 'conversation'
            meta['type_label'] = '会話'
        elif any(kw in content_str for kw in ['【基本情報】', '【スキル・条件】', '【特徴・ミッション】']):
            meta['type'] = 'job-posting'
            meta['type_label'] = '求人票'
        elif any(kw in content_str for kw in ['【職務経歴】', '【スキル】', '【自己pr】']):
            meta['type'] = 'resume'
            meta['type_label'] = '履歴書'
        elif any(kw in step_lower for kw in ['質問', '回答', '面接']):
            meta['type'] = 'interview'
            meta['type_label'] = '面接'
        elif any(kw in step_lower for kw in ['判定', '合否', '決断', '最終決断']):
            meta['type'] = 'decision'
            meta['type_label'] = '判定'
        elif any(kw in step_lower for kw in ['オファー', '交渉']):
            meta['type'] = 'offer'
            meta['type_label'] = 'オファー'
        
        return meta
    
    def generate_chat_html(content_str, meta):
        """チャット形式のHTML生成"""
        html = '<div class="chat-container">\n'
        
        # アイコン付き発言者を識別
        icon_speakers = {
            '👤': ('seeker', '求職者'),
            '🎯': ('agent', '転職AI'),
            '👨‍💼': ('hr', 'HR'),
            '👩‍💻': ('hr', '面接官'),
            '🤖': ('empai', 'AI')
        }
        
        # 従来の発言者も識別
        text_speakers = {
            'seeker:': ('seeker', '求職者'),
            'seekerai:': ('agent', '転職AI'),
            'hr:': ('hr', '人事'),
            'employeragent:': ('hr', '企業担当')
        }
        
        # 行ごとに処理
        lines = content_str.split('\n')
        current_speaker = ""
        current_class = ""
        current_name = ""
        message = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # アイコン付き発言者を検出
            found_speaker = False
            for icon, (class_name, display_name) in icon_speakers.items():
                if line.startswith(icon):
                    if message and current_speaker:
                        html += generate_chat_bubble(message, current_class, current_name)
                    current_speaker = icon
                    current_class = class_name
                    current_name = display_name
                    message = line[len(icon):].strip()
                    found_speaker = True
                    break
            
            if not found_speaker:
                # 従来の発言者を検出
                line_lower = line.lower()
                for speaker, (class_name, display_name) in text_speakers.items():
                    if line_lower.startswith(speaker):
                        if message and current_speaker:
                            html += generate_chat_bubble(message, current_class, current_name)
                        current_speaker = speaker
                        current_class = class_name
                        current_name = display_name
                        message = line[len(speaker):].strip()
                        found_speaker = True
                        break
                
                if not found_speaker and current_speaker:
                    # 継続メッセージ
                    message += " " + line
        
        # 最後のメッセージを出力
        if message and current_speaker:
            html += generate_chat_bubble(message, current_class, current_name)
        
        html += '</div>\n'
        return html
    
    def generate_chat_bubble(message, class_name, display_name):
        """チャットバブルHTML生成"""
        return f'''
<div class="chat-bubble {class_name}">
  <div class="sender">{display_name}</div>
  {message}
</div>
'''
    
    def generate_card_html(content_str, meta):
        """カード形式のHTML生成"""
        card_class = meta['type']
        title = meta['type_label']
        
        # 構造化された情報を解析
        content_formatted = content_str.replace('\n', '<br>\n')
        content_formatted = re.sub(r'\*\*【(.+?)】\*\*', r'<h4>\1</h4>', content_formatted)
        content_formatted = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content_formatted)
        
        return f'''
<div class="info-card {card_class}">
  <div class="card-header">
    <h3 class="card-title">{title}</h3>
  </div>
  {content_formatted}
</div>
'''
    
    def generate_result_html(content_str, meta):
        """結果・判定のHTML生成"""
        # ポジティブ・ネガティブ判定
        is_positive = any(kw in content_str for kw in ['合格', '通過', '受諾', '継続', '進む', 'オファー段階'])
        is_negative = any(kw in content_str for kw in ['不合格', '見送り', '辞退', '終了'])
        
        result_class = 'positive' if is_positive else 'negative' if is_negative else ''
        
        return f'''
<div class="result-highlight {result_class}">
  {content_str.replace('\n', '<br>\n')}
</div>
'''
    
    def generate_interview_html(content_str, meta):
        """面接Q&A形式のHTML生成"""
        title = "面接質問" if "質問" in meta['type_label'] else "面接回答"
        
        # 構造化された情報を調整
        content_formatted = re.sub(r'\*\*(.+?):\*\*', r'<strong>\1:</strong>', content_str)
        
        return f'''
<div class="info-card interview">
  <div class="card-header">
    <h3 class="card-title">{title}</h3>
  </div>
  <p>{content_formatted.replace('\n', '<br>\n')}</p>
</div>
'''
    
    def generate_html_file():
        # 最終的なHTMLファイル生成（従来の機能）
        template_path = 'logs/転職AIエージェント_シミュレーションログ_UI形式_最終版.html'
        try:
            with open(template_path, 'r', encoding='utf-8') as template_file:
                template = template_file.read()
            
            # テンプレートのコンテンツ挿入位置を特定
            content_placeholder = '<!-- Canvasから貼り付けた最終版がここに入ります -->'
            complete_html = template.replace(content_placeholder, '\n'.join(html_content))
            
            # 静的版のファイル名
            static_html_path = log_html_path.replace('.html', '_static.html')
            with open(static_html_path, 'w', encoding='utf-8') as f:
                f.write(complete_html)
            print(f"📄 静的版HTMLログも保存: {static_html_path}")
        except FileNotFoundError:
            print(f"警告: HTMLテンプレートファイル '{template_path}' が見つかりません。")
    
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

    # リアルタイムHTML初期化
    init_realtime_html()

    # エージェント初期化（seeker_agentを先に）
    seeker_agent = SeekerAgent()
    simulated_hr = SimulatedHR()
    simulated_hr.llm = seeker_agent.llm
    employer_agent = EmployerAgent()

    # 既存のHR要望生成は残す（互換性のため）
    hr_needs = simulated_hr.provide_needs()
    log_json("0.1. SimulatedHRの求人要望", hr_needs)
    log_md("0.1. SimulatedHRの求人要望", hr_needs)
    log_html("0.1. SimulatedHRの求人要望", hr_needs)

    # HRとEmployerAgentの会話を生成
    with open("prompts/hr_employer_conversation.txt", encoding="utf-8") as f:
        hr_emp_conv_prompt = f.read().strip()
    hr_emp_conv_prompt_filled = hr_emp_conv_prompt.format(hr_needs=json.dumps(hr_needs, ensure_ascii=False, indent=2))
    # LLMで会話生成（seeker_agentを流用）
    hr_emp_conversation = await seeker_agent.llm.generate_content_async(
        hr_emp_conv_prompt_filled, 
        agent_name="HRとEmployerの会話生成",
        progress_callback=update_progress
    )
    
    # 会話の整形処理
    # LLMの出力から余分な「**」や改行を除去し、整形する
    hr_emp_conversation_clean = re.sub(r'\*\*\s*\n*\s*', '**', hr_emp_conversation)
    
    log_json("0.1.5. HRとEmployerAgentの会話", hr_emp_conversation_clean)
    log_md("0.1.5. HRとEmployerAgentの会話", hr_emp_conversation_clean)
    log_html("0.1.5. HRとEmployerAgentの会話", hr_emp_conversation_clean)

    # DataManagerで生成された求人を使用（HR要望ベースの求人生成は引き続き実行するが、実際のシミュレーションでは使わない）
    traditional_job_posting = employer_agent.create_job_posting(simulated_hr)
    log_json("0.2. EmployerAgentが生成した従来求人票（参考）", traditional_job_posting)
    formatted_traditional_job_posting = format_job_posting_md(traditional_job_posting)
    log_md("0.2. EmployerAgentが生成した従来求人票（参考）", formatted_traditional_job_posting)
    log_html("0.2. EmployerAgentが生成した従来求人票（参考）", formatted_traditional_job_posting)
    print("\n【従来の求人生成（参考）】")
    print(traditional_job_posting)

    # DataManagerで選択した求人票を実際のシミュレーションで使用
    log_json("0.3. 今回使用する求人票", generated_job)
    formatted_generated_job = format_job_posting_md(generated_job)
    log_md("0.3. 今回使用する求人票", formatted_generated_job)
    log_html("0.3. 今回使用する求人票", formatted_generated_job)
    print("\n【今回のシミュレーションで使用する求人票】")
    print(generated_job)

    # job_listを選択された求人とする
    job_list = [generated_job]

    # エージェント初期化
    simulated_seeker = SimulatedSeeker()
    # 面接官情報を求人データから取得
    interviewer_info = None
    if generated_job.get("interviewers"):
        interviewer_info = generated_job["interviewers"][0]  # 最初の面接官を使用
    
    if interviewer_info is None:
        # フォールバック：デフォルトの面接官情報
        interviewer_info = {
            "name": "田中部長",
            "role": "開発部長",
            "availability": [
                {
                    "start": "2025-01-20T14:00:00+09:00",
                    "end": "2025-01-20T18:00:00+09:00"
                },
                {
                    "start": "2025-01-22T10:00:00+09:00",
                    "end": "2025-01-22T16:00:00+09:00"
                }
            ]
        }
    
    interviewer = SimulatedInterviewer(info=interviewer_info)

    # --- seekerとseekerAIの会話をまとめて生成・表示 ---
    conversation_example = await simulated_seeker.start_conversation(seeker_profile)
    print("\n【転職相談の会話】")
    print(conversation_example)
    log_json("1. 転職相談の会話", conversation_example)
    log_md("1. 転職相談の会話", conversation_example)
    log_html("1. 転職相談の会話", conversation_example)

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
        job_summary = await seeker_agent.propose_job_summary(job, progress_callback=update_progress)
        print("\n【キャリアアドバイザーの求人概要】")
        print(job_summary)
        log_json(step, job_summary)
        log_md(step, job_summary)
        log_html(step, job_summary)

        step = step_title("求人推しプレゼン")
        job_pitch = await seeker_agent.propose_job_pitch(seeker_profile, job, progress_callback=update_progress)
        print("\n【キャリアアドバイザーの推しポイント】")
        print(job_pitch)
        log_json(step, job_pitch)
        log_md(step, job_pitch)
        log_html(step, job_pitch)

        # --- 応募意思確認 ---
        step = step_title("応募意思確認")
        job_intent = await simulated_seeker.job_intent(job_pitch)
        print("\n【求職者の応募意思】")
        print(job_intent)
        log_json(step, job_intent)
        log_md(step, job_intent)
        log_html(step, job_intent)

        # --- 応募理由（履歴書＋AI推薦コメント一体型）生成 ---
        step = step_title("応募理由・AI推薦付き履歴書")
        application_reason = await simulated_seeker.application_reason(seeker_profile, job_list[0])
        print("\n【応募理由・AI推薦付き履歴書】")
        print(application_reason)
        log_json(step, application_reason)
        log_md(step, application_reason)
        log_html(step, application_reason)

        if any(kw in job_intent for kw in ["見送", "応募しない", "辞退", "やめる", "考えたい"]):
            print("応募辞退のためシミュレーションを終了します。")
            update_realtime_html(is_completed=True)  # 完了状態に更新
            generate_html_file()  # HTML生成
            return
                
        # --- 書類選考プロセス（新フロー） ---
        step = step_title("履歴書提出")
        resume = seeker_agent.generate_resume(seeker_profile)
        print("\n【履歴書・職務経歴書】")
        print(resume)
        log_json(step, resume)
        log_md(step, resume)
        log_html(step, resume)

        step = step_title("empaiによる書類審査")
        empai_judgement = await employer_agent.screen_resume_llm(resume)
        print("\n【empaiの書類審査】")
        print(empai_judgement["raw"])
        log_json(step, empai_judgement)
        log_md(step, empai_judgement["raw"])
        log_html(step, empai_judgement["raw"])

        step = step_title("simhrの意見")
        simhr_opinion = await simulated_hr.opine_on_resume_screening(resume, empai_judgement)
        print("\n【simhrの意見】")
        print(simhr_opinion["raw"])
        log_json(step, simhr_opinion)
        log_md(step, simhr_opinion["raw"])
        log_html(step, simhr_opinion["raw"])

        # --- 最終合否決定 ---
        step = step_title("書類選考・最終判定")
        # シンプルなロジック例：empaiが合格でsimhrが賛成→合格、それ以外は不合格
        if empai_judgement["decision"] == "合格" and simhr_opinion["stance"] == "agree":
            final_result = "合格"
            final_reason = f"empai・simhrともに合格判断。理由: {empai_judgement['reason']} / {simhr_opinion['reason']}"
        else:
            final_result = "不合格"
            final_reason = f"empaiまたはsimhrが不合格・反対判断。理由: {empai_judgement['reason']} / {simhr_opinion['reason']}"
        print(f"\n【書類選考・最終判定】{final_result}\n{final_reason}")
        log_json(step, {"result": final_result, "reason": final_reason})
        log_md(step, f"合否: {final_result}\n理由: {final_reason}")
        log_html(step, f"合否: {final_result}\n理由: {final_reason}")
        # 不合格の場合は終了
        if final_result == "不合格":
            print("書類選考で不合格のため、シミュレーションを終了します。")
            update_realtime_html(is_completed=True)  # 完了状態に更新
            generate_html_file()  # HTML生成
            return
        
        # 合格の場合は面接プロセスに進む
        print("書類選考に合格しました。面接プロセスに進みます。")

        # --- 面接プロセス多段階化 ---
        interview_stages = ["一次面接", "二次面接", "最終面接"]
        interview_results = []  # 各面接の結果を保存
        scheduled_interviews = {}  # 各ステージのスケジュール情報を保存
        
        # 面接官情報を jobs.jsonから取得（複数ステージ対応）
        stage_interviewers = {}
        for job in jobs:
            if job.get("interviewers"):
                for interviewer in job["interviewers"]:
                    stage = interviewer.get("stage", "一次面接")
                    stage_interviewers[stage] = interviewer
                break
        
        # フォールバック：各ステージの面接官が見つからない場合
        if not stage_interviewers:
            stage_interviewers = {
                "一次面接": {
                    "name": "田中部長", "role": "開発部長",
                    "email": "tanaka@company.co.jp", "scheduling_method": "calendar",
                    "interview_duration": 45,
                    "availability": [
                        {"start": "2025-01-20T14:00:00+09:00", "end": "2025-01-20T18:00:00+09:00"},
                        {"start": "2025-01-22T10:00:00+09:00", "end": "2025-01-22T16:00:00+09:00"}
                    ]
                },
                "二次面接": {
                    "name": "佐藤リーダー", "role": "テックリード",
                    "email": "sato@company.co.jp", "scheduling_method": "email",
                    "interview_duration": 60, "availability": None, "preferred_times": "平日 10:00-18:00"
                },
                "最終面接": {
                    "name": "山本CTO", "role": "技術責任者",
                    "email": "yamamoto@company.co.jp", "scheduling_method": "calendar",
                    "interview_duration": 60,
                    "availability": [
                        {"start": "2025-01-24T14:00:00+09:00", "end": "2025-01-24T18:00:00+09:00"}
                    ]
                }
            }
        
        for i, stage in enumerate(interview_stages):
            print(f"\n【{stage}】")
            
            # --- 🆕 各ステージでの日程調整 ---
            step = step_title(f"{stage}・日程調整")
            current_interviewer_info = stage_interviewers.get(stage)
            
            if current_interviewer_info:
                print(f"\n【{stage}・日程調整】")
                print(f"面接官: {current_interviewer_info['name']} ({current_interviewer_info['role']})")
                
                # 面接官インスタンスを作成
                stage_interviewer = SimulatedInterviewer(info=current_interviewer_info)
                
                # 日程調整実行
                schedule_result = stage_interviewer.schedule_interview(
                    seeker_data=seeker_profile,
                    stage=stage,
                    company_name=job_list[0].get("company", ""),
                    position=job_list[0].get("title", "")
                )
                
                if schedule_result:
                    if isinstance(schedule_result, dict) and schedule_result.get("status") == "email_sent":
                        # メール送信の場合
                        print("📧 面接官へのメール送信が完了しました。返信待ちです。")
                        
                        # 🆕 メール返信をシミュレート（デモ用）
                        print(f"\n【{stage}・面接官返信シミュレート】")
                        simulated_reply = stage_interviewer.schedule_agent.email_agent.simulate_interviewer_reply(
                            schedule_result["candidate_slots"], 
                            "positive"
                        )
                        print("シミュレート返信:")
                        print(simulated_reply)
                        
                        # 返信処理
                        reply_result = stage_interviewer.schedule_agent.process_interview_reply(
                            schedule_result["request_id"], 
                            simulated_reply
                        )
                        
                        if reply_result["status"] == "confirmed":
                            scheduled_slot = reply_result["confirmed_slot"]
                            interview_format = reply_result.get("interview_format", "オンライン")
                            print(f"✅ {stage}の日程確定: {simulated_reply[:30]}...")
                        else:
                            print(f"❌ {stage}の返信処理失敗: {reply_result['message']}")
                            scheduled_slot = None
                    else:
                        # カレンダー自動調整の場合
                        scheduled_slot = schedule_result
                        interview_format = "オンライン"  # デフォルト
                    
                    if scheduled_slot:
                        # 求職者への通知
                        seeker_response = simulated_seeker.notify_interview_scheduled(
                            scheduled_slot, 
                            current_interviewer_info.get("name", "面接官")
                        )
                        
                        # スケジュール情報を保存
                        scheduled_interviews[stage] = {
                            "scheduled_slot": scheduled_slot,
                            "interviewer_info": current_interviewer_info,
                            "interview_format": interview_format,
                            "seeker_response": seeker_response
                        }
                        
                        # ログに記録
                        schedule_log = {
                            "stage": stage,
                            "scheduled_start": scheduled_slot["start"],
                            "scheduled_end": scheduled_slot["end"],
                            "interviewer_name": current_interviewer_info.get("name", "面接官"),
                            "interviewer_role": current_interviewer_info.get("role", "面接官"),
                            "interview_format": interview_format,
                            "seeker_response": seeker_response
                        }
                        log_json(step, schedule_log)
                        log_md(step, f"{stage}日程調整完了\n- 日時: {scheduled_slot['start']} 〜 {scheduled_slot['end']}\n- 面接官: {current_interviewer_info.get('name', '面接官')}\n- 形式: {interview_format}\n- 求職者応答: {seeker_response}")
                        log_html(step, f"{stage}日程調整完了\n日時: {scheduled_slot['start']} 〜 {scheduled_slot['end']}\n面接官: {current_interviewer_info.get('name', '面接官')}\n形式: {interview_format}")
                    else:
                        print(f"⚠️ {stage}の日程調整に失敗しました。")
                        log_json(step, {"result": "日程調整失敗", "stage": stage})
                        log_md(step, f"{stage}日程調整失敗")
                        log_html(step, f"{stage}日程調整失敗")
                        print("日程調整ができないため、シミュレーションを終了します。")
                        update_realtime_html(is_completed=True)
                        generate_html_file()
                        return
                else:
                    print(f"⚠️ {stage}の日程調整に失敗しました。")
                    log_json(step, {"result": "日程調整失敗", "stage": stage})
                    log_md(step, f"{stage}日程調整失敗")
                    log_html(step, f"{stage}日程調整失敗")
                    print("日程調整ができないため、シミュレーションを終了します。")
                    update_realtime_html(is_completed=True)
                    generate_html_file()
                    return
            else:
                print(f"⚠️ {stage}の面接官情報が見つかりません。")
                log_json(step, {"result": "面接官情報なし", "stage": stage})
                log_md(step, f"{stage}面接官情報なし")
                log_html(step, f"{stage}面接官情報なし")
            
            # --- 面接実施 ---
            # スケジュール情報を表示
            if stage in scheduled_interviews:
                schedule_info = scheduled_interviews[stage]
                print(f"予定日時: {schedule_info['scheduled_slot']['start']} 〜 {schedule_info['scheduled_slot']['end']}")
                print(f"面接官: {schedule_info['interviewer_info']['name']} ({schedule_info['interviewer_info']['role']})")
                print(f"形式: {schedule_info['interview_format']}")
                
                # 面接官インスタンスを使用
                interviewer = SimulatedInterviewer(info=schedule_info['interviewer_info'])
            else:
                # フォールバック
                interviewer = SimulatedInterviewer(info=current_interviewer_info or {})
            
            question = await interviewer.generate_question(job_list[0], stage=stage, seeker_profile=seeker_profile, resume=resume)
            print("【面接質問】")
            print(question)
            log_json(step_title(f"{stage} 質問"), question)
            log_md(step_title(f"{stage} 質問"), question)
            log_html(step_title(f"{stage} 質問"), question)

            answer = await simulated_seeker.answer_interview(question, seeker_profile=seeker_profile)
            print("【面接回答】")
            print(answer)
            log_json(step_title(f"{stage} 回答"), answer)
            log_md(step_title(f"{stage} 回答"), answer)
            log_html(step_title(f"{stage} 回答"), answer)

            # 面接結果を記録（評価は振り返り会議で行う）
            interview_results.append({
                "stage": stage,
                "question": question,
                "answer": answer,
                "schedule_info": scheduled_interviews.get(stage)
            })
            
            # --- 企業側振り返り会議（会話形式） ---
            step = step_title(f"{stage}後・企業側振り返り会議")
            
            # 振り返り会議を会話形式で生成
            reflection_prompt = f"""
あなたは企業の採用チームの振り返り会議をシミュレートしてください。{stage}が終了し、3人の担当者が議論します。

【面接情報】
- 段階: {stage}
- 面接質問: {question}
- 求職者回答: {answer}

【参加者】
- 👨‍💼 HR（佐藤）: 採用全体を俯瞰し、会社のニーズとマッチするかを判断する人事担当
- 👩‍💻 面接官（田中）: 技術面・人物面での直接評価を提供する現場マネージャー  
- 🤖 empai: データ分析的観点から客観的判断を提供するAI採用支援システム

【これまでの選考経過】
- 書類選考: 合格
- 今回の面接: {stage}

次の段階は「{"オファー検討" if i == len(interview_stages)-1 else interview_stages[i+1]}」です。

実際の会議のように、3者が自然に議論し、最終的に次のステップの判定（進む/見送り）を決定してください。
会話は以下の形式で：

👨‍💼 HR（佐藤）: [発言内容]
👩‍💻 面接官（田中）: [発言内容]
🤖 empai: [発言内容]
👨‍💼 HR（佐藤）: [発言内容]
...

最後に明確な結論を示してください。

出力は必ず日本語のみで行ってください。
"""
            
            reflection_result = await seeker_agent.llm.generate_content_async(
                reflection_prompt,
                agent_name=f"{stage}後振り返り会議",
                progress_callback=update_progress
            )
            
            print(f"\n【{stage}後・企業側振り返り会議】")
            print(reflection_result)
            log_json(step, reflection_result)
            log_md(step, reflection_result)
            log_html(step, reflection_result)
            
            # 企業側判定結果を抽出
            if any(keyword in reflection_result for keyword in ["見送り", "不合格", "次に進まない", "お断り", "辞退"]):
                company_decision = "見送り"
                print(f"\n【{stage}・企業判定】見送り")
                print(f"{stage}で企業側が見送りのため、選考を終了します。")
                log_json(step_title(f"{stage} 企業判定"), {"result": "見送り", "reason": "企業側振り返り会議での判断"})
                log_md(step_title(f"{stage} 企業判定"), "見送り")
                log_html(step_title(f"{stage} 企業判定"), "見送り")
                update_realtime_html(is_completed=True)  # 完了状態に更新
                generate_html_file()  # HTML生成
                return
            else:
                company_decision = "進む"
                next_step = interview_stages[i+1] if i < len(interview_stages)-1 else "オファー段階"
                print(f"\n【{stage}・企業判定】{next_step}に進む")
                log_json(step_title(f"{stage} 企業判定"), {"result": company_decision, "next_step": next_step})
                log_md(step_title(f"{stage} 企業判定"), f"{next_step}に進む")
                log_html(step_title(f"{stage} 企業判定"), f"{next_step}に進む")
            
            # --- 求職者側振り返り会議（新機能） ---
            step = step_title(f"{stage}後・求職者側振り返り会議")
            
            # 求職者側振り返り会議を会話形式で生成
            seeker_reflection_prompt = f"""
あなたは転職活動中の求職者とその転職エージェントの振り返り会議をシミュレートしてください。{stage}が終了し、2人で面接の印象を議論します。

【面接情報】
- 段階: {stage}
- 面接質問: {question}
- 求職者回答: {answer}
- 企業側判定: {company_decision}

【参加者】
- 👤 seeker（山田太郎）: 求職者本人の感情、印象、不安、直感を表現
- 🎯 seekerAI（転職エージェント）: 客観的アドバイス、キャリア視点、市場分析を提供

【検討ポイント】
- 面接体験（面接官の対応、質問の質、雰囲気）
- 企業文化（価値観の一致、働き方、チームの印象）  
- キャリア影響（成長機会、スキル向上、将来性）
- 直感・感情（なんとなくの印象、違和感、ワクワク感）

実際の面接後の会話のように、求職者の率直な感想と転職エージェントのアドバイスを自然に表現してください。
最終的に「継続したい/条件付き継続/辞退したい」のいずれかの判定を示してください。

会話は以下の形式で：

👤 seeker: [発言内容]
🎯 seekerAI: [発言内容]
👤 seeker: [発言内容]
🎯 seekerAI: [発言内容]
...

最後に明確な継続意思を示してください。

出力は必ず日本語のみで行ってください。
"""
            
            seeker_reflection_result = await seeker_agent.llm.generate_content_async(
                seeker_reflection_prompt,
                agent_name=f"{stage}後求職者振り返り",
                progress_callback=update_progress
            )
            
            print(f"\n【{stage}後・求職者側振り返り会議】")
            print(seeker_reflection_result)
            log_json(step, seeker_reflection_result)
            log_md(step, seeker_reflection_result)
            log_html(step, seeker_reflection_result)
            
            # 求職者側判定結果をLLMで分析
            seeker_decision_prompt = f"""
以下の求職者側振り返り会議の内容を分析し、求職者が選考を「継続したい」か「辞退したい」かを判定してください。

【振り返り会議の内容】
{seeker_reflection_result}

【判定基準】
- 「継続したい」「条件付き継続」「進みたい」などの表現がある場合は「継続」
- 「辞退したい」「やめたい」「合わない」「継続しない」などの表現がある場合は「辞退」
- 迷いや不安があっても、最終的に前向きな意思が示されている場合は「継続」
- 明確な判定表現がない場合、全体的な文脈から判断

以下のフォーマットで回答してください：
判定: 継続 または 辞退
理由: [判定理由を1-2文で]

必ず日本語で回答してください。
"""
            
            seeker_decision_result = await seeker_agent.llm.generate_content_async(
                seeker_decision_prompt,
                agent_name=f"{stage}求職者判定分析",
                progress_callback=update_progress
            )
            
            print(f"\n【{stage}・求職者判定分析】")
            print(seeker_decision_result)
            
            # LLMの判定結果から「継続」または「辞退」を抽出
            if "判定: 継続" in seeker_decision_result or "判定：継続" in seeker_decision_result:
                seeker_decision = "継続"
            elif "判定: 辞退" in seeker_decision_result or "判定：辞退" in seeker_decision_result:
                seeker_decision = "辞退"
            else:
                # LLMの回答から判定を推測（フォールバック）
                if any(keyword in seeker_decision_result for keyword in ["継続", "進む", "前向き"]):
                    seeker_decision = "継続"
                else:
                    seeker_decision = "辞退"
            
            if seeker_decision == "辞退":
                print(f"\n【{stage}・求職者判定】辞退")
                print(f"{stage}で求職者が辞退のため、選考を終了します。")
                log_json(step_title(f"{stage} 求職者判定"), {"result": "辞退", "reason": "求職者側振り返り会議での判断"})
                log_md(step_title(f"{stage} 求職者判定"), "辞退")
                log_html(step_title(f"{stage} 求職者判定"), "辞退")
                update_realtime_html(is_completed=True)  # 完了状態に更新
                generate_html_file()  # HTML生成
                return
            else:
                seeker_decision = "継続"
                print(f"\n【{stage}・求職者判定】継続")
                log_json(step_title(f"{stage} 求職者判定"), {"result": seeker_decision})
                log_md(step_title(f"{stage} 求職者判定"), "継続")
                log_html(step_title(f"{stage} 求職者判定"), "継続")
            
            # --- 最終判定（企業・求職者両方の意思確認） ---
            print(f"\n【{stage}・最終判定】企業:{company_decision} × 求職者:{seeker_decision}")
            if company_decision == "進む" and seeker_decision == "継続":
                if i < len(interview_stages)-1:
                    print(f"{next_step}に進みます。")
                else:
                    print("全面接を通過しました。オファー段階に進みます。")
            
            log_json(step_title(f"{stage} 最終判定"), {
                "company_decision": company_decision, 
                "seeker_decision": seeker_decision,
                "result": f"{next_step}に進む" if i < len(interview_stages)-1 else "オファー段階に進む"
            })
            log_md(step_title(f"{stage} 最終判定"), f"企業:{company_decision} × 求職者:{seeker_decision}")
            log_html(step_title(f"{stage} 最終判定"), f"企業:{company_decision} × 求職者:{seeker_decision}")

        # --- オファー交渉ステップ ---
        # 面接評価リストを作成
        interview_evaluations = []
        for result in interview_results:
            interview_evaluations.append(result["answer"])
        
        # 面接評価と求職者プロフィールに基づく動的オファー生成
        offer = employer_agent.generate_initial_offer(
            seeker_profile=seeker_profile,
            job=job_list[0],
            interview_evaluations=interview_evaluations
        )
        print("\n【初回オファー提示】")
        print(offer)
        log_json(step_title("初回オファー提示"), offer)
        log_md(step_title("初回オファー提示"), offer)
        log_html(step_title("初回オファー提示"), offer)

        max_rounds = 3
        for round_num in range(1, max_rounds + 1):
            print(f"\n【オファー交渉ラウンド{round_num}】")
            request = await seeker_agent.request_offer_change(offer)
            print("求職者リクエスト:", request)
            log_json(step_title(f"交渉ラウンド{round_num} 求職者リクエスト"), request)
            log_md(step_title(f"交渉ラウンド{round_num} 求職者リクエスト"), request)
            log_html(step_title(f"交渉ラウンド{round_num} 求職者リクエスト"), request)
            if request == "特にありません":
                print("合意に達しました。")
                log_json(step_title(f"交渉ラウンド{round_num} 合意"), offer)
                log_md(step_title(f"交渉ラウンド{round_num} 合意"), offer)
                log_html(step_title(f"交渉ラウンド{round_num} 合意"), offer)
                break
            offer = await employer_agent.update_offer(offer, request)
            print("企業再提示:", offer)
            log_json(step_title(f"交渉ラウンド{round_num} 企業再提示"), offer)
            log_md(step_title(f"交渉ラウンド{round_num} 企業再提示"), offer)
            log_html(step_title(f"交渉ラウンド{round_num} 企業再提示"), offer)
            if round_num == max_rounds:
                print("最大ラウンドに達したため、現状オファーで最終判断します。")
                log_json(step_title(f"交渉ラウンド{round_num} 打ち切り"), offer)
                log_md(step_title(f"交渉ラウンド{round_num} 打ち切り"), offer)
                log_html(step_title(f"交渉ラウンド{round_num} 打ち切り"), offer)

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
        
        # 迷いの詳細情報を表示
        hesitation_score = offer_decision_result.get("hesitation_score", 0)
        hesitation_factors = offer_decision_result.get("hesitation_factors", [])
        decision_confidence = offer_decision_result.get("decision_confidence", 0)
        
        print(f"\n【迷いの分析】")
        print(f"迷いスコア: {hesitation_score}")
        if hesitation_factors:
            print("迷いの要因:")
            for factor in hesitation_factors:
                print(f"  - {factor}")
        
        confidence_labels = ["推測判断", "傾向判断", "明確な表現", "明示的決断"]
        confidence_text = confidence_labels[min(decision_confidence, 3)]
        print(f"決断の信頼度: {confidence_text}")
        
        log_json(step, offer_decision_result)
        log_md(step, offer_decision_result["conversation"])
        log_html(step, offer_decision_result["conversation"])
        
        # 最終決断のみ分けて表示
        final_decision = "受諾" if offer_decision_result["decision"] else "辞退"
        print(f"\n【最終決断】{final_decision}")
        log_json(step_title("最終決断"), {"decision": final_decision, "confidence": confidence_text, "score": hesitation_score})
        log_md(step_title("最終決断"), final_decision)
        log_html(step_title("最終決断"), final_decision)
    else:
        print("求人の話を聞きたい意思が示されなかったため、シミュレーションを終了します。")
        update_realtime_html(is_completed=True)  # 完了状態に更新
        generate_html_file()  # HTML生成
        return

    # シミュレーション完了後、examples/logsにサンプルログをコピー
    print("\n【シミュレーション完了】")
    print(f"ログは logs/simulation_log_{now_str}.md と logs/simulation_log_{now_str}.jsonl に保存されました")
    
    # HTML生成
    update_realtime_html(is_completed=True)  # 完了状態に更新
    generate_html_file()
    print(f"HTML形式のログも logs/simulation_log_{now_str}.html に保存されました")
    
    # examples/logsディレクトリの作成とログファイルのコピー
    try:
        # examples/logsディレクトリが存在しない場合は作成
        os.makedirs('examples/logs', exist_ok=True)
        
        # 最新ログをコピー
        shutil.copy(log_md_path, 'examples/logs/latest_simulation.md')
        shutil.copy(log_path, 'examples/logs/latest_simulation.jsonl')
        shutil.copy(log_html_path, 'examples/logs/latest_simulation.html')
        
        print("\n【サンプルログを更新】")
        print("examples/logs/latest_simulation.md と examples/logs/latest_simulation.jsonl と examples/logs/latest_simulation.html を更新しました")
        print("※このサンプルログはGitHubリポジトリに含まれます。個人情報が含まれていないか確認してください。")
    except Exception as e:
        print(f"\n【サンプルログ更新エラー】: {e}")
        print("examples/logsへのコピーに失敗しました。")

if __name__ == "__main__":
    asyncio.run(main()) 