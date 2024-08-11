import boto3
import json

# Função responsável por retornar uma instância de cliente do AWS Lambda
def aws_lambda():
    # Retorna uma instância de cliente do AWS Lambda
    return boto3.client('lambda')

# Função responsável por invocar uma função lambda
def trigger_lambda_function(function_name, lambda_function_request_body):
    # Inicia o cliente da AWS Lambda
    lambda_client = aws_lambda()

    # Invoca função lambda passando o nome da função e os parâmetros da requisição
    lambda_function_response = lambda_client.invoke(
        FunctionName=function_name,
        Payload=json.dumps(lambda_function_request_body).encode(),
    )

    # Retorna resposta da função lambda
    return lambda_function_response