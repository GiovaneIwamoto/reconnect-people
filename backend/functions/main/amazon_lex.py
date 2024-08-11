import boto3
import os

# Função responsável por retornar uma instância de cliente do Amazon Lex
def amazon_lex():
    # Retorna uma instância de cliente do Amazon Lex
    return boto3.client('lexv2-runtime')

# Função responsável por retornar as credenciais do chatbot criado com Amazon Lex
def retrieve_chatbot_info():
    # Recupera as credenciais armazenadas como variáveis de ambiente
    amazon_lex_bot_id = os.environ['AMAZON_LEX_BOT_ID']
    amazon_lex_bot_alias_id = os.environ['AMAZON_LEX_BOT_ALIAS_ID']
    amazon_lex_locale_id = os.environ['AMAZON_LEX_LOCALE_ID']

    # Retorna dicionário com as informações de acesso ao Amazon Lex
    return {
        'botId': amazon_lex_bot_id,
        'botAliasId': amazon_lex_bot_alias_id,
        'localeId': amazon_lex_locale_id
    }

# Função responsável por retornar a sessão do usuário no Amazon Lex
def get_lex_user_session(amazon_lex_session_id):
    # Inicia o cliente do Amazon Lex
    amazon_lex_client = amazon_lex()
    # Recupera credenciais de acesso ao Amazon Lex
    chatbot_info = retrieve_chatbot_info()

    try:
        # Busca sessão ativa do usuário no Amazon Lex
        user_session_info = amazon_lex_client.get_session(
            **chatbot_info,
            sessionId=amazon_lex_session_id
        )
    except amazon_lex_client.exceptions.ResourceNotFoundException as error:
        # Define sessão como None caso não exista sessão ativa
        user_session_info = None

    # Retorna sessão do usuário
    return user_session_info

# Função responsável por excluir a sessão do usuário no Amazon Lex
def delete_lex_user_session(amazon_lex_session_id):
    # Inicia o cliente do Amazon Lex
    amazon_lex_client = amazon_lex()
    # Recupera credenciais de acesso ao Amazon Lex
    chatbot_info = retrieve_chatbot_info()

    # Exclui sessão ativa do usuário
    amazon_lex_client.delete_session(
        **chatbot_info,
        sessionId=amazon_lex_session_id
    )

# Função responsável por encaminhar a mensagem do usuário para o Amazon Lex
def forward_user_input_to_lex(amazon_lex_session_id, user_input):
    # Inicia o cliente do Amazon Lex
    amazon_lex_client = amazon_lex()
    # Recupera credenciais de acesso ao Amazon Lex
    chatbot_info = retrieve_chatbot_info()

    # Envia mensagem do usuário para o Amazon Lex
    amazon_lex_response = amazon_lex_client.recognize_text(
        **chatbot_info,
        sessionId=amazon_lex_session_id,
        text=user_input
    )

    # Retorna a resposta do Amazon Lex com os dados da sessão após o consumo da mensagem do usuário
    return amazon_lex_response

# Função responsável por adicionar um atributo de sessão a sessão atual do usuário
def set_lex_session_attribute(lex_session, session_attribute):
    # Inicia o cliente do Amazon Lex
    amazon_lex_client = amazon_lex()
    # Recupera credenciais de acesso ao Amazon Lex
    chatbot_info = retrieve_chatbot_info()

    # Recupera chave e valor do atributo a ser inserido
    session_attribute_key = list(session_attribute.keys())[0]
    session_attribute_value = session_attribute[session_attribute_key]

    # Cria objeto para inserção de novo atributo de sessão
    amazon_lex_input = {
        'sessionId': lex_session['sessionId'],
        'sessionState': {
            'sessionAttributes': {
                session_attribute_key: session_attribute_value
            }
        }

    }

    # Injeta novo atributo de sessão na sessão atual do usuário
    amazon_lex_client.put_session(
        **chatbot_info,
        **amazon_lex_input
    )