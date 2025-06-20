# CSV User Management System

CSVファイルを使用してSaaSのユーザー管理を行うシステムです。HR/ERPシステムからエクスポートされたCSVファイルをアップロードし、フィールドマッピングを設定して、ユーザーの追加・更新・削除を一括で実行できます。

## 機能

- **CSVアップロード**: さまざまな形式のCSVファイルに対応
- **フィールドマッピング**: CSVの列とシステムフィールドを柔軟にマッピング
- **複数フィールド連結**: 名前、役職、所属などの複数フィールドを連結可能
- **マッピング設定の保存**: 設定を保存して再利用可能
- **マッピング設定の自動保持**: 画面遷移時にマッピング設定を自動的に保持
- **同期プレビュー**: 実行前に変更内容を確認
- **包括的なログシステム**: デバッグ用の詳細なログ記録

## 技術スタック

### フロントエンド
- Vue.js 3 (Composition API)
- Element Plus (UIフレームワーク)
- Pinia (状態管理)
- Vite (ビルドツール)

### バックエンド
- Python Flask
- Pandas (CSV処理)
- AWS Lambda対応設計

## インストール

### 前提条件
- Node.js 16以上
- Python 3.9以上

### セットアップ

1. リポジトリのクローン
```bash
git clone https://github.com/WhiteRabbit210/CSV_Loader.git
cd CSV_Loader
```

2. バックエンドのセットアップ
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. フロントエンドのセットアップ
```bash
cd ../frontend
npm install
```

## 開発環境での実行

1. バックエンドサーバーの起動
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python app.py
```

2. フロントエンドの起動
```bash
cd frontend
npm run dev
```

3. ブラウザで http://localhost:3000 にアクセス

## 使用方法

1. **CSVファイルのアップロード**
   - トップページから「CSVファイルを選択」をクリック
   - HR/ERPシステムからエクスポートしたCSVファイルを選択

2. **フィールドマッピング**
   - CSVの列とシステムフィールド（名前、メールアドレス、役職、所属）をマッピング
   - メールアドレスは必須フィールド（ユーザー識別キー）
   - 「+」ボタンで複数フィールドの連結が可能

3. **同期内容の確認**
   - 追加・更新・削除されるユーザーのプレビュー
   - 変更内容を確認して実行

4. **結果確認**
   - 同期結果の表示
   - エラーがあった場合は詳細を確認可能

## 環境変数

### バックエンド (.env)
```
FLASK_ENV=development
FLASK_DEBUG=true
SECRET_KEY=your-secret-key
```

### フロントエンド
- `.env.development`: 開発環境設定
- `.env.production`: 本番環境設定

## デプロイ

AWS Lambdaへのデプロイ手順は [deploy-instructions.md](deploy-instructions.md) を参照してください。

## ディレクトリ構造

```
CSV_Loader/
├── backend/
│   ├── app.py              # Flaskアプリケーション
│   ├── lambdas/            # Lambda関数
│   ├── utils/              # ユーティリティ
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/          # Vueコンポーネント
│   │   ├── stores/         # Pinia ストア
│   │   └── utils/          # ユーティリティ
│   └── package.json
└── README.md
```

## ライセンス

[MITライセンス](LICENSE)

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを作成して変更内容について議論してください。