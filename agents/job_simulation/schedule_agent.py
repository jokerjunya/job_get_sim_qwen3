from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pytz
from .email_agent import EmailAgent


class ScheduleAgent:
    """
    面接日程調整を行うエージェント
    求職者と面接官の空き時間から最適な面接スロットを見つける
    """
    
    def __init__(self):
        self.timezone = pytz.timezone('Asia/Tokyo')
        self.email_agent = EmailAgent()
        # 進行中の調整案件を管理
        self.pending_schedules = {}  # {request_id: {...}}
    
    def parse_iso_datetime(self, iso_string: str) -> datetime:
        """ISO8601形式の日時文字列をdatetimeオブジェクトに変換"""
        return datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
    
    def find_common_slot(
        self, 
        seeker_avail: List[Dict[str, str]], 
        interviewer_avail: List[Dict[str, str]], 
        interview_minutes: int = 45, 
        buffer_minutes: int = 15
    ) -> Optional[Dict[str, str]]:
        """
        求職者と面接官の空き時間から共通の面接スロットを見つける
        
        Args:
            seeker_avail: 求職者の空き時間リスト [{"start": "...", "end": "..."}]
            interviewer_avail: 面接官の空き時間リスト [{"start": "...", "end": "..."}]
            interview_minutes: 面接時間（分）
            buffer_minutes: バッファ時間（分）
            
        Returns:
            最初に見つかった共通スロット {"start": "...", "end": "..."} または None
        """
        total_minutes = interview_minutes + buffer_minutes
        
        # 求職者の各スロットに対して面接官のスロットとの重複をチェック
        for seeker_slot in seeker_avail:
            seeker_start = self.parse_iso_datetime(seeker_slot["start"])
            seeker_end = self.parse_iso_datetime(seeker_slot["end"])
            
            for interviewer_slot in interviewer_avail:
                interviewer_start = self.parse_iso_datetime(interviewer_slot["start"])
                interviewer_end = self.parse_iso_datetime(interviewer_slot["end"])
                
                # 重複期間の開始と終了を計算
                overlap_start = max(seeker_start, interviewer_start)
                overlap_end = min(seeker_end, interviewer_end)
                
                # 重複期間が必要な時間以上あるかチェック
                if overlap_end > overlap_start:
                    overlap_duration = (overlap_end - overlap_start).total_seconds() / 60
                    
                    if overlap_duration >= total_minutes:
                        # 面接時間のスロットを返す（バッファ時間は含めない）
                        interview_end = overlap_start + timedelta(minutes=interview_minutes)
                        
                        return {
                            "start": overlap_start.isoformat(),
                            "end": interview_end.isoformat()
                        }
        
        return None
    
    def generate_candidate_slots_from_seeker(
        self,
        seeker_avail: List[Dict[str, str]],
        interview_minutes: int = 45,
        max_candidates: int = 3
    ) -> List[Dict[str, str]]:
        """
        求職者の空き時間から面接候補日程を生成
        """
        candidates = []
        
        for slot in seeker_avail:
            seeker_start = self.parse_iso_datetime(slot["start"])
            seeker_end = self.parse_iso_datetime(slot["end"])
            
            # 各スロット内で可能な開始時間を30分間隔で生成
            current_time = seeker_start
            while current_time + timedelta(minutes=interview_minutes) <= seeker_end:
                candidate_end = current_time + timedelta(minutes=interview_minutes)
                
                candidates.append({
                    "start": current_time.isoformat(),
                    "end": candidate_end.isoformat()
                })
                
                # 30分ずらす
                current_time += timedelta(minutes=30)
                
                if len(candidates) >= max_candidates:
                    break
            
            if len(candidates) >= max_candidates:
                break
        
        return candidates[:max_candidates]
    
    def generate_request_id(self, seeker_name: str, interviewer_name: str) -> str:
        """調整リクエストIDを生成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"req_{seeker_name}_{interviewer_name}_{timestamp}"
    
    def process_interview_reply(
        self,
        request_id: str,
        reply_text: str
    ) -> Dict:
        """
        面接官からの返信を処理して面接を確定
        
        Args:
            request_id: 調整リクエストID
            reply_text: 返信メール本文
            
        Returns:
            {
                "status": "confirmed" | "alternative_needed" | "rejected" | "unclear",
                "confirmed_slot": {...} | None,
                "interview_format": str | None,
                "message": str,
                "confidence": float
            }
        """
        
        if request_id not in self.pending_schedules:
            return {
                "status": "error",
                "message": f"リクエストID {request_id} が見つかりません",
                "confidence": 0.0
            }
        
        pending_info = self.pending_schedules[request_id]
        candidate_slots = pending_info["candidate_slots"]
        
        # 返信解析
        parse_result = self.email_agent.parse_interview_reply(reply_text, candidate_slots)
        
        result = {
            "status": parse_result["status"],
            "confirmed_slot": None,
            "interview_format": parse_result["interview_format"],
            "message": "",
            "confidence": parse_result["confidence"]
        }
        
        if parse_result["status"] == "confirmed":
            result["confirmed_slot"] = parse_result["selected_slot"]
            result["message"] = f"面接確定: {self.email_agent.format_datetime_japanese(parse_result['selected_slot']['start'])}"
            
            # 確定通知メールを生成・送信
            self._send_confirmation_emails(request_id, parse_result)
            
            # pending_schedulesから削除
            del self.pending_schedules[request_id]
            
        elif parse_result["status"] == "alternative":
            result["status"] = "alternative_needed"
            result["message"] = f"代替案要求: {parse_result['alternative_request'][:50]}..."
            
        elif parse_result["status"] == "rejected":
            result["message"] = "面接辞退/中止"
            # pending_schedulesから削除
            del self.pending_schedules[request_id]
            
        else:
            result["status"] = "unclear"
            result["message"] = f"返信内容が不明確です（信頼度: {parse_result['confidence']:.2f}）"
        
        return result
    
    def _send_confirmation_emails(self, request_id: str, parse_result: Dict):
        """面接確定後の通知メール送信"""
        pending_info = self.pending_schedules[request_id]
        
        # 求職者への確定通知
        confirmation_email = self.email_agent.generate_confirmation_email(
            seeker_name=pending_info["seeker_name"],
            interviewer_name=pending_info["interviewer_name"],
            company_name=pending_info["company_name"],
            position=pending_info["position"],
            confirmed_slot=parse_result["selected_slot"],
            interview_format=parse_result["interview_format"] or "オンライン"
        )
        
        print("📧 求職者への確定通知メール:")
        self.email_agent.send_email(
            to_email=pending_info["seeker_email"],
            subject=confirmation_email["subject"],
            body=confirmation_email["body"],
            dry_run=True
        )
    
    def schedule_interview(
        self,
        seeker_data: dict,
        interviewer_info: dict,
        company_name: str = "",
        position: str = ""
    ) -> dict:
        """
        面接日程調整のメイン処理
        interviewer_infoのscheduling_methodに応じて完全自動またはメール送信を選択
        
        Returns:
            {
                "status": "auto_scheduled" | "email_sent" | "failed",
                "scheduled_slot": {...} | None,
                "email_info": {...} | None,
                "message": "...",
                "request_id": str | None  # メール送信時のリクエストID
            }
        """
        
        scheduling_method = interviewer_info.get("scheduling_method", "calendar")
        seeker_name = seeker_data.get("name", "求職者")
        seeker_email = seeker_data.get("email", "seeker@example.com")
        interviewer_name = interviewer_info.get("name", "面接官")
        interviewer_email = interviewer_info.get("email", "interviewer@example.com")
        interview_duration = interviewer_info.get("interview_duration", 45)
        
        if scheduling_method == "calendar":
            # 完全自動調整（既存の処理）
            seeker_availability = seeker_data.get("availability", [])
            interviewer_availability = interviewer_info.get("availability", [])
            
            if not interviewer_availability:
                return {
                    "status": "failed",
                    "message": f"面接官（{interviewer_name}）のカレンダー情報が利用できません"
                }
            
            scheduled_slot = self.find_common_slot(
                seeker_availability,
                interviewer_availability,
                interview_minutes=interview_duration
            )
            
            if scheduled_slot:
                schedule_info = self.format_schedule_info(
                    scheduled_slot,
                    seeker_name,
                    interviewer_name
                )
                print(schedule_info)
                print("=" * 50)
                
                return {
                    "status": "auto_scheduled",
                    "scheduled_slot": scheduled_slot,
                    "message": f"自動調整成功: {seeker_name} × {interviewer_name}"
                }
            else:
                return {
                    "status": "failed",
                    "message": f"共通の空き時間が見つかりませんでした"
                }
        
        elif scheduling_method == "email":
            # メール送信による半自動調整
            seeker_availability = seeker_data.get("availability", [])
            
            if not seeker_availability:
                return {
                    "status": "failed",
                    "message": f"求職者（{seeker_name}）の空き時間情報がありません"
                }
            
            # 求職者の空き時間から候補日程を生成
            candidate_slots = self.generate_candidate_slots_from_seeker(
                seeker_availability,
                interview_minutes=interview_duration,
                max_candidates=3
            )
            
            if not candidate_slots:
                return {
                    "status": "failed",
                    "message": f"候補日程を生成できませんでした"
                }
            
            # リクエストIDを生成して進行中案件に登録
            request_id = self.generate_request_id(seeker_name, interviewer_name)
            self.pending_schedules[request_id] = {
                "seeker_name": seeker_name,
                "seeker_email": seeker_email,
                "interviewer_name": interviewer_name,
                "interviewer_email": interviewer_email,
                "company_name": company_name,
                "position": position,
                "candidate_slots": candidate_slots,
                "created_at": datetime.now().isoformat()
            }
            
            # メール生成・送信
            email_content = self.email_agent.generate_interview_request_email(
                seeker_name=seeker_name,
                seeker_email=seeker_email,
                interviewer_name=interviewer_name,
                company_name=company_name,
                position=position,
                candidate_slots=candidate_slots,
                interview_duration=interview_duration
            )
            
            # ドライラン送信
            success = self.email_agent.send_email(
                to_email=interviewer_email,
                subject=email_content["subject"],
                body=email_content["body"],
                dry_run=True  # とりあえずドライラン
            )
            
            if success:
                return {
                    "status": "email_sent",
                    "candidate_slots": candidate_slots,
                    "email_info": {
                        "to": interviewer_email,
                        "subject": email_content["subject"],
                        "body": email_content["body"]
                    },
                    "message": f"メール送信成功: {interviewer_name}様への日程調整依頼",
                    "request_id": request_id
                }
            else:
                # 失敗時はpending_schedulesから削除
                del self.pending_schedules[request_id]
                return {
                    "status": "failed",
                    "message": f"メール送信に失敗しました"
                }
        
        else:
            return {
                "status": "failed",
                "message": f"未対応の調整方式: {scheduling_method}"
            }
    
    def format_schedule_info(self, schedule: Dict[str, str], seeker_name: str, interviewer_name: str) -> str:
        """
        スケジュール情報を読みやすい形式でフォーマット
        """
        start_dt = self.parse_iso_datetime(schedule["start"])
        end_dt = self.parse_iso_datetime(schedule["end"])
        
        # 日本時間での表示
        start_jst = start_dt.astimezone(self.timezone)
        end_jst = end_dt.astimezone(self.timezone)
        
        date_str = start_jst.strftime("%Y年%m月%d日")
        start_time = start_jst.strftime("%H:%M")
        end_time = end_jst.strftime("%H:%M")
        
        return f"📅 面接日程調整完了\n" \
               f"日時: {date_str} {start_time}〜{end_time}\n" \
               f"求職者: {seeker_name}\n" \
               f"面接官: {interviewer_name}"
    
    def check_schedule_conflict(self, schedule1: Dict[str, str], schedule2: Dict[str, str]) -> bool:
        """
        2つのスケジュールが重複しているかチェック
        """
        start1 = self.parse_iso_datetime(schedule1["start"])
        end1 = self.parse_iso_datetime(schedule1["end"])
        start2 = self.parse_iso_datetime(schedule2["start"])
        end2 = self.parse_iso_datetime(schedule2["end"])
        
        # 重複チェック：一方の開始時刻が他方の終了時刻より前で、かつ一方の終了時刻が他方の開始時刻より後
        return start1 < end2 and end1 > start2 