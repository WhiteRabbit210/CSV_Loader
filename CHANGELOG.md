# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- フィールドマッピング画面で戻るボタンを押しても設定が保持される機能
  - Vuexストアでマッピング設定を永続化
  - 画面遷移時の自動保存機能
  - コンポーネントのアンマウント時にも設定を保存

### Changed
- FieldMapping.vueコンポーネントの改善
  - ストアから既存のマッピング設定を読み込むように変更
  - watcherを追加してリアルタイムでストアに同期
  - onBeforeUnmountフックで確実に設定を保存

## [1.0.0] - 2025-06-20

### Added
- CSV User Management System初回リリース
- CSVファイルアップロード機能
- フィールドマッピング機能
  - 複数フィールドの連結サポート
  - マッピング設定の保存と再利用
- ユーザー同期機能（追加・更新・削除）
- 同期プレビュー機能
- 包括的なログシステム
- Vue.js 3フロントエンド（Element Plus UI）
- Python Flaskバックエンド（AWS Lambda対応設計）

### Features
- CSVファイルの文字コード自動検出
- メールアドレスをキーとしたユーザー識別
- 必須フィールドの視覚的表示
- エラーハンドリングとユーザーフィードバック