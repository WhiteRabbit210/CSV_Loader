import os
import sys
import json
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
import time

# Lambdaのコードを再利用するためパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.csv_analyzer import CSVAnalyzer
from utils.user_sync import UserSyncManager
from utils.logger import log_info, log_error, log_access, log_debug

app = Flask(__name__)

# 環境変数の読み込み
from dotenv import load_dotenv
load_dotenv()

# 環境設定
env = os.getenv('FLASK_ENV', 'production')
os.environ['ENV'] = env

# CORS設定
cors_origins = os.getenv('CORS_ORIGINS', '*').split(',')
CORS(app, origins=cors_origins, 
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# ログAPIを登録
from api_logs import logs_bp
app.register_blueprint(logs_bp)

# アップロードされたCSVを一時的に保存
uploaded_csv_data = {}

# ログ初期化
log_info("Flask server started", {"port": 8000, "env": "development"})

# リクエストログ
@app.before_request
def log_request():
    log_debug(f"Request: {request.method} {request.path}", {
        "headers": dict(request.headers),
        "args": dict(request.args)
    })
    request.start_time = time.time()

# レスポンスログ
@app.after_request
def log_response(response):
    if hasattr(request, 'start_time'):
        response_time = (time.time() - request.start_time) * 1000  # ms
        log_access(
            request.method,
            request.path,
            response.status_code,
            response_time,
            request.headers.get('User-Agent')
        )
    return response


@app.route('/api/csv/upload', methods=['POST'])
def upload_csv():
    """CSVファイルのアップロード"""
    try:
        log_info("CSV upload started")
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'ファイルが選択されていません'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'ファイルが選択されていません'
            }), 400
        
        # 一時ファイルに保存
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            file.save(tmp_file.name)
            tmp_path = tmp_file.name
        
        try:
            # CSV解析
            analyzer = CSVAnalyzer()
            df = analyzer.read_csv(tmp_path)
            
            # フィールド自動検出
            auto_mapping = analyzer.auto_detect_fields(df)
            
            # プレビューデータ取得
            headers, preview = analyzer.get_preview_data(df)
            
            # CSVデータを保存（後の処理で使用）
            with open(tmp_path, 'rb') as f:
                file_content = base64.b64encode(f.read()).decode('utf-8')
            
            session_id = str(hash(file.filename))
            uploaded_csv_data[session_id] = {
                'file_content': file_content,
                'headers': headers,
                'preview': preview
            }
            
            log_info("CSV upload successful", {
                'filename': file.filename,
                'rows': len(df),
                'session_id': session_id
            })
            
            return jsonify({
                'success': True,
                'headers': headers,
                'preview': preview,
                'auto_mapping': auto_mapping,
                'total_rows': len(df),
                'session_id': session_id
            })
            
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    except Exception as e:
        log_error("CSV upload failed", e, {"filename": request.files.get('file', {}).get('filename')})
        return jsonify({
            'success': False,
            'message': f'CSV解析中にエラーが発生しました: {str(e)}'
        }), 500


@app.route('/api/sync/preview', methods=['POST'])
def sync_preview():
    """同期プレビュー"""
    try:
        data = request.json
        csv_data = data.get('csvData', {})
        mapping = data.get('mapping', {})
        
        session_id = csv_data.get('session_id')
        if not session_id or session_id not in uploaded_csv_data:
            return jsonify({
                'success': False,
                'message': 'CSVデータが見つかりません'
            }), 400
        
        # CSVデータを復元
        file_content = uploaded_csv_data[session_id]['file_content']
        file_data = base64.b64decode(file_content)
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as tmp_file:
            tmp_file.write(file_data)
            tmp_path = tmp_file.name
        
        try:
            # CSV読み込み
            analyzer = CSVAnalyzer()
            df = analyzer.read_csv(tmp_path)
            
            # 既存ユーザーを読み込み
            sync_manager = UserSyncManager()
            existing_users = sync_manager.load_existing_users(
                os.path.join(os.path.dirname(__file__), '../sample-data/existing-saas-users.json')
            )
            
            # ユーザー比較
            new_users, update_users, delete_users = sync_manager.compare_users(
                df, mapping, existing_users
            )
            
            return jsonify({
                'success': True,
                'summary': {
                    'toAdd': len(new_users),
                    'toUpdate': len(update_users),
                    'toDelete': len(delete_users)
                },
                'newUsers': new_users[:10],
                'updateUsers': update_users[:10],
                'deleteUsers': delete_users[:10]
            })
            
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'プレビュー生成中にエラーが発生しました: {str(e)}'
        }), 500


@app.route('/api/sync/execute', methods=['POST'])
def sync_execute():
    """同期実行"""
    try:
        data = request.json
        csv_data = data.get('csvData', {})
        mapping = data.get('mapping', {})
        
        session_id = csv_data.get('session_id')
        if not session_id or session_id not in uploaded_csv_data:
            return jsonify({
                'success': False,
                'message': 'CSVデータが見つかりません'
            }), 400
        
        # CSVデータを復元
        file_content = uploaded_csv_data[session_id]['file_content']
        file_data = base64.b64decode(file_content)
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as tmp_file:
            tmp_file.write(file_data)
            tmp_path = tmp_file.name
        
        try:
            # CSV読み込み
            analyzer = CSVAnalyzer()
            df = analyzer.read_csv(tmp_path)
            
            # 既存ユーザーを読み込み
            sync_manager = UserSyncManager()
            existing_users = sync_manager.load_existing_users(
                os.path.join(os.path.dirname(__file__), '../sample-data/existing-saas-users.json')
            )
            
            # ユーザー比較
            new_users, update_users, delete_users = sync_manager.compare_users(
                df, mapping, existing_users
            )
            
            # 同期実行（開発環境なのでdry_run=True）
            results = sync_manager.execute_sync(
                new_users, update_users, delete_users, dry_run=True
            )
            
            results['id'] = session_id
            
            return jsonify({
                'success': True,
                'results': results
            })
            
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'同期実行中にエラーが発生しました: {str(e)}'
        }), 500


@app.route('/api/sync/download-log', methods=['POST'])
def download_log():
    """処理ログのダウンロード"""
    try:
        # ダミーのログデータを生成
        log_data = """処理日時,操作,メールアドレス,結果,エラー内容
2024-01-20 10:30:00,追加,tanaka.jiro@example.com,成功,
2024-01-20 10:30:01,追加,yamada.hanako@example.com,成功,
2024-01-20 10:30:02,追加,sasaki.taro@example.com,成功,
2024-01-20 10:30:03,更新,suzuki.hanako@example.com,成功,
2024-01-20 10:30:04,更新,kobayashi.takeshi@example.com,成功,
2024-01-20 10:30:05,削除,sato.yuki@example.com,成功,
2024-01-20 10:30:06,削除,ito.hiroshi@example.com,成功,"""
        
        return log_data, 200, {
            'Content-Type': 'text/csv; charset=utf-8',
            'Content-Disposition': 'attachment; filename=sync-log.csv'
        }
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'ログダウンロード中にエラーが発生しました: {str(e)}'
        }), 500


@app.route('/api/mappings', methods=['GET'])
def get_mappings():
    """保存済みマッピング設定を取得"""
    return jsonify({
        'success': True,
        'mappings': []  # 開発環境では空配列を返す
    })


@app.route('/api/mappings', methods=['POST'])
def save_mapping():
    """マッピング設定を保存"""
    data = request.json
    return jsonify({
        'success': True,
        'mapping': {
            'id': '1',
            'name': data.get('name'),
            'config': data.get('config'),
            'createdAt': '2024-01-20T10:00:00Z'
        }
    })


if __name__ == '__main__':
    app.run(debug=True, port=8000)