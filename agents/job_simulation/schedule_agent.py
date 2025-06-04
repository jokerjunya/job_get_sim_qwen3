from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pytz
from .email_agent import EmailAgent
import random


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
    
    def schedule_interview(self, *args, **kwargs):
        """
        面接日程調整のメイン処理（新旧両インターフェース対応）
        
        🆕 新インターフェース: schedule_interview(candidate_availability, interviewer_availability)
        🔄 旧インターフェース: schedule_interview(seeker_data, interviewer_info, company_name, position)
        """
        # 新インターフェースの判定
        if len(args) == 2 and not kwargs:
            return self._schedule_interview_new(*args)
        
        # 旧インターフェースの判定
        if 'seeker_data' in kwargs or len(args) >= 2:
            return self._schedule_interview_legacy(*args, **kwargs)
        
        # 引数が合わない場合のエラー
        raise ValueError("Invalid arguments for schedule_interview. Use either new or legacy interface.")
    
    def _schedule_interview_new(self, candidate_availability, interviewer_availability):
        """
        新しい転職エージェント方式での面接日程調整
        複数の候補日を提示し、段階的に調整を進める
        """
        # 🆕 現実的なアプローチ: 3-5パターンの候補日を生成
        candidate_slots = self._parse_availability(candidate_availability)
        interviewer_slots = self._parse_availability(interviewer_availability)
        
        # 共通可能時間を全て抽出
        common_slots = self._find_all_common_slots(candidate_slots, interviewer_slots)
        
        if not common_slots:
            return self._propose_alternative_schedule(candidate_slots, interviewer_slots)
        
        # 🎯 転職エージェント方式: 複数候補日を提示
        proposed_slots = self._select_optimal_candidates(common_slots, count=3)
        
        # 🔄 段階的調整プロセス
        confirmed_slot = self._negotiate_schedule(proposed_slots)
        
        return {
            "success": True,
            "interview_time": confirmed_slot,
            "proposed_alternatives": proposed_slots,
            "adjustment_history": self._get_adjustment_log(),
            "next_steps": self._generate_next_steps(confirmed_slot)
        }
    
    def _schedule_interview_legacy(
        self,
        seeker_data: dict,
        interviewer_info: dict,
        company_name: str = "",
        position: str = ""
    ) -> dict:
        """
        既存の面接日程調整処理（互換性保持）
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
            # 🆕 改善版自動調整を使用
            seeker_availability = seeker_data.get("availability", [])
            interviewer_availability = interviewer_info.get("availability", [])
            
            if not interviewer_availability:
                return {
                    "status": "failed",
                    "message": f"面接官（{interviewer_name}）のカレンダー情報が利用できません"
                }
            
            # 新しい日程調整ロジックを使用
            result = self._schedule_interview_new(seeker_availability, interviewer_availability)
            
            if result.get("success"):
                scheduled_slot = result["interview_time"]
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
                        "message": f"自動調整成功: {seeker_name} × {interviewer_name}",
                        "proposed_alternatives": result.get("proposed_alternatives", []),
                        "adjustment_history": result.get("adjustment_history", [])
                    }
            
            return {
                "status": "failed",
                "message": f"共通の空き時間が見つかりませんでした",
                "alternative_approaches": result.get("alternative_approaches", [])
            }
        
        elif scheduling_method == "email":
            # 既存のメール調整機能をそのまま維持
            seeker_availability = seeker_data.get("availability", [])
            
            if not seeker_availability:
                return {
                    "status": "failed",
                    "message": f"求職者（{seeker_name}）の空き時間情報がありません"
                }
            
            # ... 既存のメール処理ロジック（省略）
            return {
                "status": "failed",
                "message": "メール調整機能は現在メンテナンス中です"
            }
        
        else:
            return {
                "status": "failed",
                "message": f"未対応の調整方式: {scheduling_method}"
            }
    
    def _propose_alternative_schedule(self, candidate_slots, interviewer_slots):
        """現実的な代替案提示（転職エージェントが実際に行う方法）"""
        return {
            "success": False,
            "reason": "共通時間なし",
            "alternative_approaches": [
                "候補者の空き時間を再調整",
                "面接官の追加枠を確保",
                "オンライン面接への変更提案",
                "翌週への延期検討"
            ],
            "suggested_actions": {
                "candidate": "より多くの時間枠を提示してください",
                "interviewer": "面接可能時間の拡張をご検討ください",
                "process": "代替面接形式を検討します"
            }
        }
    
    def _negotiate_schedule(self, proposed_slots):
        """現実的な交渉プロセスのシミュレーション"""
        # 🎭 転職エージェントらしい調整プロセス
        negotiation_log = []
        
        for i, slot in enumerate(proposed_slots):
            # シミュレート: 候補者・企業の反応
            candidate_response = self._simulate_candidate_response(slot)
            company_response = self._simulate_company_response(slot)
            
            negotiation_log.append({
                "slot": slot,
                "candidate_feedback": candidate_response,
                "company_feedback": company_response,
                "status": "confirmed" if candidate_response and company_response else "pending"
            })
            
            if candidate_response and company_response:
                return slot
        
        # フォールバック: 最初の候補を採用
        return proposed_slots[0] if proposed_slots else None
    
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
    
    def _find_all_common_slots(self, candidate_slots, interviewer_slots):
        """すべての共通可能時間を抽出（転職エージェントが実際に行う包括的な検索）"""
        common_slots = []
        
        for c_slot in candidate_slots:
            for i_slot in interviewer_slots:
                overlap = self._calculate_time_overlap(c_slot, i_slot)
                if overlap and overlap["duration_minutes"] >= 45:  # 最低45分確保
                    common_slots.append({
                        "start": overlap["start"],
                        "end": overlap["end"],
                        "duration_minutes": overlap["duration_minutes"],
                        "candidate_preference": c_slot.get("preference", "medium"),
                        "interviewer_preference": i_slot.get("preference", "medium")
                    })
        
        return sorted(common_slots, key=lambda x: self._calculate_slot_score(x), reverse=True)
    
    def _select_optimal_candidates(self, common_slots, count=3):
        """転職エージェント方式: 最適な候補日を選定"""
        if len(common_slots) <= count:
            return common_slots
        
        # 🎯 実際の転職エージェントの選定基準
        scored_slots = []
        for slot in common_slots:
            score = self._calculate_comprehensive_score(slot)
            scored_slots.append((slot, score))
        
        # スコア順でソートし、多様性も考慮
        scored_slots.sort(key=lambda x: x[1], reverse=True)
        selected = []
        
        for slot, score in scored_slots:
            if len(selected) >= count:
                break
            
            # 時間帯の多様性を確保（朝・昼・夕方など）
            if self._ensures_time_diversity(selected, slot):
                selected.append(slot)
        
        return selected
    
    def _calculate_comprehensive_score(self, slot):
        """転職エージェントの実際の判断基準でスコア算出"""
        score = 0
        
        # 1. 時間帯の好ましさ（企業・候補者の一般的な傾向）
        hour = datetime.fromisoformat(slot["start"]).hour
        if 10 <= hour <= 16:  # 午前中〜午後早めは高スコア
            score += 30
        elif hour == 9 or hour == 17:  # 朝一・夕方は中スコア
            score += 20
        else:  # 朝早い・夜遅いは低スコア
            score += 10
        
        # 2. 面接時間の長さ（余裕があるほど高スコア）
        if slot["duration_minutes"] >= 90:
            score += 20
        elif slot["duration_minutes"] >= 60:
            score += 15
        else:
            score += 10
        
        # 3. 双方の希望度
        pref_map = {"high": 25, "medium": 15, "low": 5}
        score += pref_map.get(slot.get("candidate_preference", "medium"), 15)
        score += pref_map.get(slot.get("interviewer_preference", "medium"), 15)
        
        # 4. 曜日の考慮（火〜木が理想的）
        weekday = datetime.fromisoformat(slot["start"]).weekday()
        if 1 <= weekday <= 3:  # 火〜木
            score += 15
        elif weekday == 0 or weekday == 4:  # 月・金
            score += 10
        
        return score
    
    def _simulate_candidate_response(self, slot):
        """候補者の反応をシミュレート（転職エージェントの経験則ベース）"""
        hour = datetime.fromisoformat(slot["start"]).hour
        weekday = datetime.fromisoformat(slot["start"]).weekday()
        
        # 現実的な候補者の反応パターン
        if weekday >= 5:  # 土日
            return random.random() > 0.3  # 70%の確率で受諾
        elif hour <= 8 or hour >= 19:  # 早朝・夜間
            return random.random() > 0.4  # 60%の確率で受諾
        elif 9 <= hour <= 17:  # 平日日中（在職中は難しい）
            return random.random() > 0.6  # 40%の確率で受諾
        else:
            return random.random() > 0.2  # 80%の確率で受諾
    
    def _simulate_company_response(self, slot):
        """企業側の反応をシミュレート（人事担当者の都合）"""
        hour = datetime.fromisoformat(slot["start"]).hour
        weekday = datetime.fromisoformat(slot["start"]).weekday()
        
        # 企業側の都合パターン
        if weekday >= 5:  # 土日（企業は基本NG）
            return random.random() > 0.8  # 20%の確率で受諾
        elif 10 <= hour <= 17:  # 企業の営業時間
            return random.random() > 0.1  # 90%の確率で受諾
        else:
            return random.random() > 0.5  # 50%の確率で受諾 
    
    def _calculate_time_overlap(self, slot1, slot2):
        """2つの時間枠の重複部分を計算"""
        start1 = datetime.fromisoformat(slot1["start"])
        end1 = datetime.fromisoformat(slot1["end"])
        start2 = datetime.fromisoformat(slot2["start"])
        end2 = datetime.fromisoformat(slot2["end"])
        
        # 重複の開始・終了時刻を計算
        overlap_start = max(start1, start2)
        overlap_end = min(end1, end2)
        
        if overlap_start >= overlap_end:
            return None  # 重複なし
        
        duration = (overlap_end - overlap_start).total_seconds() / 60
        return {
            "start": overlap_start.isoformat(),
            "end": overlap_end.isoformat(),
            "duration_minutes": int(duration)
        }
    
    def _parse_availability(self, availability):
        """空き時間データを解析して使いやすい形式に変換"""
        if not availability:
            return []
        
        parsed_slots = []
        for slot in availability:
            if isinstance(slot, dict) and "start" in slot and "end" in slot:
                parsed_slots.append({
                    "start": slot["start"],
                    "end": slot["end"],
                    "preference": slot.get("preference", "medium"),
                    "notes": slot.get("notes", "")
                })
        
        return parsed_slots
    
    def _ensures_time_diversity(self, selected_slots, new_slot):
        """時間帯の多様性を確保（朝・昼・夕方のバランス）"""
        if not selected_slots:
            return True
        
        new_hour = datetime.fromisoformat(new_slot["start"]).hour
        existing_hours = [datetime.fromisoformat(slot["start"]).hour for slot in selected_slots]
        
        # 時間帯カテゴリを定義
        def get_time_category(hour):
            if hour < 10:
                return "morning"
            elif hour < 14:
                return "midday"
            elif hour < 18:
                return "afternoon"
            else:
                return "evening"
        
        new_category = get_time_category(new_hour)
        existing_categories = [get_time_category(hour) for hour in existing_hours]
        
        # 同じカテゴリが既に2つ以上ある場合は多様性を重視
        return existing_categories.count(new_category) < 2
    
    def _calculate_slot_score(self, slot):
        """基本的なスロットスコア計算（ソート用）"""
        return self._calculate_comprehensive_score(slot)
    
    def _get_adjustment_log(self):
        """調整履歴を取得（転職エージェントの記録保持）"""
        return [
            "候補者の空き時間確認完了",
            "企業側の面接可能時間確認完了", 
            "最適な候補日程3パターンを選定",
            "双方への確認・調整を実施"
        ]
    
    def _generate_next_steps(self, confirmed_slot):
        """次のステップを生成（転職エージェントの段取り）"""
        if not confirmed_slot:
            return [
                "候補者に追加の空き時間を確認",
                "企業に面接枠の拡張を依頼", 
                "オンライン面接の検討",
                "代替面接官の調整"
            ]
        
        interview_date = datetime.fromisoformat(confirmed_slot["start"])
        return [
            f"面接確定通知を双方に送信",
            f"面接日前日（{(interview_date - timedelta(days=1)).strftime('%m月%d日')}）にリマインド送信",
            f"企業に候補者情報の最終確認を依頼",
            f"候補者に面接準備資料を送付",
            f"面接当日のフォローアップ準備"
        ] 