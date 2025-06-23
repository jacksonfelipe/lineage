# Diagrama de Arquitetura

Este diagrama representa a arquitetura do projeto, desde o acesso do usuário até o banco de dados, incluindo todos os serviços orquestrados pelo Docker Compose.

```mermaid
flowchart TD
    subgraph Web
        A["Usuário (Browser)"]
    end
    subgraph Nginx
        B["nginx (Proxy Reverso)"]
    end
    subgraph App
        C["site (Django/ASGI)"]
        D["celery (Worker)"]
        E["celery-beat (Agendador)"]
        F["flower (Monitoramento Celery)"]
    end
    subgraph Infra
        G["redis (Broker/Cache)"]
        H["postgres (Banco de Dados)"]
    end
    
    A -->|HTTP/HTTPS| B
    B -->|Proxy| C
    B -->|Arquivos Estáticos/Mídia| B
    C -->|ORM| H
    C -->|Tarefas Assíncronas| G
    D -->|Broker| G
    E -->|Broker| G
    F -->|Broker| G
    D -->|Executa Tarefas| C
    E -->|Dispara Tarefas| D
    F -->|Monitora| D
    F -->|Monitora| E
    C -->|Depende| G
    D -->|Depende| C
    E -->|Depende| C
    F -->|Depende| C
    B -->|Depende| C
    C -->|Depende| H
    D -->|Depende| G
    E -->|Depende| G
    F -->|Depende| G

    classDef safe fill:#444,stroke:#fff,stroke-width:2px,color:#fff;
    class A,B,C,D,E,F,G,H safe;
    %% Fundo do gráfico
    %% O Mermaid não tem uma diretiva oficial para fundo, mas pode-se usar uma nota para simular
    %% ou instruir o visualizador a usar tema escuro.
    %% Para renderizadores que suportam, pode-se usar: %%{init: { 'theme': 'dark' }}%%
    %%{init: { 'theme': 'dark' }}%%
```

## Component Legend
- **User (Browser):** Client accessing the system.
- **nginx:** Reverse proxy, serves static files and forwards requests to Django.
- **site:** Django application running via ASGI (Daphne).
- **celery:** Worker for asynchronous tasks.
- **celery-beat:** Periodic task scheduler.
- **flower:** Celery monitoring and dashboard.
- **redis:** Message broker and cache.
- **postgres:** Relational database.
