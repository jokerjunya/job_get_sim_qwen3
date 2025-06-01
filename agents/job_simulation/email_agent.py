import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional
import pytz
import json
import re


class EmailAgent:
    """
    面接日程調整のためのメール自動送信を行うエージェント
    """
    
    def __init__(self, smtp_server="localhost", smtp_port=587, username=None, password=None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.timezone = pytz.timezone('Asia/Tokyo')
    
    def format_datetime_japanese(self, iso_string: str) -> str:
        """ISO8601日時を日本語形式に変換"""
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        jst_dt = dt.astimezone(self.timezone)
        return jst_dt.strftime("%Y年%m月%d日(%a) %H:%M")
    
    def parse_interview_reply(self, reply_text: str, candidate_slots: List[Dict[str, str]]) -> Dict:
        """
        面接官からの返信メールを解析して面接確定情報を抽出
        
        Args:
            reply_text: 返信メールの本文
            candidate_slots: 提案した候補日程リスト
            
        Returns:
            {
                "status": "confirmed" | "alternative" | "rejected" | "unclear",
                "selected_slot": {...} | None,
                "alternative_request": str | None,
                "interview_format": "オンライン" | "対面" | None,
                "additional_requests": str | None,
                "confidence": float  # 解析の信頼度 0-1
            }
        """
        
        reply_lower = reply_text.lower().strip()
        result = {
            "status": "unclear",
            "selected_slot": None,
            "alternative_request": None,
            "interview_format": None,
            "additional_requests": None,
            "confidence": 0.0
        }
        
        # 候補番号の抽出パターン
        candidate_patterns = [
            r'候補\s*([123])',  # 候補1, 候補 2 など
            r'([123])\s*番',     # 1番, 2 番 など
            r'([123])\s*希望',   # 1希望, 2 希望 など
            r'([123])\s*で',     # 1で, 2 で など
            r'([123])\s*を希望', # 1を希望, 2 を希望 など
            r'([123])\s*でお願い', # 1でお願い など
        ]
        
        selected_candidate = None
        max_confidence = 0
        
        for pattern in candidate_patterns:
            matches = re.findall(pattern, reply_lower)
            if matches:
                # 最初に見つかった候補番号を使用
                candidate_num = int(matches[0])
                if 1 <= candidate_num <= len(candidate_slots):
                    selected_candidate = candidate_num
                    max_confidence = max(max_confidence, 0.8)
                    break
        
        # 面接形式の判定
        if any(keyword in reply_lower for keyword in ['オンライン', 'zoom', 'teams', 'meet', 'リモート', 'ビデオ']):
            result["interview_format"] = "オンライン"
            max_confidence += 0.1
        elif any(keyword in reply_lower for keyword in ['対面', '現地', '御社', '弊社', '会社', 'オフィス']):
            result["interview_format"] = "対面"
            max_confidence += 0.1
        
        # 確定・承諾の判定
        positive_keywords = [
            '希望', 'お願い', '承知', '了解', '了承', 'ok', 'よろしく', 
            '確定', '決定', '面接', 'で結構', 'で大丈夫', 'で問題ない'
        ]
        
        # 代替案要求の判定
        alternative_keywords = [
            '都合が悪い', '難しい', '別の', '他の', '違う', '変更', 
            '調整', 'もう少し', '後ろ倒し', '前倒し', '別日'
        ]
        
        # 拒否の判定
        rejection_keywords = [
            '見送り', '辞退', 'キャンセル', '取りやめ', '中止', 
            '申し訳', '困難', '無理', '厳しい'
        ]
        
        if selected_candidate and any(keyword in reply_lower for keyword in positive_keywords):
            result["status"] = "confirmed"
            result["selected_slot"] = candidate_slots[selected_candidate - 1]
            result["confidence"] = min(1.0, max_confidence + 0.2)
            
        elif any(keyword in reply_lower for keyword in alternative_keywords):
            result["status"] = "alternative"
            # 代替案の要求テキストを抽出（簡易版）
            result["alternative_request"] = reply_text.strip()
            result["confidence"] = min(1.0, max_confidence + 0.1)
            
        elif any(keyword in reply_lower for keyword in rejection_keywords):
            result["status"] = "rejected"
            result["confidence"] = min(1.0, max_confidence + 0.2)
            
        elif selected_candidate:
            # 候補番号は見つかったが明確な意思表示がない場合
            result["status"] = "confirmed"
            result["selected_slot"] = candidate_slots[selected_candidate - 1]
            result["confidence"] = max_confidence
        
        # 追加要望の抽出（簡易版）
        additional_lines = []
        for line in reply_text.split('\n'):
            line = line.strip()
            if line and not any(keyword in line.lower() for keyword in ['候補', '希望日程', '面接形式']):
                if any(keyword in line.lower() for keyword in ['要望', 'お願い', '質問', '確認', '準備']):
                    additional_lines.append(line)
        
        if additional_lines:
            result["additional_requests"] = '\n'.join(additional_lines)
        
        return result
    
    def simulate_interviewer_reply(self, candidate_slots: List[Dict[str, str]], reply_type: str = "positive") -> str:
        """
        面接官からの返信をシミュレート（テスト用）
        
        Args:
            candidate_slots: 候補日程リスト
            reply_type: "positive" | "alternative" | "rejection"
            
        Returns:
            シミュレートされた返信メール本文
        """
        
        if reply_type == "positive":
            import random
            selected = random.randint(1, len(candidate_slots))
            format_choice = random.choice(["オンライン", "対面"])
            
            replies = [
                f"お疲れ様です。\n候補{selected}でお願いします。\n面接形式は{format_choice}でお願いします。\nよろしくお願いいたします。",
                f"ありがとうございます。\n{selected}番の日程で承知いたします。\n{format_choice}面接でお願いします。",
                f"候補{selected}希望です。\n{format_choice}で実施予定でお願いします。\n当日はよろしくお願いします。"
            ]
            return random.choice(replies)
            
        elif reply_type == "alternative":
            alternatives = [
                "お疲れ様です。\n申し訳ございませんが、提示いただいた日程では都合が悪く、\n1月25日（土）午後または1月27日（月）午前中はいかがでしょうか？",
                "ありがとうございます。\n候補日程ですが、少し調整が必要です。\n来週火曜日以降でご相談できればと思います。",
                "恐れ入りますが、会議と重複してしまい、\n別の日程での調整をお願いできますでしょうか。"
            ]
            import random
            return random.choice(alternatives)
            
        elif reply_type == "rejection":
            rejections = [
                "お疲れ様です。\n申し訳ございませんが、急遽プロジェクトの都合により、\n今回の面接は見送らせていただきます。",
                "ありがとうございます。\n諸事情により、今回の採用プロセスを中止いたします。\n申し訳ございません。"
            ]
            import random
            return random.choice(rejections)
        
        return "返信内容が不明です。"

    def generate_interview_request_email(
        self, 
        seeker_name: str,
        seeker_email: str,
        interviewer_name: str,
        company_name: str,
        position: str,
        candidate_slots: List[Dict[str, str]],
        interview_duration: int = 45
    ) -> Dict[str, str]:
        """
        面接日程調整依頼メールを生成
        
        Args:
            seeker_name: 求職者名
            seeker_email: 求職者メールアドレス  
            interviewer_name: 面接官名
            company_name: 会社名
            position: 職種
            candidate_slots: 候補日程リスト [{"start": "...", "end": "..."}]
            interview_duration: 面接時間（分）
            
        Returns:
            {"subject": "件名", "body": "本文"}
        """
        
        # 候補日程をフォーマット
        formatted_slots = []
        for i, slot in enumerate(candidate_slots, 1):
            start_time = self.format_datetime_japanese(slot["start"])
            formatted_slots.append(f"候補{i}: {start_time}から{interview_duration}分程度")
        
        slots_text = "\n".join(formatted_slots)
        
        subject = f"【面接日程調整】{company_name} {position}ポジション - {seeker_name}様"
        
        body = f"""
{interviewer_name}様

お疲れ様です。
転職支援AIシステムより、面接日程調整のご連絡です。

【応募者情報】
氏名: {seeker_name}様
応募職種: {position}
連絡先: {seeker_email}

【面接日程候補】
以下の候補日程の中から、ご都合の良い日時をお選びください：

{slots_text}

【ご回答方法】
このメールに返信で、以下のようにお答えください：
- 希望日程: 候補○
- 面接形式: オンライン/対面
- その他ご要望: （あれば）

なお、上記候補日程でご都合が合わない場合は、
ご希望の日時をお知らせください。
改めて調整いたします。

よろしくお願いいたします。

---
転職支援AIシステム
自動送信メール
        """.strip()
        
        return {"subject": subject, "body": body}
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        body: str, 
        from_email: str = "ai-recruiter@example.com",
        dry_run: bool = True
    ) -> bool:
        """
        メール送信（実際の送信またはドライラン）
        
        Args:
            to_email: 送信先メールアドレス
            subject: 件名
            body: 本文
            from_email: 送信元メールアドレス
            dry_run: Trueの場合は実際に送信せずコンソール出力のみ
            
        Returns:
            送信成功/失敗
        """
        
        if dry_run:
            print("=" * 60)
            print("📧 メール送信（ドライラン）")
            print("=" * 60)
            print(f"送信先: {to_email}")
            print(f"送信元: {from_email}")
            print(f"件名: {subject}")
            print("-" * 40)
            print(body)
            print("=" * 60)
            return True
        
        try:
            # 実際のメール送信処理
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            if self.username and self.password:
                server.starttls()
                server.login(self.username, self.password)
            
            text = msg.as_string()
            server.sendmail(from_email, to_email, text)
            server.quit()
            
            print(f"✅ メール送信成功: {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ メール送信失敗: {e}")
            return False
    
    def generate_confirmation_email(
        self,
        seeker_name: str,
        interviewer_name: str,
        company_name: str,
        position: str,
        confirmed_slot: Dict[str, str],
        interview_format: str = "オンライン"
    ) -> Dict[str, str]:
        """
        面接確定通知メールを生成
        """
        
        start_time = self.format_datetime_japanese(confirmed_slot["start"])
        end_time = self.format_datetime_japanese(confirmed_slot["end"])
        
        subject = f"【面接確定】{company_name} {position}ポジション - {seeker_name}様"
        
        body = f"""
{seeker_name}様

お疲れ様です。
転職支援AIシステムより、面接日程確定のご連絡です。

【確定した面接予定】
日時: {start_time} 〜 {end_time}
面接官: {interviewer_name}様
形式: {interview_format}
応募職種: {position}

面接前日に詳細なご案内（参加URLや会場情報）を
別途お送りいたします。

当日はよろしくお願いいたします。

---
転職支援AIシステム
自動送信メール
        """.strip()
        
        return {"subject": subject, "body": body} 