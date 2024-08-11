import boto3
import json

# Inicia o cliente do Amazon Bedrock
bedrock_client = boto3.client('bedrock-runtime')

# Função responsável por gerar instruções a partir de IA Generativa
def generate_instructions(prompt):
    # Define estrutura de entrada do Amazon Bedrock
    native_request = {
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 300,
            "temperature": 0.9,
            "topP": 0.9
        },
    }

    # Converte dicionário em uma string JSON
    request = json.dumps(native_request)

    try:
        # Define o modelo a ser utilizado no Amazon Bedrock
        model_id = "amazon.titan-text-premier-v1:0"

        # Invoca modelo do Amazon Bedrock fornecendo as informações anteriores como entrada
        response = bedrock_client.invoke_model(modelId=model_id, body=request)

        # Converte string JSON em dicionário
        model_response = json.loads(response["body"].read())

        # Recupera resposta fornecida pelo Amazon Bedrock
        response_text = model_response["results"][0]["outputText"]
        # Retira quebras de linha da resposta
        response_text = response_text.replace('\n', '<break/>').replace("\"", "")
        
        # Retorna texto gerado pelo Amazon Bedrock
        return response_text
    except:
        # Retorna None caso ocorra um erro na geração do texto
        return None
