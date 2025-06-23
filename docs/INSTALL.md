# Guia de Instalação e Deploy

## Pré-requisitos
- Python 3.10+
- Docker e Docker Compose
- Node.js (opcional, para frontend)

## Instalação Local (sem Docker)
1. Clone o repositório:
   ```bash
   git clone <repo-url>
   cd SITE
   ```
2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure as variáveis de ambiente:
   - Copie `env.sample` para `.env` e ajuste conforme necessário.
5. Migre o banco e crie um superusuário:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
6. Rode o servidor:
   ```bash
   python manage.py runserver
   ```

## Instalação com Docker
1. Configure o arquivo `.env`.
2. Rode:
   ```bash
   docker-compose up --build
   ```
3. Acesse o sistema em `http://localhost:6085`.

## Deploy em Produção
- Use Docker Compose, Nginx, HTTPS (Let's Encrypt).
- Configure volumes para persistência de dados.
- Ajuste variáveis de ambiente para produção.

## Dicas
- Use `docker-compose logs -f` para ver os logs.
- Use `docker-compose exec site bash` para acessar o container do Django. 