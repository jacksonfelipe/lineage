# Diagrama de Integração: Django x Banco do L2

Este diagrama ilustra como o app `apps.lineage.server` faz a ponte entre o Django e o banco de dados do Lineage 2 (L2), detalhando o fluxo de dados e responsabilidades de cada camada.

```mermaid
flowchart TD
    subgraph Django
        A["Usuário (Browser)"]
        B["Views/Endpoints Django"]
        C["Funções utilitárias (LineageStats, LineageServices, etc)"]
    end
    subgraph Integração
        D["LineageDB (SQLAlchemy)"]
    end
    subgraph L2
        E["Banco de Dados L2 (MySQL)"]
        F["Tabelas: characters, accounts, clan_data, ..."]
    end

    A -->|HTTP| B
    B --> C
    C -->|SQL| D
    D -->|Conexão direta| E
    E --> F

    classDef safe fill:#bbf,stroke:#333,stroke-width:2px;
    class A,B,C,D,E,F safe;
```

## Legenda
- **Usuário (Browser):** Cliente acessando o site.
- **Views/Endpoints Django:** Camada de apresentação e API.
- **Funções utilitárias:** Camada de lógica que prepara e executa queries.
- **LineageDB:** Classe de integração, faz a ponte entre Django e o banco do L2 usando SQLAlchemy.
- **Banco de Dados L2:** Base de dados do servidor de jogo, com tabelas específicas do Lineage 2. 