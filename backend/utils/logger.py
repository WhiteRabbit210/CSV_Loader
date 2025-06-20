import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import json
import traceback


class DebugLogger:
    """共通のデバッグログ機能を提供するクラス"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
        os.makedirs(self.log_dir, exist_ok=True)
        
        # ログファイルのパス
        self.app_log_file = os.path.join(self.log_dir, 'app.log')
        self.error_log_file = os.path.join(self.log_dir, 'error.log')
        self.access_log_file = os.path.join(self.log_dir, 'access.log')
        
        # アプリケーションログの設定
        self.app_logger = self._setup_logger(
            'app_logger',
            self.app_log_file,
            logging.INFO
        )
        
        # エラーログの設定
        self.error_logger = self._setup_logger(
            'error_logger',
            self.error_log_file,
            logging.ERROR
        )
        
        # アクセスログの設定
        self.access_logger = self._setup_logger(
            'access_logger',
            self.access_log_file,
            logging.INFO
        )
    
    def _setup_logger(self, name, log_file, level):
        """ロガーのセットアップ"""
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # 既存のハンドラーをクリア
        logger.handlers.clear()
        
        # ファイルハンドラー（ローテーション付き）
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # コンソールハンドラー
        console_handler = logging.StreamHandler()
        
        # フォーマッター
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def info(self, message, data=None):
        """情報ログを記録"""
        log_entry = self._create_log_entry(message, data)
        self.app_logger.info(log_entry)
    
    def error(self, message, error=None, data=None):
        """エラーログを記録"""
        error_info = {
            'message': message,
            'data': data
        }
        
        if error:
            error_info['error_type'] = type(error).__name__
            error_info['error_message'] = str(error)
            error_info['traceback'] = traceback.format_exc()
        
        log_entry = json.dumps(error_info, ensure_ascii=False, indent=2)
        self.error_logger.error(log_entry)
        self.app_logger.error(log_entry)
    
    def access(self, method, path, status_code, response_time=None, user_agent=None):
        """アクセスログを記録"""
        log_data = {
            'method': method,
            'path': path,
            'status_code': status_code,
            'response_time': response_time,
            'user_agent': user_agent,
            'timestamp': datetime.now().isoformat()
        }
        log_entry = json.dumps(log_data, ensure_ascii=False)
        self.access_logger.info(log_entry)
    
    def debug(self, message, data=None):
        """デバッグログを記録"""
        log_entry = self._create_log_entry(f"[DEBUG] {message}", data)
        self.app_logger.debug(log_entry)
    
    def _create_log_entry(self, message, data=None):
        """ログエントリを作成"""
        if data:
            return f"{message} - {json.dumps(data, ensure_ascii=False)}"
        return message
    
    def get_recent_logs(self, log_type='app', lines=100):
        """最近のログを取得"""
        log_files = {
            'app': self.app_log_file,
            'error': self.error_log_file,
            'access': self.access_log_file
        }
        
        log_file = log_files.get(log_type, self.app_log_file)
        
        if not os.path.exists(log_file):
            return []
        
        with open(log_file, 'r', encoding='utf-8') as f:
            lines_list = f.readlines()
            return lines_list[-lines:]


# シングルトンインスタンス
debug_log = DebugLogger()


# 便利な関数として公開
def log_info(message, data=None):
    """情報ログを記録する便利関数"""
    debug_log.info(message, data)


def log_error(message, error=None, data=None):
    """エラーログを記録する便利関数"""
    debug_log.error(message, error, data)


def log_access(method, path, status_code, response_time=None, user_agent=None):
    """アクセスログを記録する便利関数"""
    debug_log.access(method, path, status_code, response_time, user_agent)


def log_debug(message, data=None):
    """デバッグログを記録する便利関数"""
    debug_log.debug(message, data)