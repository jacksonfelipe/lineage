#!/bin/bash

set -e

echo "=== Setting up Python environment ==="

# Requisito mínimo
REQUIRED_PYTHON="3.10"

# Detecta versão do Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

# Compara versão
if [ "$(printf '%s\n' "$REQUIRED_PYTHON" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_PYTHON" ]; then
  echo "Python $REQUIRED_PYTHON+ required, found $PYTHON_VERSION"
  exit 1
fi

# Instala venv e pip se não existirem
sudo apt-get update -qq
sudo apt-get install -y python3-venv python3-pip

# Cria virtualenv se não existir
[ -d .venv ] || python3 -m venv .venv

# Ativa ambiente virtual
source .venv/bin/activate

# Atualiza pip e instala dependências
pip install --upgrade pip
pip install -r requirements.txt

# Garante diretórios obrigatórios
mkdir -p logs

echo "✓ Environment ready."
