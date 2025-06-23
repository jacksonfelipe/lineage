# Documento de Arquitetura do Projeto

## 1. Visão Geral

Este projeto é uma aplicação web robusta, baseada em Django, com múltiplos módulos (apps) organizados para diferentes domínios de negócio. Ele utiliza Docker para orquestração de ambientes, facilitando o desenvolvimento, testes e deploy. O frontend é desacoplado, sugerindo uma arquitetura moderna e escalável.

---

## 2. Componentes Principais

### 2.1 Backend (Django)
- **Localização:** `apps/`, `core/`, `middlewares/`, `utils/`
- **Descrição:**  
  O backend é implementado em Django, estruturado em múltiplos apps, cada um responsável por um domínio específico (ex: `accountancy`, `auction`, `games`, `inventory`, etc).  
  O diretório `core/` provavelmente contém configurações globais e funcionalidades compartilhadas.
- **Funcionalidades:**  
  - Autenticação, administração, relatórios, inventário, pagamentos, jogos, loja, wiki, notificações, etc.
  - Uso de middlewares customizados.
  - Utilitários e scripts auxiliares em `utils/`.

### 2.2 Frontend
- **Localização:** `frontend/`
- **Descrição:**  
  O frontend está desacoplado do backend, sugerindo o uso de frameworks modernos (React, Vue, etc).  
  O arquivo `Charts.js` e outros arquivos JS indicam visualizações dinâmicas.
- **Integração:**  
  Comunicação via API REST ou GraphQL com o backend Django.

### 2.3 Banco de Dados
- **Localização:** Definido no `docker-compose.yml` (não visível diretamente, mas presumido)
- **Descrição:**  
  O projeto utiliza um banco de dados relacional (provavelmente PostgreSQL ou MySQL, comum em projetos Django).
- **Persistência:**  
  O arquivo `db.sqlite3` sugere uso de SQLite em ambiente de desenvolvimento.

### 2.4 Servidor Web e Proxy
- **Localização:** `nginx/`, `Dockerfile`, `gunicorn-cfg.py`
- **Descrição:**  
  O Nginx atua como proxy reverso, servindo arquivos estáticos e repassando requisições para o Gunicorn, que executa o Django.
- **Configuração:**  
  Arquivos de configuração customizados para Nginx e Gunicorn.

### 2.5 Internacionalização
- **Localização:** `locale/`
- **Descrição:**  
  Suporte a múltiplos idiomas (pt, en, es), com arquivos `.po` e `.mo` para traduções.

### 2.6 Arquivos Estáticos e Mídia
- **Localização:** `static/`, `media/`
- **Descrição:**  
  Organização de assets (CSS, JS, imagens, fontes) e uploads de usuários.

### 2.7 Testes e Scripts
- **Localização:** `test/`, `setup/`
- **Descrição:**  
  Scripts de teste, geração de chaves, automação de backup, build e instalação de dependências.

---

## 3. Orquestração com Docker Compose

### 3.1 Serviços Definidos
O arquivo `docker-compose.yml` define os seguintes serviços principais:
- **site:**  
  Container principal rodando o Django com Daphne (ASGI).
- **nginx:**  
  Servidor web/proxy reverso.
- **db (postgres):**  
  Banco de dados relacional.
- **redis:**  
  Broker de mensagens e cache.
- **celery:**  
  Worker para tarefas assíncronas.
- **celery-beat:**  
  Agendador de tarefas periódicas.
- **flower:**  
  Monitoramento e dashboard do Celery.

### 3.2 Rede e Volumes
- **Rede interna:**  
  Comunicação entre containers via rede Docker.
- **Volumes:**  
  Persistência de dados do banco, arquivos estáticos e mídia.

---

## 4. Estrutura de Diretórios

```plaintext
apps/           # Apps Django organizados por domínio
core/           # Configurações e funcionalidades centrais do projeto
middlewares/    # Middlewares customizados para Django
utils/          # Scripts e utilitários auxiliares
frontend/       # Código do frontend desacoplado
static/         # Arquivos estáticos (CSS, JS, imagens)
media/          # Uploads de usuários
nginx/          # Configurações do Nginx
locale/         # Arquivos de tradução
setup/          # Scripts de automação e setup
test/           # Scripts e arquivos de teste
templates/      # Templates HTML do Django
```

---

## 5. Fluxo de Requisições

Ver diagrama em `DIAGRAMA.md`.

---

## 6. Considerações de Segurança
- Uso de variáveis de ambiente para segredos (`env.sample`).
- Configuração de proxy reverso (Nginx) para proteção e performance.
- Possível uso de autenticação e autorização customizadas.

---

## 7. Internacionalização e Acessibilidade
- Suporte a múltiplos idiomas via `locale/`.
- Templates organizados para fácil manutenção e customização.

---

## 8. Deploy e Escalabilidade
- Deploy facilitado via Docker Compose.
- Possibilidade de escalar serviços (web, workers) conforme demanda.
- Separação clara entre frontend e backend.

---

## 9. Observabilidade e Logs
- Diretório `logs/` para armazenamento de logs de aplicação e acesso.
- Possível integração com ferramentas externas de monitoramento.

---

## 10. Documentação
- `README.md`, `wiki.md`, `help.md` fornecem instruções de uso, contribuição e detalhes do projeto. 