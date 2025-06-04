import json
import random
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import pytz

class DataManager:
    """求職者と求人データの管理・選択を行うクラス"""
    
    def __init__(self):
        self.seekers = self._load_seekers()
        self.job_patterns = self._load_job_patterns()
        self.static_jobs = self._load_static_jobs()
    
    def _load_seekers(self) -> List[Dict]:
        """求職者データを読み込み"""
        seekers = []
        
        # 既存の山田太郎データ
        try:
            with open('data/seekers.json', encoding='utf-8') as f:
                original_seekers = json.load(f)
                seekers.extend(original_seekers)
        except FileNotFoundError:
            pass
        
        # 新しい多様な求職者データ
        try:
            with open('data/seekers_patterns.json', encoding='utf-8') as f:
                pattern_seekers = json.load(f)
                seekers.extend(pattern_seekers)
        except FileNotFoundError:
            pass
            
        return seekers
    
    def _load_job_patterns(self) -> List[Dict]:
        """求人パターンを読み込み"""
        try:
            with open('data/job_patterns.json', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def _load_static_jobs(self) -> List[Dict]:
        """既存の静的求人データを読み込み"""
        try:
            with open('data/jobs.json', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def select_random_seeker(self) -> Dict:
        """ランダムに求職者を選択"""
        if not self.seekers:
            raise ValueError("求職者データが見つかりません")
        return random.choice(self.seekers)
    
    def select_suitable_job_pattern(self, seeker: Dict) -> Optional[Dict]:
        """求職者に適した求人パターンを選択"""
        if not self.job_patterns:
            return None
            
        # 求職者の特性に基づいてマッチング
        suitable_patterns = []
        seeker_tags = seeker.get('tags', [])
        seeker_values = seeker.get('values', [])
        seeker_skills = seeker.get('skills', [])
        
        for pattern in self.job_patterns:
            score = self._calculate_match_score(seeker, pattern)
            if score > 0:
                suitable_patterns.append((pattern, score))
        
        if suitable_patterns:
            # スコアによる重み付き選択
            suitable_patterns.sort(key=lambda x: x[1], reverse=True)
            # 上位50%からランダム選択（完全にランダムではなく、ある程度マッチングを考慮）
            top_half = suitable_patterns[:max(1, len(suitable_patterns)//2)]
            return random.choice(top_half)[0]
        
        # マッチしない場合はランダム選択
        return random.choice(self.job_patterns)
    
    def _calculate_match_score(self, seeker: Dict, job_pattern: Dict) -> int:
        """求職者と求人パターンのマッチスコアを計算"""
        score = 0
        
        # 年齢とポジションレベルの整合性
        age = seeker.get('age', 0)
        position = job_pattern.get('position', '')
        
        if age <= 27 and any(keyword in position for keyword in ['フロントエンド', 'エンジニア', 'アナリスト']):
            score += 2
        elif 28 <= age <= 35 and any(keyword in position for keyword in ['マネージャー', 'プロジェクト', 'リード']):
            score += 2
        elif age >= 36 and any(keyword in position for keyword in ['アーキテクト', 'シニア', '責任者']):
            score += 2
        
        # スキルマッチング
        seeker_skills = set(skill.lower() for skill in seeker.get('skills', []))
        required_skills = set(skill.lower() for skill in job_pattern.get('requirements', {}).get('skills', []))
        skill_overlap = len(seeker_skills.intersection(required_skills))
        score += skill_overlap
        
        # 価値観とカルチャーマッチング
        seeker_values = set(value.lower() for value in seeker.get('values', []))
        culture_keywords = set(culture.lower() for culture in job_pattern.get('culture', []))
        culture_overlap = len(seeker_values.intersection(culture_keywords))
        score += culture_overlap
        
        # キャリアチェンジの場合の特別考慮
        if "キャリアチェンジ" in seeker.get('tags', []):
            if "未経験" in str(job_pattern.get('requirements', {})) or \
               "学習支援" in job_pattern.get('culture', []):
                score += 3
        
        return score
    
    def generate_job_posting_from_pattern(self, pattern: Dict, company_name: str = None) -> Dict:
        """求人パターンから具体的な求人票を生成"""
        if not company_name:
            # 業界に応じたランダムな会社名を生成
            company_name = self._generate_company_name(pattern.get('industry', ''))
        
        # 年収範囲から具体的な金額を設定
        salary_range = pattern.get('conditions', {}).get('salary_range', '400-600万円')
        salary = self._extract_salary_from_range(salary_range)
        
        # 面接官情報を取得し、現在時刻ベースでavailabilityを更新
        interviewers = self._get_default_interviewers()
        updated_interviewers = self._update_interviewer_availability(interviewers)
        
        job_posting = {
            "id": f"generated_{pattern['id']}_{random.randint(1000, 9999)}",
            "title": pattern['position'],
            "company": company_name,
            "salary": salary,
            "work_style": pattern.get('conditions', {}).get('work_style', 'ハイブリッド'),
            "tech_stack": pattern.get('requirements', {}).get('skills', []),
            "culture_keywords": pattern.get('culture', []),
            "mission": pattern.get('mission', ''),
            "appeal_points": pattern.get('appeal_points', []),
            "requirements": pattern.get('requirements', {}),
            "benefits": pattern.get('conditions', {}).get('benefits', []),
            "company_type": pattern.get('company_type', ''),
            "industry": pattern.get('industry', ''),
            "size": pattern.get('size', ''),
            # 🆕 更新済み面接官情報
            "interviewers": updated_interviewers
        }
        
        return job_posting
    
    def _generate_company_name(self, industry: str) -> str:
        """業界に応じた会社名を生成"""
        industry_prefixes = {
            'EdTech': ['エデュ', 'ラーン', 'スタディ', 'アカデミー'],
            '金融': ['フィン', 'ペイ', 'マネー', 'ファイナンス'],
            '戦略コンサル': ['ストラテジー', 'コンサル', 'アドバイザリー', 'ソリューション'],
            'SaaS': ['クラウド', 'テック', 'ソフト', 'システム'],
            'システムインテグレーション': ['システム', 'IT', 'テクノロジー', 'ソリューション'],
            'eコマース': ['マーケット', 'コマース', 'ショップ', 'リテール']
        }
        
        suffixes = ['株式会社', '合同会社', '株式会社', 'Inc.', 'Co., Ltd.']
        
        prefixes = industry_prefixes.get(industry, ['テック', 'イノベーション', 'デジタル'])
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        
        return f"{prefix}{suffix}"
    
    def _extract_salary_from_range(self, salary_range: str) -> int:
        """年収範囲文字列から具体的な金額を抽出"""
        try:
            # "400-550万円" -> 400から550の間でランダム
            import re
            numbers = re.findall(r'\d+', salary_range)
            if len(numbers) >= 2:
                min_salary = int(numbers[0])
                max_salary = int(numbers[1])
                return random.randint(min_salary, max_salary)
            elif len(numbers) == 1:
                return int(numbers[0])
        except:
            pass
        return 500  # デフォルト値
    
    def _get_default_interviewers(self) -> List[Dict]:
        """デフォルトの面接官情報を取得"""
        if self.static_jobs:
            # 既存のjobs.jsonから面接官情報を借用
            for job in self.static_jobs:
                if job.get('interviewers'):
                    return job['interviewers']
        
        # フォールバック：ダミー面接官（availability付き）
        jst = pytz.timezone('Asia/Tokyo')
        base_date = datetime.now(jst) + timedelta(days=7)
        
        # フォールバック面接官の空き時間を生成
        availability = [
            {
                "stage": "一次面接",
                "name": "田中マネージャー",
                "role": "採用マネージャー",
                "email": "tanaka@example.com",
                "scheduling_method": "calendar",
                "interview_duration": 45,
                "availability": availability
            },
            {
                "stage": "最終面接", 
                "name": "山田部長",
                "role": "部長",
                "email": "yamada@example.com",
                "scheduling_method": "calendar",
                "interview_duration": 60,
                "availability": availability
            }
        ]
        
        return [
            {
                "stage": "一次面接",
                "name": "田中マネージャー",
                "role": "採用マネージャー",
                "email": "tanaka@example.com",
                "scheduling_method": "calendar",
                "interview_duration": 45,
                "availability": availability
            },
            {
                "stage": "最終面接", 
                "name": "山田部長",
                "role": "部長",
                "email": "yamada@example.com",
                "scheduling_method": "calendar",
                "interview_duration": 60,
                "availability": availability
            }
        ]
    
    def _update_interviewer_availability(self, interviewers: List[Dict]) -> List[Dict]:
        """面接官のavailabilityを現在時刻ベースに更新（求職者と重複しやすく調整）"""
        from datetime import datetime, timedelta
        import pytz
        
        jst = pytz.timezone('Asia/Tokyo')
        base_date = datetime.now(jst) + timedelta(days=7)
        
        updated_interviewers = []
        for interviewer in interviewers:
            updated_interviewer = interviewer.copy()
            
            # 🎯 転職エージェントの現実: 面接官は複数の時間帯で柔軟に対応
            availability = []
            
            # パターン1: 求職者の平日午後に合わせた企業側の調整
            day1 = base_date.replace(hour=13, minute=0, second=0, microsecond=0)  # 13:00開始で重複確保
            availability.append({
                "start": day1.isoformat(),
                "end": (day1 + timedelta(hours=5)).isoformat(),  # 13:00-18:00（求職者14:00-18:00と重複）
                "preference": "high"
            })
            
            # パターン2: 求職者の平日夕方と重複する企業の延長対応
            day2 = (base_date + timedelta(days=2)).replace(hour=17, minute=0, second=0, microsecond=0)
            availability.append({
                "start": day2.isoformat(),
                "end": (day2 + timedelta(hours=3)).isoformat(),  # 17:00-20:00（求職者18:00-20:00と重複）
                "preference": "medium"
            })
            
            # パターン3: 土曜日の対応（転職面接では企業も土曜日に対応することが多い）
            saturday = base_date + timedelta(days=(5-base_date.weekday()) % 7)  # 次の土曜日
            saturday_slot = saturday.replace(hour=10, minute=0, second=0, microsecond=0)
            availability.append({
                "start": saturday_slot.isoformat(),
                "end": (saturday_slot + timedelta(hours=6)).isoformat(),  # 10:00-16:00（求職者と重複）
                "preference": "medium"
            })
            
            # パターン4: 平日朝の早朝対応（9:00開始で朝型の面接）
            early_day = (base_date + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
            availability.append({
                "start": early_day.isoformat(),
                "end": (early_day + timedelta(hours=3)).isoformat(),  # 9:00-12:00
                "preference": "low"
            })
            
            updated_interviewer['availability'] = availability
            updated_interviewers.append(updated_interviewer)
        
        return updated_interviewers
    
    def get_simulation_pair(self) -> Tuple[Dict, Dict]:
        """シミュレーション用の求職者と求人のペアを取得"""
        seeker = self.select_random_seeker()
        
        # 🆕 求職者にavailability（空き時間情報）を追加
        seeker = self._add_availability_to_seeker(seeker.copy())
        
        job_pattern = self.select_suitable_job_pattern(seeker)
        
        if job_pattern:
            job_posting = self.generate_job_posting_from_pattern(job_pattern)
        else:
            # フォールバック：既存の静的求人からランダム選択
            if self.static_jobs:
                job_posting = random.choice(self.static_jobs)
            else:
                raise ValueError("求人データが見つかりません")
        
        return seeker, job_posting
    
    def _add_availability_to_seeker(self, seeker: Dict) -> Dict:
        """求職者にダミーの空き時間情報を追加"""
        # 日本時間のタイムゾーンを設定
        jst = pytz.timezone('Asia/Tokyo')
        
        # 現在日時から1週間後の範囲で空き時間を生成（timezone-aware）
        base_date = datetime.now(jst) + timedelta(days=7)
        
        # 平日の空き時間パターンを複数生成（現実的な空き時間を想定）
        availability = []
        
        # パターン1: 平日午後（在職中のため午後に時間を作る）
        day1 = base_date.replace(hour=14, minute=0, second=0, microsecond=0)
        availability.append({
            "start": day1.isoformat(),
            "end": (day1 + timedelta(hours=4)).isoformat()
        })
        
        # パターン2: 平日夕方（在職中のため夕方に時間を作る）
        day2 = (base_date + timedelta(days=2)).replace(hour=18, minute=0, second=0, microsecond=0)
        availability.append({
            "start": day2.isoformat(),
            "end": (day2 + timedelta(hours=2)).isoformat()
        })
        
        # パターン3: 土曜日の午前（休日を利用）
        saturday = base_date + timedelta(days=(5 - base_date.weekday()) % 7)
        saturday_slot = saturday.replace(hour=10, minute=0, second=0, microsecond=0)
        availability.append({
            "start": saturday_slot.isoformat(),
            "end": (saturday_slot + timedelta(hours=6)).isoformat()
        })
        
        seeker["availability"] = availability
        
        return seeker
    
    def get_stats(self) -> Dict:
        """データ統計情報を取得"""
        return {
            "seekers_count": len(self.seekers),
            "job_patterns_count": len(self.job_patterns),
            "static_jobs_count": len(self.static_jobs),
            "seeker_types": [seeker.get('tags', ['不明'])[0] for seeker in self.seekers if seeker.get('tags')],
            "job_types": [pattern.get('position', '不明') for pattern in self.job_patterns]
        } 