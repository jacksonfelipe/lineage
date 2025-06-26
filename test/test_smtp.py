import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

EMAIL_ENABLE = os.getenv('CONFIG_EMAIL_ENABLE', 'False').lower() in ['true', '1', 'yes']
EMAIL_USE_TLS = os.getenv('CONFIG_EMAIL_USE_TLS', 'True').lower() in ['true', '1', 'yes']
EMAIL_HOST = os.getenv('CONFIG_EMAIL_HOST')
EMAIL_HOST_USER = os.getenv('CONFIG_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('CONFIG_EMAIL_HOST_PASSWORD')
EMAIL_PORT = int(os.getenv('CONFIG_EMAIL_PORT', 587))
DEFAULT_FROM_EMAIL = os.getenv('CONFIG_DEFAULT_FROM_EMAIL', EMAIL_HOST_USER)


def main():
    if not EMAIL_ENABLE:
        print('Email está desabilitado nas configurações.')
        return
    if not all([EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_PORT]):
        print('Faltam configurações SMTP.')
        return

    to_email = input('Digite o email de destino para o teste SMTP: ')
    subject = 'Teste SMTP'
    body = 'Este é um email de teste enviado pelo script test_smtp.py.'

    msg = MIMEMultipart()
    msg['From'] = DEFAULT_FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT, timeout=10)
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.sendmail(DEFAULT_FROM_EMAIL, to_email, msg.as_string())
        server.quit()
        print('Email de teste enviado com sucesso!')
    except Exception as e:
        print(f'Erro ao enviar email: {e}')


if __name__ == '__main__':
    main() 
