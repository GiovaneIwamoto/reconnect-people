from functions.manage_records.amazon_dynamodb import save_record, retrieve_record

import os

def main(event, context):
    # Recupera nome das tabelas do Amazon DynamoDB armazenadas nas variáveis de ambiente
    disappeared_table_name = os.environ['DISAPPEARED_TABLE_NAME']
    found_table_name = os.environ['FOUND_TABLE_NAME']

    # Recupera dados do registro do corpo da requisição
    record_data = event.get('RecordData', {})
    record_type = event.get('Path', '')
    protocol_number = event.get('protocol_number', '')
    current_lex_session_id = event.get('amazon_lex_session_id', '')

    # se a operação for de exclusão 
    if 'protocol_number' in event:
        try:
            # Busca registro no banco de dados de desaparecidos
            record = retrieve_record(protocol_number, disappeared_table_name)

            """
            
            # FIXME: Implementar busca na tabela de localizados. Ainda não implementar pois a tabela de localizados ainda não foi criada
            
            # Se o registro não for encontrado na tabela de desaparecidos, busca na tabela de localizados
            #if record is None:
                #record = retrieve_record(protocol_number, found_table_name)
            
            """
            
            # Se o registro não for encontrado em nenhuma das tabelas, retorna 404
            if record is None:
                return {
                    'statusCode': 404,
                    'body': {
                        'message': 'Record not found'
                    }
                }
            
            # Se o registro for encontrado, retorna o registro
            else:
                return {
                    'statusCode': 200,
                    'body': {
                        'record': record
                    }
                }
        
        # Se ocorrer algum erro, retorna 500
        except Exception as e:
            print(f"Error in retrieve_record function: {e}")
            return {
                'statusCode': 500,
                'body': {
                    'message': 'Internal server error'
                }
            }
    else:
        table_name = disappeared_table_name if record_type == 'desaparecidos' else found_table_name

        # Verifica se existe os dados para registro no corpo da requisição
        if 'RecordData' in event:
            # Salva registro de desaparecimento no banco de dados
            record_id = save_record(record_type, record_data, table_name)

            # Retorna o ID do registro no banco de dados
            return {
                'record_id': record_id
            }
        
        # Retorna o ID do registro no banco de dados como None caso um erro tenha ocorrido
        return {
            'record_id': None
        }

