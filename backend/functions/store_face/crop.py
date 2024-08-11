from PIL import Image
from io import BytesIO
from functions.store_face.twilio import retrieve_twilio_image

# Função responsável por utilizar o bounding box para recortar a face da pessoa na imagem
def crop_image(media_url, bounding_box):
    # Faz download da imagem
    image = retrieve_twilio_image(media_url)
    # Instância objeto do Pillow com a imagem
    pillow_image = Image.open(BytesIO(image))

    # Recupera dimensões da imagem
    image_width = pillow_image.size[0]
    image_height = pillow_image.size[1]

    # Calcula comprimento e largura reais da imagem
    width = int(bounding_box['Width'] * image_width)
    height = int(bounding_box['Height'] * image_height)

    # Calcula coordenadas da instância encontrada
    left = int(bounding_box['Left'] * image_width)
    top = int(bounding_box['Top'] * image_height)
    right = left + width
    bottom = top + height

    # Recorta imagem da instância encontrada baseada nas coordenadas calculadas
    pillow_image_cropped = pillow_image.crop((left, top, right, bottom))

    # Converte o recorte de bytes para uma imagem PNG
    face = BytesIO()
    pillow_image_cropped.save(face, "PNG")

    # Retorna face em PNG
    return face