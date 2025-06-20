import json
import os
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key


def lambda_handler(event, context):
    """
    マッピング設定の保存・読み込みを行うLambda関数
    """
    try:
        http_method = event.get('httpMethod', 'GET')
        
        if http_method == 'GET':
            return get_mappings(event, context)
        elif http_method == 'POST':
            return save_mapping(event, context)
        else:
            return {
                'statusCode': 405,
                'body': json.dumps({
                    'success': False,
                    'message': 'Method not allowed'
                })
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'message': f'エラーが発生しました: {str(e)}'
            }, ensure_ascii=False)
        }


def get_mappings(event, context):
    """保存済みマッピング設定を取得"""
    # 開発環境ではダミーデータを返す
    if os.environ.get('ENV') == 'development':
        dummy_mappings = [
            {
                'id': '1',
                'name': '標準フォーマット',
                'config': {
                    'email': 0,
                    'position': 3,
                    'department': 2
                },
                'createdAt': '2024-01-10T10:00:00Z'
            },
            {
                'id': '2',
                'name': '英語フォーマット',
                'config': {
                    'email': 0,
                    'position': 3,
                    'department': 2
                },
                'createdAt': '2024-01-15T14:30:00Z'
            }
        ]
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'mappings': dummy_mappings
            }, ensure_ascii=False)
        }
    
    # 本番環境ではDynamoDBから取得
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'csv-loader-mappings')
    table = dynamodb.Table(table_name)
    
    response = table.scan()
    mappings = response.get('Items', [])
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': True,
            'mappings': mappings
        }, ensure_ascii=False)
    }


def save_mapping(event, context):
    """マッピング設定を保存"""
    body = json.loads(event.get('body', '{}'))
    mapping_name = body.get('name')
    mapping_config = body.get('config')
    
    if not mapping_name or not mapping_config:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'success': False,
                'message': '設定名と設定内容が必要です'
            })
        }
    
    # 開発環境では成功レスポンスを返す
    if os.environ.get('ENV') == 'development':
        new_mapping = {
            'id': str(datetime.now().timestamp()),
            'name': mapping_name,
            'config': mapping_config,
            'createdAt': datetime.now().isoformat()
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'mapping': new_mapping
            }, ensure_ascii=False)
        }
    
    # 本番環境ではDynamoDBに保存
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'csv-loader-mappings')
    table = dynamodb.Table(table_name)
    
    item = {
        'id': str(datetime.now().timestamp()),
        'name': mapping_name,
        'config': mapping_config,
        'createdAt': datetime.now().isoformat()
    }
    
    table.put_item(Item=item)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': True,
            'mapping': item
        }, ensure_ascii=False)
    }