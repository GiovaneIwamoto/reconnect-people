from functions.main.aws_lambda import trigger_lambda_function
from functions.main.amazon_polly import convert_instructions_to_audio
from functions.main.amazon_s3 import save_audio_to_s3

import json

# Função responsável por checar o estado atual da sessão do usuário no chatbot
def check_triggers(user_session_info, request_body):
    # Recupera nome da intent, ação e possível slot a ser coletado da sessão do usuário no chatbot
    intent_name = user_session_info.get('sessionState', {}).get('intent', {}).get('name', '')
    dialog_action = user_session_info.get('sessionState', {}).get('dialogAction', {}).get('type', '')
    slot_to_elict = user_session_info.get('sessionState', {}).get('dialogAction', {}).get('slotToElicit', '')
    
    # Recupera número de sessão whatsapp do usuário no Amazon Lex
    session_id = user_session_info['sessionId']
    user_session_info_whatsapp_number = session_id.replace('whatsapp:', '')

    # Verifica se o chatbot está esperando o envio da imagem pelo usuário como próxima ação
    if (intent_name == 'RegistrarDesaparecimento' or intent_name == 'RegistrarLocalizado') and dialog_action == 'ElicitSlot' and slot_to_elict == 'Foto':
        # Recupera número de imagens e url da primeira imagem que o usuário enviou
        num_media = request_body.get('NumMedia', 0)
        media_url = request_body.get('MediaUrl0', '')

        # Verifica se foi enviada somente uma imagem (esperado)
        if num_media == '1':
            # Monta corpo da requisição para uma função lambda com o link da imagem
            match_face_request_body = {
                'MediaUrl': media_url
            }

            # Monta corpo da requisição para uma função lambda com o link da imagem
            store_face_request_body = {
                'UploadType': 'Image',
                'MediaUrl': media_url,
                'Path': 'desaparecidos' if intent_name == 'RegistrarDesaparecimento' else 'localizados'
            }

            # Dispara função lambda para armazenar a foto da pessoa desaparecida em um bucket do S3
            store_face_response = trigger_lambda_function('dev-store-face-lambda', store_face_request_body)
            store_face_status_code = store_face_response.get('ResponseMetadata', {}).get('HTTPStatusCode', '')

            # Verifica se houve erro na execução da função lambda
            if store_face_status_code != 200:
                return 500, None
            
            # Recupera corpo da resposta da função lambda
            store_face_payload = json.loads(store_face_response.get('Payload', b'{}').read())


            if store_face_payload.get('code') == 204:
                return 204, None
            elif store_face_payload.get('code') == 500:
                return 500, None
            elif store_face_payload.get('code') == 400:
                return 400, None
            
            # Captura valores dos slots preenchidos pelo usuário
            slots = user_session_info.get('sessionState', {}).get('intent', {}).get('slots', {})
            
            if intent_name == 'RegistrarDesaparecimento':
                # Constroi objeto com as informações do desaparecido e solicitante
                record_data = {
                    'record_id': store_face_payload.get('key'), # Utiliza o ID do rosto armazenado no banco de dados
                    'nome_solicitante': slots.get('NomeUsuario', {}).get('value', {}).get('interpretedValue', ''),
                    'email_solicitante': slots.get('EmailUsuario', {}).get('value', {}).get('interpretedValue', ''),
                    'telefone_solicitante': user_session_info_whatsapp_number,
                    'nome_completo_desaparecido': slots.get('NomeCompletoDesaparecido', {}).get('value', {}).get('interpretedValue', ''),
                    'data_nascimento_desaparecido': slots.get('DataNascimentoDesaparecido', {}).get('value', {}).get('interpretedValue', ''),
                    'sexo_desaparecido': slots.get('SexoDesaparecido', {}).get('value', {}).get('interpretedValue', ''),
                    'descricao_fisica_desaparecido': slots.get('DescricaoDesaparecido', {}).get('value', '').get('interpretedValue', ''),
                    'face_id': store_face_payload.get('face_id'),
                    'localizado': store_face_payload.get('in_found')
                }
            else:
                # Constroi objeto com as informações do localizado e solicitante
                record_data = {
                    'record_id': store_face_payload.get('key'), # Utiliza o ID do rosto armazenado no banco de dados
                    'nome_solicitante': slots.get('NomeUsuario', {}).get('value', {}).get('interpretedValue', ''),
                    'email_solicitante': slots.get('EmailUsuario', {}).get('value', {}).get('interpretedValue', ''),
                    'telefone_solicitante': user_session_info_whatsapp_number,
                    'nome_completo_localizado': slots.get('NomeCompletoLocalizado', {}).get('value', {}).get('interpretedValue', ''),
                    'idade_estimada_localizado': slots.get('IdadeLocalizado', {}).get('value', {}).get('interpretedValue', ''),
                    'sexo_localizado': slots.get('SexoLocalizado', {}).get('value', {}).get('interpretedValue', ''),
                    'descricao_fisica_localizado': slots.get('DescricaoLocalizado', {}).get('value', '').get('interpretedValue', ''),
                    'face_id': store_face_payload.get('face_id'),
                    'desaparecido': store_face_payload.get('in_disappeared')
                }

            # Monta corpo da requisição para uma função lambda com os dados para registro de um desaparecido
            store_record_request_body = {
                'RecordData': record_data,
                'Path': 'desaparecidos' if intent_name == 'RegistrarDesaparecimento' else 'localizados'
            }

            # Chama a função lambda que armazena os dados da pessoa desaparecida no DynamoDB
            store_record_response = trigger_lambda_function('dev-manage-records-lambda', store_record_request_body)
            store_record_status_code = store_record_response.get('ResponseMetadata', {}).get('HTTPStatusCode', '')
            store_record_payload = json.loads(store_record_response.get('Payload', b'{}').read())

            # Monta corpo da requisição para uma função lambda com o tipo de prompt a ser gerado e a chave que deve ser utilizada para salvar o áudio no bucket do S3
            generate_instructions_request_body = {
                'prompt_type': 'missing_person' if intent_name == 'RegistrarDesaparecimento' else 'notification',
            }
            
            # Chama a função lambda que gera as instruções utilizando o Amazon Bedrock e converte em áudio com Amazon Polly
            generate_instructions_response = trigger_lambda_function('dev-generate-instructions-lambda', generate_instructions_request_body)
            generate_instructions_status_code = generate_instructions_response.get('ResponseMetadata', {}).get('HTTPStatusCode', '')
            generate_instructions_payload = json.loads(generate_instructions_response.get('Payload', b'{}').read())

            print(generate_instructions_payload)

            audio_content = convert_instructions_to_audio(generate_instructions_payload.get('bedrock_response'))

            audio_link = save_audio_to_s3(
                'desaparecidos' if intent_name == 'RegistrarDesaparecimento' else 'localizados',
                store_face_payload.get('key'),
                audio_content
            )

            feedback_message = None

            if intent_name == 'RegistrarDesaparecimento' and store_face_payload.get('in_found', '') == True:
                feedback_message = '🚨 *O desaparecido que foi registrado já foi encontrado!* 🚨\nVocê receberá as instruções em breve através de um dos meios de comunicação que você nos informou.'

            if intent_name == 'RegistrarLocalizado' and store_face_payload.get('in_disappeared', '') == True:
                feedback_message = '🚨 *Há um registro de desaparecimento para a pessoa localizada!* 🚨\nVocê receberá as instruções em breve através de um dos meios de comunicação que você nos informou.'

            # Se houve sucesso na chamada das funções lambdas anteriores, retorna o ID do registro no DynamoDB e o link para o áudio de instruções armazenado no S3
            return 201, {
                'record_id': store_record_payload['record_id'],
                'instruction_audio_link': audio_link,
                'message': feedback_message
            }
        else:
            # Retorna 400 caso não tenha sido enviada a quantidade esperada de imagens pelo usuário
            return 400, None
    
    # Verifica se o chatbot está esperando o número do protocolo do registro de desaparecimento para verificar o status
    if intent_name == 'AcompanharStatus' and dialog_action == 'ElicitSlot' and slot_to_elict == 'NumeroProtocolo':
        num_protocolo_received = request_body.get('Body', '')
        num_protocolo_request_body = {'protocol_number': num_protocolo_received}

        if num_protocolo_received == 'Menu':
            return 200, None

        # Chama a função lambda que verifica o status do registro de desaparecimento
        check_status_response = trigger_lambda_function('dev-manage-records-lambda', num_protocolo_request_body)
        
        # Carrega payload da resposta da função lambda e verifica o status do registro de desaparecimento
        check_status_payload = json.loads(check_status_response.get('Payload', b'{}').read())
        check_status_status_code = check_status_payload.get('statusCode', '')

        # Verifica se obteve sucesso na execução da função lambda
        if check_status_status_code == 200:
            check_status_body = check_status_payload.get('body', '')            
            check_status_record = check_status_body.get('record', '')
            check_status_localizado = check_status_record.get('localizado', '')

            # Verifica se o registro foi localizado e se o status é true
            if check_status_localizado.get('BOOL','') == True:
                return 201, {'status_localizado': 'true'}
            
            # Encontrou registro porém pessoa segue com status de desaparecida
            else:
                return 201, {'status_localizado': 'false'}
            
        # Protocolo não encontrado
        if check_status_status_code == 404:
            return 404, None
        
        # Erro interno
        if check_status_status_code == 500:
            return 500, None
            
    # Retorna 200 caso o fluxo da sessão não necessite disparar outras lambdas
    return 200, None