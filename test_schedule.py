#!/usr/bin/env python3
"""
日程調整機能のテストスクリプト
"""

import json
from agents.job_simulation.schedule_agent import ScheduleAgent
from agents.job_simulation.simulated_interviewer import SimulatedInterviewer

def test_schedule_functionality():
    """日程調整機能の基本テスト"""
    print("=== 日程調整機能テスト ===")
    
    # テストデータの設定
    seeker_availability = [
        {
            "start": "2025-01-20T13:00:00+09:00",
            "end": "2025-01-20T17:00:00+09:00"
        },
        {
            "start": "2025-01-22T14:00:00+09:00",
            "end": "2025-01-22T18:00:00+09:00"
        }
    ]
    
    interviewer_availability = [
        {
            "start": "2025-01-20T14:00:00+09:00",
            "end": "2025-01-20T18:00:00+09:00"
        },
        {
            "start": "2025-01-22T10:00:00+09:00",
            "end": "2025-01-22T16:00:00+09:00"
        }
    ]
    
    # ScheduleAgentのテスト
    print("1. ScheduleAgentの基本機能テスト")
    schedule_agent = ScheduleAgent()
    
    # 共通スロットの検索
    common_slot = schedule_agent.find_common_slot(
        seeker_availability, 
        interviewer_availability
    )
    
    if common_slot:
        print(f"✅ 共通スロット発見: {common_slot}")
        
        # スケジュール情報のフォーマット
        formatted_info = schedule_agent.format_schedule_info(
            common_slot, 
            "山田太郎", 
            "田中部長"
        )
        print(f"✅ フォーマット済み情報:\n{formatted_info}")
    else:
        print("❌ 共通スロットが見つかりませんでした")
    
    # SimulatedInterviewerのテスト
    print("\n2. SimulatedInterviewerの日程調整機能テスト")
    
    interviewer_info = {
        "name": "田中部長",
        "role": "開発部長",
        "availability": interviewer_availability
    }
    
    interviewer = SimulatedInterviewer(info=interviewer_info)
    
    seeker_data = {
        "name": "山田太郎",
        "availability": seeker_availability
    }
    
    # 面接日程調整のテスト
    result = interviewer.schedule_first_interview(seeker_data)
    
    if result:
        print(f"✅ 面接日程調整成功: {result}")
    else:
        print("❌ 面接日程調整失敗")
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    test_schedule_functionality() 