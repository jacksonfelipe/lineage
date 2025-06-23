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

    classDef safe fill:#bbf,stroke:#333,stroke-width:2px;
    class A,B,C,D,E,F,G,H,I,J,K safe;
```

## Legenda
- **Admin Django:** Upload e gerenciamento dos temas.
- **Model Theme:** Validação, extração e ativação do tema.
- **theme.json:** Metadados e variáveis do tema.
- **Arquivos extraídos:** Templates, CSS, JS, imagens, etc.
- **ThemeVariable:** Variáveis salvas e internacionalizadas.
- **Context Processors:** Injeção de contexto nos templates.
- **render_theme_page:** Função utilitária para renderização dinâmica.
- **Templates do tema ativo:** Templates customizados do tema.
- **Fallback:** Uso dos templates padrão caso não exista no tema.
- **Usuário:** Visualiza o site com o tema ativo. 