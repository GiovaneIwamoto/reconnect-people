from functions.store_face.amazon_rekognition import extract_bounding_box, save_face_to_collection
from functions.store_face.crop import crop_image
from functions.store_face.amazon_s3 import save_face_to_s3, save_audio_to_s3
from functions.store_face.match_face import match_face

def main(event, context):
    upload_type = event.get('UploadType', '')

    if upload_type == 'Image':
        # Recupera url da imagem do corpo da requisição
        media_url = event.get('MediaUrl', '')
        path = event.get('Path', '')
        
        match_face_response = match_face(media_url)

        if (path == 'desaparecidos' and not match_face_response.get('in_disappeared')) or (path == 'localizados' and not match_face_response.get('in_found')):
            try:
                # Extrai bounding box da face da pessoa na imagem
                bounding_box = extract_bounding_box(media_url)

                if bounding_box == 400:
                    return {
                        'code': 400,
                        'key': None,
                        'face_id': None
                    }

                # Recorta a face da pessoa na imagem
                face = crop_image(media_url, bounding_box)
                # Salva a face recotada no S3
                key = save_face_to_s3(face, path)
                # Adiciona a face da pessoa em uma coleção do Amazon Rekognition
                face_id = save_face_to_collection(key, path)

                # Retorna chave do arquivo armazenado no S3 e ID da face na coleção do Amazon Rekognition
                return {
                    'code': 201,
                    'key': str(key),
                    'face_id': face_id,
                    'in_disappeared': match_face_response.get('in_disappeared'),
                    'in_found': match_face_response.get('in_found')
                }
            except:
                # Caso ocorra um erro ao salvar a face retorna chave do arquivo armazenado no S3 e ID da face na coleção do Amazon Rekognition como None
                return {
                    'code': 500,
                    'key': None,
                    'face_id': None
                }
        else:
            return {
                'code': 204,
                'key': None,
                'face_id': None
            }
    elif upload_type == 'Audio':
        audio_key = event.get('AudioKey', '')
        audio_content = event.get('AudioContent', '')
        path = event.get('Path', '')

        # Executa função responsável por salvar áudio no bucket do S3
        audio_link = save_audio_to_s3(path, audio_key, audio_content)

        # Retorna o link do áudio no S3 como resposta
        return {
            'audio_link': audio_link
        }