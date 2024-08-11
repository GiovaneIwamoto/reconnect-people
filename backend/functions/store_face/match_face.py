from functions.store_face.amazon_rekognition import find_match
from functions.store_face.twilio import retrieve_twilio_image

import os

def match_face(media_url):
    # Recupera nome das coleções do Amazon Rekognition armazenadas nas variáveis de ambiente
    desaparecidos_collection_id = os.environ['DESAPARECIDOS_COLLECTION_ID']
    localizados_collection_id = os.environ['LOCALIZADOS_COLLECTION_ID']

    try:
        # Faz download da imagem
        image = retrieve_twilio_image(media_url)

        # Verifica se existe face correspondente na coleção de desaparecidos
        disappeared_match = find_match(desaparecidos_collection_id, image)
        # Verifica se existe face correspondente na coleção de localizados
        found_match = find_match(localizados_collection_id, image)

        # Retorna se há uma correspondência nas respectivas coleções do Amazon Rekognition
        return {
            'in_disappeared': disappeared_match,
            'in_found': found_match
        }
    except:
        # Retorna None caso tenha ocorrido algum erro no reconhecimento facial
        return None
