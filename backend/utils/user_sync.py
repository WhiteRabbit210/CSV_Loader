import json
import boto3
from typing import Dict, List, Tuple
import pandas as pd
from datetime import datetime


class UserSyncManager:
    """ユーザー同期処理を管理するクラス"""
    
    def __init__(self, cognito_user_pool_id: str = None):
        self.cognito_user_pool_id = cognito_user_pool_id
        if cognito_user_pool_id:
            self.cognito_client = boto3.client('cognito-idp')
        else:
            self.cognito_client = None
    
    def load_existing_users(self, file_path: str = None) -> Dict[str, Dict]:
        """既存のSaaSユーザーを読み込み（開発用）"""
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {user['email']: user for user in data['users']}
        return {}
    
    def compare_users(self, csv_df: pd.DataFrame, mapping: Dict[str, any], 
                     existing_users: Dict[str, Dict]) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """CSVデータと既存ユーザーを比較"""
        new_users = []
        update_users = []
        delete_users = []
        
        # CSVのメールアドレスを取得
        csv_emails = set()
        email_col = mapping.get('email')
        
        if email_col is None:
            raise ValueError("メールアドレスフィールドが指定されていません")
        
        # CSVデータを処理
        for _, row in csv_df.iterrows():
            email = str(row.iloc[email_col]).strip()
            if not email or email == 'nan':
                continue
                
            csv_emails.add(email)
            
            user_data = {
                'name': self._get_field_value(row, mapping.get('name')),
                'email': email,
                'position': self._get_field_value(row, mapping.get('position')),
                'department': self._get_field_value(row, mapping.get('department'))
            }
            
            if email in existing_users:
                # 既存ユーザーの場合、変更をチェック
                existing = existing_users[email]
                changes = {}
                
                if user_data['name'] != existing.get('name'):
                    changes['name'] = {
                        'old': existing.get('name', ''),
                        'new': user_data['name']
                    }
                
                if user_data['position'] != existing.get('position'):
                    changes['position'] = {
                        'old': existing.get('position', ''),
                        'new': user_data['position']
                    }
                
                if user_data['department'] != existing.get('department'):
                    changes['department'] = {
                        'old': existing.get('department', ''),
                        'new': user_data['department']
                    }
                
                if changes:
                    update_users.append({
                        'email': email,
                        'changes': changes,
                        'new_data': user_data
                    })
            else:
                # 新規ユーザー
                new_users.append(user_data)
        
        # 削除対象ユーザーを特定
        for email, user in existing_users.items():
            if email not in csv_emails:
                delete_users.append({
                    'email': email,
                    'id': user.get('id'),
                    'name': user.get('name', ''),
                    'position': user.get('position', ''),
                    'department': user.get('department', '')
                })
        
        return new_users, update_users, delete_users
    
    def _get_field_value(self, row: pd.Series, col_config: any) -> str:
        """フィールドの値を取得（複数フィールドの連結対応）"""
        if col_config is None:
            return ''
        
        # 配列の場合は複数フィールドを連結
        if isinstance(col_config, list):
            values = []
            for idx in col_config:
                if idx is not None and 0 <= idx < len(row):
                    value = row.iloc[idx]
                    if pd.notna(value) and str(value).strip():
                        values.append(str(value).strip())
            return ' '.join(values)
        
        # 単一の値の場合
        if isinstance(col_config, int) and 0 <= col_config < len(row):
            value = row.iloc[col_config]
            return str(value).strip() if pd.notna(value) else ''
        
        return ''
    
    def execute_sync(self, new_users: List[Dict], update_users: List[Dict], 
                    delete_users: List[Dict], dry_run: bool = False) -> Dict:
        """同期を実行"""
        results = {
            'added': 0,
            'updated': 0,
            'deleted': 0,
            'errors': [],
            'startTime': datetime.now().isoformat(),
            'endTime': None
        }
        
        if dry_run:
            results['added'] = len(new_users)
            results['updated'] = len(update_users)
            results['deleted'] = len(delete_users)
            results['endTime'] = datetime.now().isoformat()
            return results
        
        # 新規ユーザー追加
        for user in new_users:
            try:
                if self.cognito_client:
                    self._create_cognito_user(user)
                results['added'] += 1
            except Exception as e:
                results['errors'].append({
                    'email': user['email'],
                    'operation': '追加',
                    'error': str(e)
                })
        
        # ユーザー更新
        for user in update_users:
            try:
                if self.cognito_client:
                    self._update_cognito_user(user)
                results['updated'] += 1
            except Exception as e:
                results['errors'].append({
                    'email': user['email'],
                    'operation': '更新',
                    'error': str(e)
                })
        
        # ユーザー削除
        for user in delete_users:
            try:
                if self.cognito_client:
                    self._delete_cognito_user(user)
                results['deleted'] += 1
            except Exception as e:
                results['errors'].append({
                    'email': user['email'],
                    'operation': '削除',
                    'error': str(e)
                })
        
        results['endTime'] = datetime.now().isoformat()
        return results
    
    def _create_cognito_user(self, user: Dict):
        """Cognitoにユーザーを作成"""
        if not self.cognito_client:
            return
            
        response = self.cognito_client.admin_create_user(
            UserPoolId=self.cognito_user_pool_id,
            Username=user['email'],
            UserAttributes=[
                {'Name': 'email', 'Value': user['email']},
                {'Name': 'custom:position', 'Value': user['position']},
                {'Name': 'custom:department', 'Value': user['department']}
            ],
            MessageAction='SUPPRESS'
        )
    
    def _update_cognito_user(self, user: Dict):
        """Cognitoのユーザー情報を更新"""
        if not self.cognito_client:
            return
            
        attributes = []
        new_data = user['new_data']
        
        if 'position' in user['changes']:
            attributes.append({'Name': 'custom:position', 'Value': new_data['position']})
        
        if 'department' in user['changes']:
            attributes.append({'Name': 'custom:department', 'Value': new_data['department']})
        
        if attributes:
            response = self.cognito_client.admin_update_user_attributes(
                UserPoolId=self.cognito_user_pool_id,
                Username=user['email'],
                UserAttributes=attributes
            )
    
    def _delete_cognito_user(self, user: Dict):
        """Cognitoからユーザーを削除"""
        if not self.cognito_client:
            return
            
        response = self.cognito_client.admin_delete_user(
            UserPoolId=self.cognito_user_pool_id,
            Username=user['email']
        )