from functions.main.twilio import twilio, is_twilio_valid_request
from functions.main.amazon_lex import get_lex_user_session, delete_lex_user_session, forward_user_input_to_lex, set_lex_session_attribute
from functions.main.triggers import check_triggers

import json
import base64
import urllib.parse
import boto3
import os
import time

def main(event, context):
    # Recupera assinatura da requisição da Twilio
    twilio_signature = event.get('headers', {}).get('x-twilio-signature', '')

    # Recupera corpo da requisição da Twilio
    request_body = dict(
        urllib.parse.parse_qsl(
            base64.b64decode(
                event.get('body', '\\{\\}')
            ).decode()
        )
    )

    # Adiciona a chave 'Body' para casos onde foi enviado uma imagem sem mensagem
    if 'Body' not in request_body:
        request_body['Body'] = ''

    # Valida autenticidade da requisição vindo da Twilio
    if not is_twilio_valid_request(twilio_signature, request_body):
        # Bloqueia requisição
        return {
            'statusCode': 401,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps(
                {
                    'error': 'Unauthorized'
                }
            )
        }
    
    # Instancia o Twilio Client
    twilio_client = twilio()

    # Recupera número de sessão do usuário no Amazon Lex (número de telefone do usuário)
    amazon_lex_session_id = request_body.get('From').replace('+', '')
    # Extrai mensagem enviada pelo usuário
    whatsapp_user_input = request_body['Body']
    # Link do áudio a ser enviado para o usuário, por padrão nenhum
    audio_link = None

    # Busca detalhes da sessão do usuário no Amazon Lex
    user_session_info = get_lex_user_session(amazon_lex_session_id)
    
    # Verifica se é o comando para encerrar a sessão do Amazon Lex (utilizado apenas durante os testes do chatbot)
    if user_session_info != None and whatsapp_user_input.strip().lower() == '#encerrar':
        delete_lex_user_session(amazon_lex_session_id)

        boto3.client('rekognition').delete_collection(CollectionId=os.environ['DESAPARECIDOS_COLLECTION_ID'])
        boto3.client('rekognition').delete_collection(CollectionId=os.environ['LOCALIZADOS_COLLECTION_ID'])

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    
    # Verifica se existe uma sessão ativa no chatbot para o usuário
    if user_session_info != None:
        # Checa se é necessário disparar alguma função lambda baseado nos dados da sessão atual do usuário
        trigger_response_code, data = check_triggers(user_session_info, request_body)

        # Verifica se código de resposta da checagem de sessão não é 200
        if trigger_response_code != 200:
            # Passa como entrada para o Amazon Lex a resposta da checagem de sessão
            whatsapp_user_input = trigger_response_code

            # Verifica se um registro de desaparecimento foi realizado com sucesso
            if trigger_response_code == 201:
                # Chama função para guardar o número do protocolo do registro de desaparecimento como um atributo de sessão na sessão do usuário
                set_lex_session_attribute(user_session_info, data)
                
                # Atribui link do áudio a ser enviado para o usuário com as instruções
                if 'instruction_audio_link' in data:
                    audio_link = data['instruction_audio_link']
    
    # Encaminha mensagem do usuário ou resposta de uma função lambda para o Amazon Lex
    amazon_lex_response = forward_user_input_to_lex(amazon_lex_session_id, str(whatsapp_user_input))

    # Percorre a lista de mensagens retornados pelo Amazon Lex
    for message in amazon_lex_response['messages']:
        # Envia mensagem do Amazon Lex para o usuário por meio da Twilio
        twilio_client.messages.create(
            from_=request_body.get('To'),
            body=message['content'].replace('\\n', '\n'),
            to=request_body.get('From')
        )

        # Define um delay de envio das mensagens para evitar que as mensagens cheguem em ordem incorreta
        time.sleep(0.5)

    # Verifica se há o link de um áudio
    # if audio_link != None:
    #     # Envia áudio para o usuário através da Twilio
    #     twilio_client.messages.create(
    #         from_=request_body.get('To'),
    #         media_url=audio_link,
    #         to=request_body.get('From')
    #     )

    if data['message'] != None:
        time.sleep(5)
        twilio_client.messages.create(
            from_=request_body.get('To'),
            body=data['message'],
            to=request_body.get('From')
        )

    # Finaliza requisição
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        }
    }