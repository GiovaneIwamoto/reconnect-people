from twilio.rest import Client
from twilio.request_validator import RequestValidator

import os

# Função responsável por retornar uma instância do client da Twilio
def twilio():
    # Define as credenciais da Twilio armazenadas como variáveis de ambiente
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]

    # Retorna client da Twilio
    return Client(account_sid, auth_token)

# Função responsável por validar se é uma requisição válida
def is_twilio_valid_request(twilio_signature, request_body):
    # Define as credenciais da Twilio armazenadas como variáveis de ambiente
    auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    # Recupera o endereço do endpoint do chatbot armazenado como variáveis de ambiente
    endpoint = os.environ["API_GATEWAY_URL"]

    # Instancia o validador da Twilio
    validator = RequestValidator(auth_token)

    # Retorna se é uma requisição válida ou não
    return validator.validate(endpoint, request_body, twilio_signature)