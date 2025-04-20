#!/bin/bash

# Sai no primeiro erro
set -e

clear

echo "========================================================="
echo "  🚀 Bem-vindo ao Instalador do Projeto Lineage 2 PDL!   "
echo "========================================================="
echo
echo "Este script vai preparar todo o ambiente para você."
echo

# Confirmar antes de iniciar
read -p "Deseja continuar com a instalação? (s/n): " CONTINUE

if [[ "$CONTINUE" != "s" && "$CONTINUE" != "S" ]]; then
  echo "Instalação cancelada."
  exit 0
fi

echo
echo "🔄 Atualizando pacotes e instalando dependências..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common python3-venv python3-pip gettext

echo
echo "🐳 Instalando Docker e Docker Compose..."

# Adiciona chave GPG do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Adiciona repositório Docker
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu jammy stable"

# Instala Docker
sudo apt update
sudo apt install -y docker-ce

# Habilita Docker no boot
sudo systemctl enable docker
sudo systemctl start docker

# Verifica Docker
docker --version

# Instala Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version

echo
echo "📂 Clonando repositório do projeto..."
git clone https://github.com/D3NKYT0/lineage.git
cd lineage

echo
echo "🐍 Configurando ambiente Python (virtualenv)..."

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

mkdir -p logs

echo
echo "⚙️ Criando arquivo .env (se não existir)..."
if [ ! -f ".env" ]; then
  cat <<EOL > .env
# True for development, False for production
DEBUG=True
SEND_EMAIL_DEGUB=True
SECRET_KEY='key_32_bytes'

DB_ENGINE=postgresql
DB_HOST=postgres
DB_NAME=db_name
DB_USERNAME=db_user
DB_PASS=db_pass
DB_PORT=5432

CONFIG_EMAIL_ENABLE=True
CONFIG_EMAIL_USE_TLS=True
CONFIG_EMAIL_HOST=smtp.domain.com
CONFIG_EMAIL_HOST_USER=mail@mail.dev.br
CONFIG_DEFAULT_FROM_EMAIL=mail@mail.dev.br
CONFIG_EMAIL_HOST_PASSWORD=password
CONFIG_EMAIL_PORT=587

CONFIG_AUDITOR_MIDDLEWARE_ENABLE = True
CONFIG_AUDITOR_MIDDLEWARE_RESTRICT_PATHS = ["/admin/", "/app/"]

DJANGO_CACHE_REDIS_URI=redis://redis_container_name:6379/0

RENDER_EXTERNAL_HOSTNAME=domain.com
RENDER_EXTERNAL_FRONTEND=domain.com

CELERY_BROKER_URI=redis://redis:6379/1
CELERY_BACKEND_URI=redis://redis:6379/1

CHANNELS_BACKEND=redis://redis:6379/2

ENCRYPTION_KEY='key_32_bytes'
DATA_UPLOAD_MAX_MEMORY_SIZE=10485760
SERVE_DECRYPTED_FILE_URL_BASE='decrypted-file'

LINEAGE_DB_NAME=l2jdb
LINEAGE_DB_USER=l2user
LINEAGE_DB_PASSWORD=suaSenhaAqui
LINEAGE_DB_HOST=192.168.1.100
LINEAGE_DB_PORT=3306

CONFIG_MERCADO_PAGO_ACCESS_TOKEN="APP_USR-0000000000000000-000000-00000000000000000000000000000000-000000000"
CONFIG_MERCADO_PAGO_PUBLIC_KEY="APP_USR-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
CONFIG_MERCADO_PAGO_CLIENT_ID="0000000000000000"
CONFIG_MERCADO_PAGO_CLIENT_SECRET="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
CONFIG_MERCADO_PAGO_SIGNATURE="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
CONFIG_MERCADO_PAGO_SUCCESS_URL="https://seusite.com.br/app/payment/mercadopago/sucesso/"
CONFIG_MERCADO_PAGO_FAILURE_URL="https://seusite.com.br/app/payment/mercadopago/erro/"

LINEAGE_QUERY_MODULE=dreamv3

CONFIG_HCAPTCHA_SITE_KEY=bcf40348-fa88-4570-a752-2asdasde0b2bc
CONFIG_HCAPTCHA_SECRET_KEY=ES_dc688fdasdasdadasdas4e918093asddsddsafa3f1b

CONFIG_LANGUAGE_CODE="pt"
CONFIG_TIME_ZONE="America/Recife"
CONFIG_DECIMAL_SEPARATOR=','
CONFIG_USE_THOUSAND_SEPARATOR=True
CONFIG_DATETIME_FORMAT='d/m/Y H:i:s'
CONFIG_DATE_FORMAT='d/m/Y'
CONFIG_TIME_FORMAT='H:i:s'
CONFIG_GMT_OFFSET=-3
EOL
fi

echo
echo "🔐 Configurando autenticação básica (.htpasswd)..."

# Solicitar usuário e senha
read -p "👤 Digite o login para o admin: " ADMIN_USER
read -s -p "🔒 Digite a senha para o admin: " ADMIN_PASS
echo

# Criar diretório nginx se não existir
mkdir -p nginx

# Gerar hash bcrypt com python
HASHED_PASS=$(python3 - <<EOF
from passlib.hash import bcrypt
print(bcrypt.using(rounds=10).hash("$ADMIN_PASS"))
EOF
)

# Criar .htpasswd
echo "$ADMIN_USER:$HASHED_PASS" > nginx/.htpasswd
echo "✅ Arquivo nginx/.htpasswd criado com sucesso."

# Gerar chave Fernet com python
FERNET_KEY=$(python3 - <<EOF
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
EOF
)

# Atualizar ENCRYPTION_KEY no .env
sed -i "/^ENCRYPTION_KEY=/c\ENCRYPTION_KEY='$FERNET_KEY'" .env
echo "✅ ENCRYPTION_KEY atualizado no .env."

echo
echo "🏗️  Construindo containers com Docker Compose..."
docker compose build

echo
echo "🚀 Subindo containers..."
docker compose up -d

echo
echo "⏳ Aguardando banco de dados iniciar..."
until docker compose exec postgres pg_isready -U db_user > /dev/null 2>&1; do
  echo "$(date '+%H:%M:%S') - PostgreSQL não está pronto ainda... aguardando..."
  sleep 2
done

echo
echo "🗄️ Aplicando migrações no banco..."
docker compose exec site python3 manage.py migrate

echo
echo "👤 Criando usuário administrador no Django..."
read -p "Username: " DJANGO_SUPERUSER_USERNAME
read -p "Email: " DJANGO_SUPERUSER_EMAIL
read -s -p "Password: " DJANGO_SUPERUSER_PASSWORD
echo
read -s -p "Confirme a senha: " DJANGO_SUPERUSER_PASSWORD_CONFIRM
echo

if [ "$DJANGO_SUPERUSER_PASSWORD" != "$DJANGO_SUPERUSER_PASSWORD_CONFIRM" ]; then
  echo "❌ As senhas não conferem. Abortando."
  exit 1
fi

docker compose exec site python3 manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser(
        username='$DJANGO_SUPERUSER_USERNAME',
        email='$DJANGO_SUPERUSER_EMAIL',
        password='$DJANGO_SUPERUSER_PASSWORD'
    )
    print('✅ Superuser \"$DJANGO_SUPERUSER_USERNAME\" criado com sucesso.')
else:
    print('ℹ️ O usuário \"$DJANGO_SUPERUSER_USERNAME\" já existe.')
"

echo
echo "🎉 Instalação concluída com sucesso!"
echo "Acesse: http://localhost:80"
echo "Para gerenciar o projeto, use:"
echo " - docker compose up -d         # Para iniciar"
echo " - docker compose down          # Para parar"
echo
