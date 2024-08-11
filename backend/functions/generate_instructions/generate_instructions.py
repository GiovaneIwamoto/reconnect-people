from functions.generate_instructions.amazon_bedrock import generate_instructions

def main(event, context):
    # Verifica o tipo de prompt baseado na entrada do evento
    prompt_type = event.get('prompt_type', '')

    # Verifica se devemos utilizar um prompt de instruções para o registro de um desaparecido ou de um localizado
    if prompt_type == 'missing_person':
        path = 'desaparecidos'
        prompt = '''
            Você é um especialista em segurança pública e apoio a familiares de pessoas desaparecidas. Forneça uma dica clara e prática para alguém que acabou de registrar o desaparecimento de uma pessoa, conhecida ou não. 
            A dica deve ser empática e fornecer orientações sobre os próximos passos importantes a serem tomados, recursos de apoio, rede de suporte, acompanhamento de longo prazo, apoio emocional inicial, entre outros.
            Lembre-se de ser encorajador e oferecer suporte emocional.
        '''
    elif prompt_type == 'notification':
        path = 'localizados'
        prompt = '''
            Você é um assistente de emergência virtual que fornece orientações detalhadas e claras para situações de emergência. 
            Um usuário acaba de notificar a localização de uma pessoa desaparecida através de um sistema de registro de desaparecidos. 
            Gere um conjunto de instruções de emergência que o usuário deve seguir imediatamente. 
            As instruções devem ser diretas, empáticas e abranger as ações necessárias para garantir a segurança da pessoa encontrada. 
            Considere os seguintes pontos ao elaborar as instruções: garantir a segurança imediata, providenciar assistência médica, informar familiares, confirmar identidade, contato com autoridades, entre outros.
        '''
    else:
        return {
            'error': 'Invalid prompt type'
        }

    # Executa função responsável por gerar texto com IA Generativa a partir do prompt fornecido
    response_bedrock = generate_instructions(prompt)

    # Retorna o link do áudio no S3 como resposta
    return {
        'bedrock_response': response_bedrock
    }