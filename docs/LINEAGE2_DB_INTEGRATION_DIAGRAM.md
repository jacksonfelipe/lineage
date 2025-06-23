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

    classDef safe fill:#444,stroke:#fff,stroke-width:2px,color:#fff;
    class A,B,C,D,E,F safe;
    %% Fundo do gráfico
    %%{init: { 'theme': 'dark' }}%%
```

## Legend
- **User (Browser):** Client accessing the site.
- **Views/Endpoints Django:** Presentation and API layer.
- **Utility functions:** Logic layer that prepares and executes queries.
- **LineageDB:** Integration class, bridges Django and the L2 database using SQLAlchemy.
- **L2 Database:** Game server database, with specific Lineage 2 tables.