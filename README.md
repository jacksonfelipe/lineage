# Painel Lineage 2 [1.0](https://denky.dev.br)

Um painel que nasceu com a missão de oferecer ferramentas poderosas para administradores de servidores privados de Lineage 2. Inicialmente voltado à análise de riscos e estabilidade dos servidores, o projeto evoluiu e se consolidou como uma solução completa para prospecção, gerenciamento e operação de servidores — tudo em código aberto.

## Tecnologias Utilizadas

- **Django**: Framework web principal que permite a construção de aplicações rapidamente, com suporte a autenticação, gerenciamento de banco de dados e muito mais.
- **Gunicorn**: Servidor WSGI que serve a aplicação Django, garantindo alta performance e capacidade de lidar com múltiplas requisições.
- **Redis**: Sistema de gerenciamento de dados em memória utilizado como broker de mensagens para o Celery, melhorando o desempenho da aplicação.
- **Nginx**: Servidor web reverso que gerencia requisições HTTP e serve arquivos estáticos e de mídia.
- **Docker**: Utilizado para containerização da aplicação, garantindo consistência e facilidade de deployment em diferentes ambientes.
- **Docker Compose**: Ferramenta que orquestra múltiplos containers, facilitando a configuração e execução dos serviços.

## Estrutura do Projeto

### Serviços Definidos no Docker Compose

- **site**: Serviço principal que roda o Django com Gunicorn.
- **nginx**: Servidor web que atua como proxy reverso para o serviço Django.
- **redis**: Banco de dados em memória utilizado como broker de mensagens.

### Volumes Utilizados

- `logs`: Para armazenar logs da aplicação.
- `static`: Para armazenar arquivos estáticos da aplicação.
- `media`: Para armazenar arquivos de mídia enviados pelos usuários.

### Rede

- **lineage_network**: Rede criada para interconectar todos os serviços.

#

[![Supported Python versions](https://img.shields.io/pypi/pyversions/Django.svg)](https://www.djangoproject.com/)


## Como iniciar

```bash
$ chmod +x build.sh
$ ./build.sh
```


## Como migrar o banco de dados (PostgreSQL)

```bash
$ python manage.py makemigrations
$ python manage.py migrate
```


## Como testar (produção / homologação)

```bash
http://127.0.0.1
```

## Sobre Mim
>Desenvolvedor - Daniel Amaral (31 Anos) Recife/PE
- Emails:  contato@denky.dev.br
- Discord: denkyto


## Grupo de Staffs:

**Núcleo de Programação**

- Daniel Amaral (Desenvolvedor - FullStack/FullCycle)

**Apoio e Testers**

- Daniel Amaral (Desenvolvedor - FullStack/FullCycle)

**Gestão**

- Daniel Amaral (Desenvolvedor - FullStack/FullCycle)
