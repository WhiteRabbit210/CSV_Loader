import pandas as pd
import chardet
import re
from typing import Dict, List, Tuple, Optional


class CSVAnalyzer:
    """CSVファイルを解析し、フィールドの自動認識を行うクラス"""
    
    def __init__(self):
        self.email_patterns = [
            r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        ]
        self.name_keywords = [
            '名前', '氏名', 'name', 'full name', '社員名', 'employee name', '名'
        ]
        self.position_keywords = [
            '役職', '職位', 'position', 'title', 'job title', '職務'
        ]
        self.department_keywords = [
            '部署', '部門', '所属', 'department', 'dept', 'division', '課'
        ]
    
    def detect_encoding(self, file_path: str) -> str:
        """ファイルのエンコーディングを検出"""
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        return result['encoding'] or 'utf-8'
    
    def read_csv(self, file_path: str) -> pd.DataFrame:
        """CSVファイルを読み込み"""
        encoding = self.detect_encoding(file_path)
        try:
            df = pd.read_csv(file_path, encoding=encoding)
        except:
            # エンコーディングエラーの場合、UTF-8で再試行
            df = pd.read_csv(file_path, encoding='utf-8', errors='ignore')
        return df
    
    def analyze_column(self, series: pd.Series) -> Dict[str, float]:
        """カラムの内容を分析してフィールドタイプの確率を返す"""
        scores = {
            'name': 0.0,
            'email': 0.0,
            'position': 0.0,
            'department': 0.0
        }
        
        # サンプルデータ（最大100行）を取得
        sample = series.dropna().head(100)
        if len(sample) == 0:
            return scores
        
        # メールアドレスの判定
        email_matches = sum(1 for val in sample if self._is_email(str(val)))
        scores['email'] = email_matches / len(sample)
        
        # カラム名による判定
        col_name_lower = series.name.lower() if series.name else ''
        
        # 名前の判定
        if any(keyword in col_name_lower for keyword in self.name_keywords):
            scores['name'] += 0.5
        if self._contains_name_values(sample):
            scores['name'] += 0.5
        
        # 役職の判定
        if any(keyword in col_name_lower for keyword in self.position_keywords):
            scores['position'] += 0.5
        if self._contains_position_values(sample):
            scores['position'] += 0.5
        
        # 部署の判定
        if any(keyword in col_name_lower for keyword in self.department_keywords):
            scores['department'] += 0.5
        if self._contains_department_values(sample):
            scores['department'] += 0.5
        
        return scores
    
    def _is_email(self, value: str) -> bool:
        """メールアドレスかどうかを判定"""
        for pattern in self.email_patterns:
            if re.match(pattern, value):
                return True
        return False
    
    def _contains_position_values(self, series: pd.Series) -> bool:
        """役職の値が含まれているかを判定"""
        position_values = ['部長', '課長', '主任', '係長', 'Manager', 'Director', 'Staff']
        values_str = ' '.join(series.astype(str).tolist()).lower()
        return any(pos.lower() in values_str for pos in position_values)
    
    def _contains_department_values(self, series: pd.Series) -> bool:
        """部署の値が含まれているかを判定"""
        dept_values = ['部', '課', 'Department', 'Division', '営業', '技術', '経理', '人事']
        values_str = ' '.join(series.astype(str).tolist()).lower()
        return any(dept.lower() in values_str for dept in dept_values)
    
    def _contains_name_values(self, series: pd.Series) -> bool:
        """名前の値が含まれているかを判定"""
        # 日本人の名前によくある姓や名
        name_indicators = ['田中', '佐藤', '鈴木', '山田', '太郎', '花子', '一郎']
        # カタカナやアルファベットのパターン
        has_katakana = any('ア' <= char <= 'ヴ' for val in series.astype(str) for char in str(val))
        has_kanji = any('一' <= char <= '鿿' for val in series.astype(str) for char in str(val))
        
        values_str = ' '.join(series.astype(str).tolist())
        has_name_indicator = any(name in values_str for name in name_indicators)
        
        return has_name_indicator or (has_katakana and has_kanji)
    
    def auto_detect_fields(self, df: pd.DataFrame) -> Dict[str, Optional[int]]:
        """フィールドを自動検出"""
        mapping = {
            'name': None,
            'email': None,
            'position': None,
            'department': None
        }
        
        field_scores = {}
        for idx, col in enumerate(df.columns):
            scores = self.analyze_column(df[col])
            for field_type, score in scores.items():
                if score > 0:
                    if field_type not in field_scores:
                        field_scores[field_type] = []
                    field_scores[field_type].append((idx, score, col))
        
        # 最も高いスコアのカラムを選択
        for field_type, candidates in field_scores.items():
            if candidates:
                best = max(candidates, key=lambda x: x[1])
                if best[1] >= 0.5:  # 閾値以上のスコアの場合のみ設定
                    mapping[field_type] = best[0]
        
        return mapping
    
    def get_preview_data(self, df: pd.DataFrame, rows: int = 10) -> Tuple[List[str], List[List[str]]]:
        """プレビューデータを取得"""
        headers = df.columns.tolist()
        preview = df.head(rows).fillna('').astype(str).values.tolist()
        return headers, preview