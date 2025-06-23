# Diagrama do Funcionamento do Sistema de Temas

Este diagrama mostra o fluxo completo do sistema de temas, desde o upload do ZIP até a renderização das páginas com o tema ativo.

```mermaid
flowchart TD
    subgraph Admin
        A["Admin Django: Upload ZIP do Tema"]
    end
    subgraph Backend
        B["Model Theme: Validação & Extração"]
        C["theme.json: Metadados & Variáveis"]
        D["Arquivos extraídos em themes/installed/<slug>/"]
        E["Ativação: Apenas 1 tema ativo"]
        F["ThemeVariable: Variáveis salvas no banco"]
    end
    subgraph Contexto
        G["Context Processors:\n- active_theme\n- theme_variables\n- background_setting"]
    end
    subgraph Renderização
        H["render_theme_page (utils)"]
        I["Templates do tema ativo\n(installed/<slug>/base.html, etc)"]
        J["Fallback para templates padrão"]
    end
    subgraph Frontend
        K["Usuário acessa página\ncom visual do tema ativo"]
    end

    A --> B
    B --> C
    B --> D
    B --> F
    B --> E
    F --> G
    E --> G
    G --> H
    H --> I
    H --> J
    I --> K
    J --> K

    classDef safe fill:#444,stroke:#fff,stroke-width:2px,color:#fff;
    class A,B,C,D,E,F,G,H,I,J,K safe;
    %% Fundo do gráfico
    %%{init: { 'theme': 'dark' }}%%
```

## Legend
- **Django Admin:** Theme upload and management.
- **Theme Model:** Validation, extraction, and activation of the theme.
- **theme.json:** Theme metadata and variables.
- **Extracted files:** Templates, CSS, JS, images, etc.
- **ThemeVariable:** Saved and internationalized variables.
- **Context Processors:** Inject context into templates.
- **render_theme_page:** Utility function for dynamic rendering.
- **Templates of active theme:** Customized theme templates.
- **Fallback:** Use default templates if not present in the theme.
- **User:** Views the site with the active theme.