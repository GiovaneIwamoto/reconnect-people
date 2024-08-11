import os
import base64
import requests

# Função responsável por baixar imagem armazenada na Twilio
def retrieve_twilio_image(media_url):
    # Recupera credenciais da Twilio armazenadas nas variáveis de ambiente
    twilio_account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    twilio_auth_token = os.environ["TWILIO_AUTH_TOKEN"]

    # Gera token de acesso para download da imagem na twilio
    twilio_token = base64.b64encode(
        f'{twilio_account_sid}:{twilio_auth_token}'.encode()
    ).decode()

    # Faz requisição para download da imagem
    image_response = requests.get(
        media_url,
        headers={'Authorization': 'Basic ' + twilio_token}
    )

    # Retorna conteúdo da imagem
    return image_response.content