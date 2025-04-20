#!/bin/bash

set -e

INSTALL_DIR=".install_status"
mkdir -p $INSTALL_DIR

clear

echo "========================================================="
echo "  🚀 Bem-vindo ao Instalador do Projeto Lineage 2 PDL!   "
echo "========================================================="
echo

if [ -f "$INSTALL_DIR/.install_done" ]; then
  echo "⚠️  Instalação já foi concluída anteriormente."
  echo
  read -p "Deseja rodar os containers (s) ou refazer a instalação (r)? (s/r): " OPCAO

  if [[ "$OPCAO" == "s" || "$OPCAO" == "S" ]]; then
    docker compose up -d
    echo "✅ Containers iniciados."
    exit 0
  elif [[ "$OPCAO" == "r" || "$OPCAO" == "R" ]]; then
    echo "🔄 Refazendo instalação..."
    rm -rf $INSTALL_DIR
    mkdir -p $INSTALL_DIR
  else
    echo "❌ Opção inválida."
    exit 1
  fi
fi

echo "Este script vai preparar todo o ambiente para você."
echo
read -p "Deseja continuar com a instalação? (s/n): " CONTINUE

if [[ "$CONTINUE" != "s" && "$CONTINUE" != "S" ]]; then
  echo "Instalação cancelada."
  exit 0
fi

# Atualizar e instalar dependências
if [ ! -f "$INSTALL_DIR/system_ready" ]; then
  echo
  echo "🔄 Atualizando pacotes e instalando dependências..."
  sudo apt update && sudo apt upgrade -y
  sudo apt install -y apt-transport-https ca-certificates curl software-properties-common python3-venv python3-pip gettext
  touch "$INSTALL_DIR/system_ready"
fi

# Instalar Docker e Compose
if [ ! -f "$INSTALL_DIR/docker_ready" ]; then
  echo
  echo "🐳 Instalando Docker e Docker Compose..."
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
  sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu jammy stable"
  sudo apt update
  sudo apt install -y docker-ce
  sudo systemctl enable docker
  sudo systemctl start docker
  docker --version
  sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  docker-compose --version
  touch "$INSTALL_DIR/docker_ready"
fi

# Clonar repositório
if [ ! -f "$INSTALL_DIR/repo_cloned" ]; then
  echo
  echo "📂 Clonando repositório do projeto..."
  git clone https://github.com/D3NKYT0/lineage.git || true
  cd lineage
  touch "../$INSTALL_DIR/repo_cloned"
else
  cd lineage
fi

# Configurar ambiente Python
if [ ! -f "../$INSTALL_DIR/python_ready" ]; then
  echo
  echo "🐍 Configurando ambiente Python (virtualenv)..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
  mkdir -p logs
  touch "../$INSTALL_DIR/python_ready"
else
  source .venv/bin/activate
fi

# Criar .env
if [ ! -f "../$INSTALL_DIR/env_created" ]; then
  echo
  echo "⚙️ Criando arquivo .env (se não existir)..."
  if [ ! -f ".env" ]; then
    cat <<EOL > .env
DEBUG=False
SECRET_KEY='key_32_bytes'
# restante...
EOL
  fi
  touch "../$INSTALL_DIR/env_created"
fi

# Configurar autenticação básica
if [ ! -f "../$INSTALL_DIR/htpasswd_created" ]; then
  echo
  echo "🔐 Configurando autenticação básica (.htpasswd)..."
  read -p "👤 Digite o login para o admin: " ADMIN_USER
  read -s -p "🔒 Digite a senha para o admin: " ADMIN_PASS
  echo
  mkdir -p nginx
  HASHED_PASS=$(python3 - <<EOF
from passlib.hash import bcrypt
print(bcrypt.using(rounds=10).hash("$ADMIN_PASS"))
EOF
)
  echo "$ADMIN_USER:$HASHED_PASS" > nginx/.htpasswd
  echo "✅ Arquivo nginx/.htpasswd criado."
  touch "../$INSTALL_DIR/htpasswd_created"
fi

# Gerar chave Fernet
if [ ! -f "../$INSTALL_DIR/fernet_key_generated" ]; then
  FERNET_KEY=$(python3 - <<EOF
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
EOF
)
  sed -i "/^ENCRYPTION_KEY=/c\ENCRYPTION_KEY='$FERNET_KEY'" .env
  echo "✅ ENCRYPTION_KEY atualizado no .env."
  touch "../$INSTALL_DIR/fernet_key_generated"
fi

# 🛠️ Docker: parar, limpar, rebuildar, rodar e migrar

echo
echo "🏗️ Parando containers antigos..."
docker compose down || { echo "❌ Falha ao parar containers"; }

echo
echo "🗑️  Removendo containers antigos específicos..."
containers=$(docker ps -a -q --filter name=site --filter name=celery --filter name=celery_beat --filter name=flower --filter name=nginx --filter name=redis)
if [ -n "$containers" ]; then
  docker rm $containers || echo "ℹ️ Alguns containers não puderam ser removidos (podem já estar removidos)"
else
  echo "ℹ️ Nenhum container antigo encontrado."
fi

echo
echo "🗑️  Removendo volume opcional static_data (se existir)..."
docker volume rm $(docker volume ls -q --filter name=static_data) || echo "ℹ️ Volume não encontrado ou já removido"

echo
echo "🔨 Construindo Docker images..."
docker compose build || { echo "❌ Falha ao buildar imagens"; exit 1; }

echo
echo "🚀 Subindo containers..."
docker compose up -d || { echo "❌ Falha ao subir containers"; exit 1; }

echo
echo "⏳ Aguardando banco de dados iniciar..."
until docker compose exec postgres pg_isready -U db_user > /dev/null 2>&1; do
  echo "$(date '+%H:%M:%S') - PostgreSQL não está pronto ainda... aguardando..."
  sleep 2
done

echo
echo "🗄️ Aplicando migrações no banco..."
docker compose exec site python3 manage.py migrate || { echo "❌ Falha ao aplicar migrações"; exit 1; }

echo
echo "🧹 Limpando imagens, volumes, containers e builders não usados..."
docker image prune -f
docker volume prune -f
docker container prune -f
docker builder prune -f

# Criar superuser
if [ ! -f "../$INSTALL_DIR/superuser_created" ]; then
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
  touch "../$INSTALL_DIR/superuser_created"
fi

# Finaliza instalação
touch "$INSTALL_DIR/.install_done"

echo
echo "🎉 Instalação concluída com sucesso!"
echo "Acesse: http://localhost:80"
echo "Para gerenciar o projeto, use:"
echo " - docker compose up -d         # Para iniciar"
echo " - docker compose down          # Para parar"
echo
