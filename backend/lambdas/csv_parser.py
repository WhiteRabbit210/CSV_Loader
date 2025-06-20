import json
import base64
import os
import tempfile
from utils.csv_analyzer import CSVAnalyzer


def lambda_handler(event, context):
    """
    CSVファイルを解析してフィールドの自動認識を行うLambda関数
    """
    try:
        # Base64エンコードされたファイルデータを取得
        file_content = event.get('body', {}).get('file_content')
        if not file_content:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'message': 'ファイルが提供されていません'
                })
            }
        
        # Base64デコード
        file_data = base64.b64decode(file_content)
        
        # 一時ファイルに保存
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as tmp_file:
            tmp_file.write(file_data)
            tmp_file_path = tmp_file.name
        
        try:
            # CSV解析
            analyzer = CSVAnalyzer()
            df = analyzer.read_csv(tmp_file_path)
            
            # フィールド自動検出
            auto_mapping = analyzer.auto_detect_fields(df)
            
            # プレビューデータ取得
            headers, preview = analyzer.get_preview_data(df)
            
            # レスポンス作成
            response = {
                'success': True,
                'headers': headers,
                'preview': preview,
                'auto_mapping': auto_mapping,
                'total_rows': len(df)
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(response, ensure_ascii=False)
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
                'message': f'CSV解析中にエラーが発生しました: {str(e)}'
            }, ensure_ascii=False)
        }