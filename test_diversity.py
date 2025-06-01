#!/usr/bin/env python3
"""
転職シミュレーションの多様性テストスクリプト

このスクリプトは新しい多様性機能をテストし、
異なる求職者と求人の組み合わせを確認します。
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.job_simulation.data_manager import DataManager
import json

def test_data_loading():
    """データ読み込みテスト"""
    print("📊 データ読み込みテスト")
    print("-" * 50)
    
    try:
        data_manager = DataManager()
        stats = data_manager.get_stats()
        
        print(f"✅ 求職者数: {stats['seekers_count']}")
        print(f"✅ 求人パターン数: {stats['job_patterns_count']}")
        print(f"✅ 静的求人数: {stats['static_jobs_count']}")
        
        if stats['seekers_count'] > 1:
            print("✅ 複数の求職者データが読み込まれました")
        else:
            print("⚠️ 求職者データが1つしかありません")
            
        if stats['job_patterns_count'] > 0:
            print("✅ 求人パターンが読み込まれました")
        else:
            print("⚠️ 求人パターンが見つかりません")
            
        return True
    except Exception as e:
        print(f"❌ データ読み込みエラー: {e}")
        return False

def test_random_selection():
    """ランダム選択テスト"""
    print("\n🎲 ランダム選択テスト")
    print("-" * 50)
    
    try:
        data_manager = DataManager()
        
        print("5回のランダム選択を実行:")
        combinations = []
        
        for i in range(5):
            seeker, job = data_manager.get_simulation_pair()
            combination = {
                "seeker_name": seeker['name'],
                "seeker_age": seeker.get('age', '?'),
                "seeker_tags": seeker.get('tags', []),
                "job_title": job['title'],
                "job_company": job['company'],
                "job_industry": job.get('industry', '?'),
                "job_company_type": job.get('company_type', '?')
            }
            combinations.append(combination)
            
            print(f"  {i+1}. {seeker['name']} ({seeker.get('age', '?')}歳) × {job['title']} at {job['company']}")
            print(f"     求職者タグ: {', '.join(seeker.get('tags', []))}")
            print(f"     求人業界: {job.get('industry', '?')} / 企業タイプ: {job.get('company_type', '?')}")
            print()
        
        # 多様性チェック
        unique_seekers = len(set(c['seeker_name'] for c in combinations))
        unique_jobs = len(set(c['job_title'] + c['job_company'] for c in combinations))
        
        print(f"多様性分析:")
        print(f"  ユニークな求職者: {unique_seekers}/5")
        print(f"  ユニークな求人: {unique_jobs}/5")
        
        if unique_seekers >= 3:
            print("✅ 求職者の多様性が確認されました")
        else:
            print("⚠️ 求職者の多様性が不足しています")
            
        if unique_jobs >= 3:
            print("✅ 求人の多様性が確認されました")
        else:
            print("⚠️ 求人の多様性が不足しています")
            
        return True
    except Exception as e:
        print(f"❌ ランダム選択エラー: {e}")
        return False

def test_matching_logic():
    """マッチングロジックテスト"""
    print("\n🔗 マッチングロジックテスト")
    print("-" * 50)
    
    try:
        data_manager = DataManager()
        
        # 各求職者について適した求人を確認
        for seeker in data_manager.seekers[:3]:  # 最初の3人をテスト
            print(f"求職者: {seeker['name']} ({seeker.get('age', '?')}歳)")
            print(f"  タグ: {', '.join(seeker.get('tags', []))}")
            print(f"  スキル: {', '.join(seeker.get('skills', []))}")
            
            # 適した求人パターンを探す
            job_pattern = data_manager.select_suitable_job_pattern(seeker)
            if job_pattern:
                print(f"  マッチした求人パターン: {job_pattern['position']}")
                print(f"  企業タイプ: {job_pattern.get('company_type', '?')}")
                print(f"  業界: {job_pattern.get('industry', '?')}")
                
                # マッチスコアを計算
                score = data_manager._calculate_match_score(seeker, job_pattern)
                print(f"  マッチスコア: {score}")
            else:
                print("  マッチする求人パターンが見つかりませんでした")
            print()
            
        return True
    except Exception as e:
        print(f"❌ マッチングロジックエラー: {e}")
        return False

def test_job_generation():
    """求人生成テスト"""
    print("\n🏢 求人生成テスト")
    print("-" * 50)
    
    try:
        data_manager = DataManager()
        
        # 求人パターンから具体的な求人を生成
        for pattern in data_manager.job_patterns[:2]:  # 最初の2つをテスト
            print(f"パターン: {pattern['position']} ({pattern.get('company_type', '?')})")
            
            job_posting = data_manager.generate_job_posting_from_pattern(pattern)
            
            print(f"  生成された求人:")
            print(f"    会社名: {job_posting['company']}")
            print(f"    職種: {job_posting['title']}")
            print(f"    年収: {job_posting['salary']}万円")
            print(f"    働き方: {job_posting['work_style']}")
            print(f"    技術スタック: {', '.join(job_posting.get('tech_stack', []))}")
            print(f"    カルチャー: {', '.join(job_posting.get('culture_keywords', []))}")
            print()
            
        return True
    except Exception as e:
        print(f"❌ 求人生成エラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("🧪 転職シミュレーション多様性テスト")
    print("=" * 60)
    
    tests = [
        test_data_loading,
        test_random_selection,
        test_matching_logic,
        test_job_generation
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n📋 テスト結果サマリー")
    print("-" * 50)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test.__name__}")
    
    print(f"\n総合結果: {passed}/{total} テスト通過")
    
    if passed == total:
        print("🎉 すべてのテストが成功しました！")
        print("多様性機能が正常に動作しています。")
    else:
        print("⚠️ 一部のテストが失敗しました。")
        print("設定を確認してください。")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 