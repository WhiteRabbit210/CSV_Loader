import json
import os
import base64
import tempfile
import pandas as pd
from utils.user_sync import UserSyncManager
from utils.csv_analyzer import CSVAnalyzer


def lambda_handler(event, context):
    """
    ユーザー同期を実行するLambda関数
    """
    try:
        body = json.loads(event.get('body', '{}'))
        csv_data = body.get('csvData', {})
        mapping = body.get('mapping', {})
        dry_run = body.get('dryRun', True)
        
        # CSV データを復元
        file_content = csv_data.get('file_content')
        if not file_content:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': 'CSVデータが提供されていません'
                })
            }
        
        # Base64デコード
        file_data = base64.b64decode(file_content)
        
        # 一時ファイルに保存
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as tmp_file:
            tmp_file.write(file_data)
            tmp_file_path = tmp_file.name
        
        try:
            # CSV読み込み
            analyzer = CSVAnalyzer()
            df = analyzer.read_csv(tmp_file_path)
            
            # UserSyncManager初期化
            cognito_pool_id = os.environ.get('COGNITO_USER_POOL_ID')
            sync_manager = UserSyncManager(cognito_pool_id)
            
            # 既存ユーザーを読み込み（開発環境では固定ファイルから）
            if os.environ.get('ENV') == 'development':
                existing_users = sync_manager.load_existing_users(
                    '/var/task/sample-data/existing-saas-users.json'
                )
            else:
                # 本番環境では実際のデータソースから読み込み
                existing_users = load_existing_users_from_db()
            
            # ユーザー比較
            new_users, update_users, delete_users = sync_manager.compare_users(
                df, mapping, existing_users
            )
            
            if dry_run:
                # プレビューモード
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': True,
                        'summary': {
                            'toAdd': len(new_users),
                            'toUpdate': len(update_users),
                            'toDelete': len(delete_users)
                        },
                        'newUsers': new_users[:10],  # 最大10件
                        'updateUsers': update_users[:10],
                        'deleteUsers': delete_users[:10]
                    }, ensure_ascii=False)
                }
            else:
                # 実行モード
                results = sync_manager.execute_sync(
                    new_users, update_users, delete_users, dry_run=False
                )
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'success': True,
                        'results': results
                    }, ensure_ascii=False)
                }
                
        finally:
            # 一時ファイルを削除
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'message': f'同期処理中にエラーが発生しました: {str(e)}'
            }, ensure_ascii=False)
        }


def load_existing_users_from_db():
    """本番環境で既存ユーザーをDBから読み込む（実装が必要）"""
    # TODO: DynamoDBなどから既存ユーザーを読み込む
    return {}