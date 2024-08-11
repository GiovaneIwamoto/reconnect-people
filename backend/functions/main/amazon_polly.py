import boto3

# Função responsável por converter instruções em texto gerada a partir do Amazon Bedrock em áudio usando Amazon Polly
def convert_instructions_to_audio(instructions):
    # Inicia o cliente do Amazon Polly
    polly_client = boto3.client('polly')

    try:
        # Sintetiza texto em áudio
        response = polly_client.synthesize_speech(
            Engine='neural',
            LanguageCode='pt-BR',
            OutputFormat='mp3',
            Text='<speak>' + instructions + '</speak>',
            VoiceId='Vitoria',  
            TextType='ssml'
        )

        # Retorna conteúdo do áudio gerado
        return response['AudioStream'].read()
    except:
        # Retorna None caso tenha ocorrido uma falha na geração do áudio
        return None