#!/bin/bash

# Renova o certificado se estiver próximo de expirar
docker-compose run --rm certbot renew

# Reinicia o Nginx para carregar o novo certificado
docker-compose restart nginx 