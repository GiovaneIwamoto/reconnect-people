import boto3
import time
import os

# Função responsável por retornar uma instância de cliente do Amazon S3
def amazon_s3():
    # Retorna uma instância de cliente do Amazon S3
    return boto3.client('s3')

# Função responsável por armazenar uma face no bucket S3
def save_face_to_s3(face, path):
    # Recupera nome do bucket S3 armazenado nas variáveis de ambiente
    aws_s3_bucket_name = os.environ['AWS_S3_BUCKET_NAME']

    # Busca o timestamp atual
    timestamp = int(time.time() * 1000)
    # Define a chave do arquivo no S3
    key = 'banco-de-' + path + '/face-'+ str(timestamp) + '.png'

    # Inicia o cliente do Amazon S3
    amazon_s3_client = amazon_s3()
    # Armazena imagem no S3
    amazon_s3_client.put_object(Bucket=aws_s3_bucket_name, Key=key, Body=face.getvalue())

    # Retorna o timestamp
    return timestamp

# Função responsável por salvar o áudio gerado pelo Amazon Polly no Amazon S3
def save_audio_to_s3(path, audio_key, audio_content):
    # Recupera nome do bucket S3 armazenado nas variáveis de ambiente
    aws_s3_bucket_name = os.environ['AWS_S3_BUCKET_NAME']

    # Monta o caminho e nome para o arquivo de áudio a ser salvo
    key = 'audios/' + path + '/instruction-'+ audio_key + '.mp3'

    # Inicia o cliente do Amazon S3
    amazon_s3_client = amazon_s3()

    # Armazena áudio no S3
    amazon_s3_client.put_object(
        Bucket=aws_s3_bucket_name,
        Key=key,
        Body=audio_content.encode(),
        ContentType='audio/mpeg',
    )

    pre_signed_url = amazon_s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': aws_s3_bucket_name,
            'Key': key
        },
        ExpiresIn=120
    )

    # Retorna URL para o áudio
    return pre_signed_url