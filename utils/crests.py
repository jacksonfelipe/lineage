from PIL import Image
import io
import os

class CrestHandler:
    def __init__(self):
        # Certifique-se de que a pasta 'crests' exista para salvar as imagens
        os.makedirs('crests', exist_ok=True)

    def make_image(self, image_blob, crest_id, crest_type, show_image):
        try:
            # Abre a imagem do blob e converte para RGBA
            image = Image.open(io.BytesIO(image_blob)).convert("RGBA")

            # Redimensiona conforme o tipo de crest (aliança ou clã)
            if crest_type == 'ally':
                image = image.resize((8, 12), Image.LANCZOS)
            else:
                image = image.resize((16, 12), Image.LANCZOS)

            # Se show_image for False, salva a imagem em disco
            if not show_image:
                save_path = f"crests/{crest_id}.png"
                image.save(save_path)

            # Retorna a imagem em formato de bytes para exibição
            byte_io = io.BytesIO()
            image.save(byte_io, 'PNG')
            byte_io.seek(0)
            return byte_io

        except Exception as e:
            raise Exception(f"Erro ao processar a imagem do crest: {e}")

    def make_empty_image(self, crest_type):
        try:
            # Define o tamanho da imagem vazia conforme o tipo de crest
            size = (8, 12) if crest_type == 'ally' else (16, 12)
            image = Image.new("RGBA", size, (0, 0, 0, 0))  # Transparente

            # Salva a imagem vazia em bytes
            byte_io = io.BytesIO()
            image.save(byte_io, 'PNG')
            byte_io.seek(0)
            return byte_io
        except Exception as e:
            raise Exception(f"Erro ao criar imagem vazia: {e}")
