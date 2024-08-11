from datetime import datetime, timezone, timedelta

import boto3
import os

# Função responsável por retornar uma instância de cliente do Amazon DynamoDB
def amazon_dynamodb():
    # Retorna uma instância de cliente do Amazon DynamoDB
    return boto3.client('dynamodb')

# Função responsável por salvar um registro no DynamoDB
def save_record(record_type, record_data, table_name):
    # Inicia o cliente do Amazon DynamoDB
    amazon_dynamodb_client = amazon_dynamodb()

    # Recupera date e hora atual no timezone de America/Sao_Paulo
    timestamp = datetime.now(timezone(timedelta(hours=-3.0))).isoformat()

    if record_type == 'desaparecidos':
        # Cria objeto que representa documento a ser inserido na tabela do DynamoDB
        item = {
            'desaparecido_id': {
                'S': '#D' + record_data['record_id']
            },
            'nome_completo_desaparecido': {
                'S': record_data['nome_completo_desaparecido']
            },
            'data_nascimento_desaparecido': {
                'S': record_data['data_nascimento_desaparecido']
            },
            'sexo_desaparecido': {
                'S': record_data['sexo_desaparecido']
            },
            'descricao_fisica_desaparecido': {
                'S': record_data['descricao_fisica_desaparecido']
            },
            's3_face_key': {
                'S': 'face-'+ record_data['record_id'] + '.png'
            },
            'collection_face_id': {
                'S': record_data['face_id']
            },
            'nome_solicitante': {
                'S': record_data['nome_solicitante']
            },
            'email_solicitante': {
                'S': record_data['email_solicitante']
            },
            'telefone_solicitante': {
                'S': record_data['telefone_solicitante']
            },
            'localizado': {
                'BOOL': record_data['localizado']
            },
            'created_at': {
                'S': timestamp
            },
            'updated_at': {
                'S': timestamp
            },
        }
    else:
        # Cria objeto que representa documento a ser inserido na tabela do DynamoDB
        item = {
            'localizado_id': {
                'S': '#L' + record_data['record_id']
            },
            'nome_completo_localizado': {	
                'S': record_data['nome_completo_localizado']
            },
            'idade_estimada_localizado': {
                'N': record_data['idade_estimada_localizado']
            },
            'sexo_localizado': {
                'S': record_data['sexo_localizado']
            },
            'descricao_fisica_localizado': {
                'S': record_data['descricao_fisica_localizado']
            },
            's3_face_key': {
                'S': 'face-'+ record_data['record_id'] + '.png'
            },
            'collection_face_id': {
                'S': record_data['face_id']
            },
            'nome_solicitante': {
                'S': record_data['nome_solicitante']
            },
            'email_solicitante': {
                'S': record_data['email_solicitante']
            },
            'telefone_solicitante': {
                'S': record_data['telefone_solicitante']
            },
            'desaparecido': {
                'BOOL': record_data['desaparecido']
            },
            'created_at': {
                'S': timestamp
            },
            'updated_at': {
                'S': timestamp
            },
        }

    try:
        # Salva documento na tabela do DynamoDB
        amazon_dynamodb_client.put_item(
            TableName=table_name,
            Item=item
        )

        # Retorna ID de referência do registro no DynamoDB
        return '#D' + record_data['record_id'] if record_type == 'desaparecidos' else '#L' + record_data['record_id']
    except:
        # Caso ocorra algum erro durante o armazenamento do documento retorna None
        return None
    
# Função responsável por buscar um registro no DynamoDB
def get_record(protocol_number, table_name):
    amazon_dynamodb_client = amazon_dynamodb()
    key = {'desaparecido_id': {'S': protocol_number}}

    try:
        response = amazon_dynamodb_client.get_item(
            TableName=table_name,
            Key=key
        )
        if 'Item' in response:
            return response['Item']
        else:
            return None
    except Exception as e:
        print(f"Error retrieving record: {e}")
        return None

# Função responsável por excluir um registro no DynamoDB
def delete_record(protocol_number, table_name):
    amazon_dynamodb_client = amazon_dynamodb()
    key = {'desaparecido_id': {'S': protocol_number}}

    try:
        amazon_dynamodb_client.delete_item(
            TableName=table_name,
            Key=key
        )
        return True
    except Exception as e:
        print(f"Error deleting record: {e}")
        return False
    
# Função responsável por buscar um registro no DynamoDB
def retrieve_record(protocol_number, table_name):
    # Inicia o cliente do Amazon DynamoDB
    amazon_dynamodb_client = amazon_dynamodb()

    # Cria a chave primária do item que será buscado
    key = {'desaparecido_id': {'S': protocol_number}}

    try:
        # Busca documento na tabela do DynamoDB
        response = amazon_dynamodb_client.get_item(
            TableName=table_name,
            Key=key
        )
        
        # Se o item foi encontrado, retorna o item
        if 'Item' in response:
            print(f"Record found: {response['Item']}")
            return response['Item']
        
        # Se o item não foi encontrado, retorna None
        else:
            return None
    
    # Se ocorrer algum erro, imprime o erro e retorna None
    except Exception as e:
        print(f"Error retrieving record: {e}")
        return None