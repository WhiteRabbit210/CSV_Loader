# デプロイ手順

## 開発環境

### バックエンド起動
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### フロントエンド起動
```bash
cd frontend
npm install
npm run dev
```

## 本番環境デプロイ

### 1. 環境変数の設定

#### バックエンド (.env)
```bash
FLASK_ENV=production
FLASK_DEBUG=false
CORS_ORIGINS=https://your-domain.com
SECRET_KEY=your-secure-secret-key
AWS_REGION=ap-northeast-1
COGNITO_USER_POOL_ID=your-pool-id
DYNAMODB_TABLE_NAME=csv-loader-mappings
S3_BUCKET_NAME=csv-loader-temp
```

#### フロントエンド
本番ビルド時は自動的に相対パスを使用（同一ドメインを想定）

### 2. ビルド

#### フロントエンド
```bash
cd frontend
npm run build
# distフォルダが生成される
```

#### バックエンド（Dockerを使用）
```bash
cd backend
docker build -t csv-loader-backend .
```

### 3. デプロイオプション

#### オプション1: 同一サーバーにデプロイ
- フロントエンドのdistフォルダをWebサーバー（Nginx等）で配信
- バックエンドをリバースプロキシで/api/*にマッピング

Nginx設定例：
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # フロントエンド
    location / {
        root /var/www/csv-loader/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # バックエンドAPI
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### オプション2: 別々のサーバーにデプロイ
1. フロントエンドの.env.productionを編集
```
VITE_API_BASE_URL=https://api.your-domain.com
```

2. バックエンドのCORS設定を更新
```
CORS_ORIGINS=https://your-frontend-domain.com
```

### 4. Lambda デプロイ（オプション）

Lambda関数として実行する場合：

1. Lambda Layer作成（pandas等の大きなライブラリ用）
```bash
pip install -r requirements.txt -t python/
zip -r layer.zip python
```

2. 各Lambda関数をzipファイルにパッケージング
```bash
cd lambdas
zip csv_parser.zip csv_parser.py
zip user_sync.zip user_sync.py
zip mapping_config.zip mapping_config.py
```

3. API Gatewayの設定
- 各エンドポイントを対応するLambda関数にマッピング
- CORSを有効化

## セキュリティ注意事項

1. 本番環境では必ず強力なSECRET_KEYを設定
2. HTTPS通信を使用
3. 適切なCORS設定（特定のドメインのみ許可）
4. ファイルアップロードサイズの制限
5. レート制限の実装を検討