"""
バックエンドの設定ファイル
環境変数から設定を読み込み
"""
import os
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

class Config:
    """基本設定"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Flask設定
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # CORS設定
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # AWS設定
    AWS_REGION = os.getenv('AWS_REGION', 'ap-northeast-1')
    COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
    DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME', 'csv-loader-mappings')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'csv-loader-temp')
    
    # ログ設定
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # ファイルアップロード設定
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = {'csv'}
    
    @staticmethod
    def init_app(app):
        """アプリケーション初期化時の処理"""
        # アップロードフォルダの作成
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)


class DevelopmentConfig(Config):
    """開発環境設定"""
    DEBUG = True
    CORS_ORIGINS = ['http://localhost:3000']


class ProductionConfig(Config):
    """本番環境設定"""
    DEBUG = False
    # 本番環境では必ず環境変数から読み込む
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in production environment")


class TestingConfig(Config):
    """テスト環境設定"""
    TESTING = True
    DEBUG = True


# 環境別設定のマッピング
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}