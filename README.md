# Pro Age (SUOPE) [1.5](https://suope.age.pe.gov.br)

<img align="right" height="180" src="https://i.imgur.com/buvNhRO.png"/>

O Projeto Proage foi inicialmente criado com o objetivo de realizar análises de risco, mas ao longo do tempo, evoluiu para um sistema completo de prospecção de clientes, com foco em crédito bancário. Desde as suas primeiras versões, o projeto passou por várias iterações e aprimoramentos, tendo sua primeira fase concluída cerca de um ano atrás. Embora uma versão do sistema já estivesse em produção, na época não houve formalização nem documentação dos requisitos, o que trouxe desafios para o desenvolvimento contínuo.

Ao longo de seu crescimento, o Proage integrou áreas essenciais à sua esteira de crédito, como compliance, análise e pequenos negócios. A maior contribuição veio do suporte às linhas de crédito para pequenos negócios, segmento que se tornou o pilar central do sistema. O Proage foi desenhado para atender dois perfis principais: o agente de crédito, que facilita a prospecção diretamente com o cliente, e o backoffice, responsável por qualificar e monitorar o crédito.

Agora, estamos avançando para uma nova fase com a atualização para o Proage 2.0. Esta nova versão trará uma série de melhorias, incluindo um aplicativo para clientes (Portal do Cliente), permitindo acompanhar propostas e contratos, resolver problemas com o agente e reemitir boletos. Além disso, será lançado um aplicativo específico para agentes, otimizando o atendimento e facilitando a prospecção. O sistema de backoffice também será significativamente aprimorado, abrangendo tanto pequenos negócios quanto operações especiais acima de R$ 21 mil. O Proage 2.0 será expansivo, cobrindo todas as áreas da AGE e trazendo melhorias ao motor do sistema, tornando-o mais eficiente e preparado para novas demandas.

Com essas inovações, o Proage 1.5 (SUOPE) se destacará como uma ferramenta ainda mais poderosa na otimização dos processos de crédito, promovendo agilidade e transparência aprimoradas para agentes e clientes.

## Tecnologias Utilizadas

- **Django**: Framework web principal que permite a construção de aplicações rapidamente, com suporte a autenticação, gerenciamento de banco de dados e muito mais.
- **Gunicorn**: Servidor WSGI que serve a aplicação Django, garantindo alta performance e capacidade de lidar com múltiplas requisições.
- **Redis**: Sistema de gerenciamento de dados em memória utilizado como broker de mensagens para o Celery, melhorando o desempenho da aplicação.
- **Nginx**: Servidor web reverso que gerencia requisições HTTP e serve arquivos estáticos e de mídia.
- **Docker**: Utilizado para containerização da aplicação, garantindo consistência e facilidade de deployment em diferentes ambientes.
- **Docker Compose**: Ferramenta que orquestra múltiplos containers, facilitando a configuração e execução dos serviços.

## Estrutura do Projeto

### Serviços Definidos no Docker Compose

- **proage**: Serviço principal que roda o Django com Gunicorn.
- **nginx**: Servidor web que atua como proxy reverso para o serviço Django.
- **redis**: Banco de dados em memória utilizado como broker de mensagens.

### Volumes Utilizados

- `logs`: Para armazenar logs da aplicação.
- `static`: Para armazenar arquivos estáticos da aplicação.
- `media`: Para armazenar arquivos de mídia enviados pelos usuários.

### Rede

- **web_network**: Rede criada para interconectar todos os serviços.

#

<p align="center">
<img height="280" src="https://i.imgur.com/8M0OG4u.png">
</p>

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
https://suop.denky.dev.br

http://127.0.0.1
```

## Sobre Mim
>Desenvolvedor da AGE - Daniel Amaral (31 Anos) Recife/PE
- Emails: danielamaral.f@age.pe.gov.br | danielamaral.f@hotmail.com | contato@denky.dev.br
- Discord: denkyto


## Grupo de Staffs:

**Núcleo de Programação**

- Daniel Amaral (Desenvolvedor - FullStack/FullCycle)
- Jonathas Cardoso (Desenvolvedor - FrontEnd)

**Apoio e Testers**

- Lucas Barbosa (Suporte)
- Ailton Junior (Suporte)

**Gestão**

- Renan Nere (Gerente / Sustentação)
- Nilo Martins (Tean Leader)
