#!/bin/bash

# Verifica se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo "Por favor, execute este script como root (sudo)"
    exit 1
fi

# Detecta a versão do Ubuntu
UBUNTU_VERSION=$(lsb_release -rs)

echo "Detectada versão do Ubuntu: $UBUNTU_VERSION"

# Instala dependências necessárias
apt-get update
apt-get install -y curl gnupg2 ca-certificates lsb-release ubuntu-keyring

# Importa a chave de assinatura do Nginx
curl https://nginx.org/keys/nginx_signing.key | gpg --dearmor | tee /usr/share/keyrings/nginx-archive-keyring.gpg >/dev/null

# Adiciona o repositório oficial do Nginx
echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] https://nginx.org/packages/mainline/ubuntu $(lsb_release -cs) nginx" | tee /etc/apt/sources.list.d/nginx.list

# Atualiza a lista de pacotes
apt-get update

# Remove versão antiga do Nginx se existir
apt-get remove -y nginx nginx-common nginx-full nginx-core

# Instala o Nginx
apt-get install -y nginx

# Verifica a instalação
nginx -v

# Habilita e inicia o serviço
systemctl enable nginx
systemctl start nginx

# Verifica o status
systemctl status nginx --no-pager

echo "Nginx instalado com sucesso!"
echo "Para verificar a versão instalada: nginx -v"
echo "Para iniciar: systemctl start nginx"
echo "Para parar: systemctl stop nginx"
echo "Para reiniciar: systemctl restart nginx" 