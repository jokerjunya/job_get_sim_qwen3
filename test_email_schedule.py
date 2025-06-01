#!/usr/bin/env python3
"""
メール送信機能付き日程調整のテストスクリプト
"""

import json
from agents.job_simulation.schedule_agent import ScheduleAgent
from agents.job_simulation.simulated_interviewer import SimulatedInterviewer

def test_email_scheduling():
    """メール送信機能の統合テスト"""
    print("=== メール送信機能付き日程調整テスト ===")
    
    # テストデータの準備
    seeker_data = {
        "name": "山田太郎",
        "email": "yamada.taro@example.com",
        "availability": [
            {
                "start": "2025-01-20T13:00:00+09:00",
                "end": "2025-01-20T17:00:00+09:00"
            },
            {
                "start": "2025-01-22T14:00:00+09:00",
                "end": "2025-01-22T18:00:00+09:00"
            }
        ]
    }
    
    # パターン1: カレンダー共有対応面接官（自動調整）
    calendar_interviewer = {
        "name": "田中部長",
        "role": "開発部長",
        "email": "tanaka@techsolutions.co.jp",
        "scheduling_method": "calendar",
        "interview_duration": 45,
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
    
    # パターン2: メール調整が必要な面接官
    email_interviewer = {
        "name": "佐藤リーダー",
        "role": "テックリード",
        "email": "sato@webinnovators.com",
        "scheduling_method": "email",
        "interview_duration": 60,
        "availability": None,
        "preferred_times": "平日 9:00-18:00"
    }
    
    print("\n1. カレンダー共有対応面接官との自動調整テスト")
    print("-" * 50)
    
    interviewer1 = SimulatedInterviewer(info=calendar_interviewer)
    result1 = interviewer1.schedule_first_interview(
        seeker_data, 
        company_name="Tech Solutions",
        position="バックエンドエンジニア"
    )
    
    if result1:
        print(f"✅ 自動調整成功: {result1}")
    else:
        print("❌ 自動調整失敗")
    
    print("\n2. メール調整が必要な面接官との半自動調整テスト")
    print("-" * 50)
    
    interviewer2 = SimulatedInterviewer(info=email_interviewer)
    result2 = interviewer2.schedule_first_interview(
        seeker_data,
        company_name="Web Innovators", 
        position="フロントエンドエンジニア"
    )
    
    if result2 is None:
        print("✅ メール送信モード正常動作（返信待ち状態）")
    else:
        print("❌ メール送信モードで予期しない結果")
    
    print("\n3. ScheduleAgentの直接テスト")
    print("-" * 50)
    
    schedule_agent = ScheduleAgent()
    
    # 自動調整テスト
    auto_result = schedule_agent.schedule_interview(
        seeker_data=seeker_data,
        interviewer_info=calendar_interviewer,
        company_name="Tech Solutions",
        position="バックエンドエンジニア"
    )
    print(f"自動調整結果: {auto_result['status']} - {auto_result['message']}")
    
    # メール送信テスト  
    email_result = schedule_agent.schedule_interview(
        seeker_data=seeker_data,
        interviewer_info=email_interviewer,
        company_name="Web Innovators",
        position="フロントエンドエンジニア"
    )
    print(f"メール送信結果: {email_result['status']} - {email_result['message']}")
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    test_email_scheduling() 