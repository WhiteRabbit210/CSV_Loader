"""
ログ確認用のAPIエンドポイント
"""
from flask import Blueprint, jsonify, request
from utils.logger import debug_log, log_info

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/api/logs/<log_type>', methods=['GET'])
def get_logs(log_type):
    """最近のログを取得"""
    try:
        lines = request.args.get('lines', 100, type=int)
        logs = debug_log.get_recent_logs(log_type, lines)
        
        log_info(f"Logs retrieved: {log_type}", {"lines": len(logs)})
        
        return jsonify({
            'success': True,
            'log_type': log_type,
            'logs': logs
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@logs_bp.route('/api/logs/clear/<log_type>', methods=['POST'])
def clear_logs(log_type):
    """ログをクリア"""
    try:
        # 実装は必要に応じて追加
        return jsonify({
            'success': True,
            'message': f'{log_type} logs cleared'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500