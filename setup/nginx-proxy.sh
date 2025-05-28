#!/bin/bash

# Verifica se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo "Por favor, execute este script como root (sudo)"
    exit 1
fi

# Instala o Nginx se não estiver instalado
if ! command -v nginx &> /dev/null; then
    echo "Instalando Nginx..."
    apt-get update
    apt-get install -y nginx
fi

# Instala o Certbot para SSL
if ! command -v certbot &> /dev/null; then
    echo "Instalando Certbot..."
    apt-get install -y certbot python3-certbot-nginx
fi

# Cria a configuração do Nginx
cat > /etc/nginx/sites-available/lineage-proxy << 'EOL'
server {
    listen 80;
    server_name _;  # Substitua pelo seu domínio

    location / {
        proxy_pass http://localhost:6085;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOL

# Cria link simbólico para habilitar o site
ln -sf /etc/nginx/sites-available/lineage-proxy /etc/nginx/sites-enabled/

# Remove a configuração padrão do Nginx
rm -f /etc/nginx/sites-enabled/default

# Testa a configuração do Nginx
nginx -t

# Reinicia o Nginx
systemctl restart nginx

echo "Configuração do Nginx concluída!"
echo "Para configurar o SSL, execute:"
echo "sudo certbot --nginx -d seu-dominio.com"
echo ""
echo "Lembre-se de substituir 'seu-dominio.com' pelo seu domínio real" 