#!/usr/bin/env python3
"""
メール返信解析機能のテストスクリプト
"""

import json
from agents.job_simulation.schedule_agent import ScheduleAgent
from agents.job_simulation.email_agent import EmailAgent

def test_reply_analysis():
    """メール返信解析機能の統合テスト"""
    print("=== メール返信解析機能テスト ===")
    
    # テスト用の候補日程
    candidate_slots = [
        {
            "start": "2025-01-20T13:00:00+09:00",
            "end": "2025-01-20T14:00:00+09:00"
        },
        {
            "start": "2025-01-20T13:30:00+09:00",
            "end": "2025-01-20T14:30:00+09:00"
        },
        {
            "start": "2025-01-20T14:00:00+09:00",
            "end": "2025-01-20T15:00:00+09:00"
        }
    ]
    
    email_agent = EmailAgent()
    
    print("\n1. 面接官返信のシミュレーション・テスト")
    print("-" * 50)
    
    # パターン1: 承諾返信
    print("【パターン1: 承諾返信】")
    positive_reply = email_agent.simulate_interviewer_reply(candidate_slots, "positive")
    print("シミュレート返信:")
    print(positive_reply)
    print()
    
    parse_result = email_agent.parse_interview_reply(positive_reply, candidate_slots)
    print("解析結果:")
    print(f"  ステータス: {parse_result['status']}")
    print(f"  選択候補: {parse_result['selected_slot']}")
    print(f"  面接形式: {parse_result['interview_format']}")
    print(f"  信頼度: {parse_result['confidence']:.2f}")
    print()
    
    # パターン2: 代替案要求
    print("【パターン2: 代替案要求】")
    alternative_reply = email_agent.simulate_interviewer_reply(candidate_slots, "alternative")
    print("シミュレート返信:")
    print(alternative_reply)
    print()
    
    parse_result = email_agent.parse_interview_reply(alternative_reply, candidate_slots)
    print("解析結果:")
    print(f"  ステータス: {parse_result['status']}")
    print(f"  代替要求: {parse_result['alternative_request'][:100]}...")
    print(f"  信頼度: {parse_result['confidence']:.2f}")
    print()
    
    # パターン3: 拒否・辞退
    print("【パターン3: 拒否・辞退】")
    rejection_reply = email_agent.simulate_interviewer_reply(candidate_slots, "rejection")
    print("シミュレート返信:")
    print(rejection_reply)
    print()
    
    parse_result = email_agent.parse_interview_reply(rejection_reply, candidate_slots)
    print("解析結果:")
    print(f"  ステータス: {parse_result['status']}")
    print(f"  信頼度: {parse_result['confidence']:.2f}")
    print()
    
    print("\n2. 手動テストケース")
    print("-" * 50)
    
    test_cases = [
        {
            "name": "明確な候補1指定",
            "reply": "お疲れ様です。候補1でお願いします。オンライン面接でお願いします。"
        },
        {
            "name": "候補2希望（対面）",
            "reply": "ありがとうございます。2番の日程で承知いたします。対面面接でお願いします。"
        },
        {
            "name": "候補3希望（簡潔）",
            "reply": "3希望です。Zoomでお願いします。"
        },
        {
            "name": "曖昧な表現",
            "reply": "検討します。後ほど連絡いたします。"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"【テストケース{i}: {test_case['name']}】")
        print(f"返信内容: {test_case['reply']}")
        
        parse_result = email_agent.parse_interview_reply(test_case['reply'], candidate_slots)
        print(f"解析結果: {parse_result['status']} (信頼度: {parse_result['confidence']:.2f})")
        if parse_result['selected_slot']:
            slot = parse_result['selected_slot']
            print(f"選択日程: {email_agent.format_datetime_japanese(slot['start'])}")
        if parse_result['interview_format']:
            print(f"面接形式: {parse_result['interview_format']}")
        print()
    
    print("\n3. ScheduleAgentの統合テスト")
    print("-" * 50)
    
    schedule_agent = ScheduleAgent()
    
    # まず、メール送信を実行してリクエストIDを取得
    seeker_data = {
        "name": "山田太郎",
        "email": "yamada.taro@example.com",
        "availability": [
            {
                "start": "2025-01-20T13:00:00+09:00",
                "end": "2025-01-20T17:00:00+09:00"
            }
        ]
    }
    
    email_interviewer = {
        "name": "佐藤リーダー",
        "role": "テックリード",
        "email": "sato@webinnovators.com",
        "scheduling_method": "email",
        "interview_duration": 60
    }
    
    print("【メール送信】")
    email_result = schedule_agent.schedule_interview(
        seeker_data=seeker_data,
        interviewer_info=email_interviewer,
        company_name="Web Innovators",
        position="フロントエンドエンジニア"
    )
    
    if email_result["status"] == "email_sent":
        request_id = email_result["request_id"]
        print(f"✅ メール送信成功 (リクエストID: {request_id})")
        
        # 承諾返信をシミュレート
        print("\n【面接官からの承諾返信をシミュレート】")
        simulated_reply = email_agent.simulate_interviewer_reply(
            email_result["candidate_slots"], 
            "positive"
        )
        print("シミュレート返信:")
        print(simulated_reply)
        print()
        
        # 返信処理
        print("【返信処理】")
        reply_result = schedule_agent.process_interview_reply(request_id, simulated_reply)
        print(f"処理結果: {reply_result['status']} - {reply_result['message']}")
        print(f"信頼度: {reply_result['confidence']:.2f}")
        
        if reply_result['confirmed_slot']:
            slot = reply_result['confirmed_slot']
            print(f"確定日程: {email_agent.format_datetime_japanese(slot['start'])}")
        
        if reply_result['interview_format']:
            print(f"面接形式: {reply_result['interview_format']}")
        
    else:
        print("❌ メール送信失敗")
    
    print("\n=== テスト完了 ===")

if __name__ == "__main__":
    test_reply_analysis() 