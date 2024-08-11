from functions.store_face.twilio import retrieve_twilio_image

import boto3
import os

# Função responsável por retornar uma instância de cliente do Amazon Rekognition
def amazon_rekognition():
    # Retorna uma instância de cliente do Amazon Rekognition
    return boto3.client('rekognition')

# Função responsável por receber o link da imagem e retornar o bounding box da face detectada
def extract_bounding_box(media_url):
    # Inicia o cliente do Amazon Rekognition
    amazon_rekognition_client = amazon_rekognition()

    # Faz download da imagem
    image = retrieve_twilio_image(media_url)

    # Detecta face na imagem
    detected_faces = amazon_rekognition_client.detect_faces(
        Image = {
            'Bytes': image
        }
    )

    if len(detected_faces['FaceDetails']) != 1:
        return 400

    # Obtém bounding box da face detectada
    bounding_box = detected_faces['FaceDetails'][0]['BoundingBox']
    
    # Retorna valores do bounding box
    return bounding_box

# Função responsável por salvar a face em uma collection do Amazon Rekognition
def save_face_to_collection(key, path):
    # Inicia o cliente do Amazon Rekognition
    amazon_rekognition_client = amazon_rekognition()

    # Recupera nome do bucket e da coleção armazenados como variáveis de ambiente
    aws_s3_bucket_name = os.environ['AWS_S3_BUCKET_NAME']

    if path == 'desaparecidos':
        collection_id = os.environ['DESAPARECIDOS_COLLECTION_ID']
    else:
        collection_id = os.environ['LOCALIZADOS_COLLECTION_ID']

    # Lista coleções existentes no Amazon Rekognition
    collections_response = amazon_rekognition_client.list_collections()

    # Verifica se já existe a coleção para armazenar as faces dos desaparecidos
    if collection_id not in collections_response['CollectionIds']:
        # Se não existe tal coleção, cria
        amazon_rekognition_client.create_collection(
            CollectionId=collection_id,
        )

    try:
        # Adiciona face a collection do Amazon Rekognition
        amazon_rekognition_response = amazon_rekognition_client.index_faces(
            CollectionId=collection_id,
            Image={
                'S3Object': {
                    'Bucket': aws_s3_bucket_name,
                    'Name': 'banco-de-' + path + '/face-'+ str(key) + '.png'
                }
            },
        )
        
        # Retorna ID da face armazenada na collection do Amazon Rekognition
        return amazon_rekognition_response['FaceRecords'][0]['Face']['FaceId']
    except:
        # Retorna None em caso de falha ao adicionar face a collection do Amazon Rekognition
        return None

# Função responsável por fazer o reconhecimento facial em uma coleção do Amazon Rekognition
def find_match(collection_id, image):
    # Inicia o cliente do Amazon Rekognition
    amazon_rekognition_client = amazon_rekognition()

    try:
        # Realiza o reconhcimento facial comparando imagem de entrada com todas as faces presentes na coleção
        face_matches = amazon_rekognition_client.search_faces_by_image(
            CollectionId=collection_id,
            Image={
                'Bytes': image
            },
        )
    except (amazon_rekognition_client.exceptions.InvalidS3ObjectException, amazon_rekognition_client.exceptions.ResourceNotFoundException) as error:
        # Se houver erro no reconhecimento facial retorna uma lista vazia
        face_matches = {
            'FaceMatches': []
        }

    # Retorna se pelo menos uma face correspondente
    return len(face_matches['FaceMatches']) > 0