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

    classDef safe fill:#bbf,stroke:#333,stroke-width:2px;
    class A,B,C,D,E,F,G,H safe;
```

## Legenda dos Componentes
- **Usuário (Browser):** Cliente acessando o sistema.
- **nginx:** Proxy reverso, serve estáticos e encaminha requisições para o Django.
- **site:** Aplicação Django rodando via ASGI (Daphne).
- **celery:** Worker para tarefas assíncronas.
- **celery-beat:** Agendador de tarefas periódicas.
- **flower:** Monitoramento e dashboard do Celery.
- **redis:** Broker de mensagens e cache.
- **postgres:** Banco de dados relacional. 