import pyotp
import qrcode
import base64
from io import BytesIO


def gerar_qr_png(email, secret):
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name="pdl-project")
    
    # Gerar o QR Code
    img = qrcode.make(uri)
    
    # Salvar como PNG em um arquivo binário
    stream = BytesIO()
    img.save(stream, format='PNG')
    
    # Converter para base64
    img_base64 = base64.b64encode(stream.getvalue()).decode('utf-8')
    
    return img_base64
