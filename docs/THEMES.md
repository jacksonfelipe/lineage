# Sistema de Temas e Templates

## Visão Geral
O sistema de temas permite customizar a aparência do site via upload de pacotes ZIP contendo templates, estilos, scripts e assets. Cada tema pode ser ativado/desativado e possui variáveis customizáveis para internacionalização e personalização visual.

---

## Como funciona
- **Modelo principal:** `Theme` (apps.main.administrator.models)
- **Upload:** O admin faz upload de um arquivo ZIP contendo o tema.
- **Validação:** O ZIP deve conter um arquivo `theme.json` com metadados obrigatórios (`name`, `slug`, etc).
- **Extração:** Os arquivos são extraídos para `themes/installed/<slug>/`.
- **Ativação:** Apenas um tema pode estar ativo por vez. Ao ativar um tema, os outros são desativados automaticamente.
- **Remoção:** Ao deletar um tema, o ZIP e a pasta extraída são removidos.

---

## Estrutura esperada do ZIP
- Arquivos permitidos: `.html`, `.css`, `.js`, imagens, fontes, etc.
- Arquivo obrigatório: `theme.json` com metadados e variáveis.
- Exemplo de `theme.json`:
  ```json
  {
    "name": "Tema Exemplo",
    "slug": "tema-exemplo",
    "version": "1.0",
    "author": "Seu Nome",
    "description": "Descrição do tema.",
    "variables": [
      {"name": "Cor Primária", "tipo": "string", "valor_pt": "#123456", "valor_en": "#123456", "valor_es": "#123456"}
    ]
  }
  ```

---

## Variáveis de Tema
- Definidas no `theme.json` e salvas como `ThemeVariable`.
- Suportam internacionalização (`valor_pt`, `valor_en`, `valor_es`).
- Disponíveis no contexto dos templates via context processor.
- Exemplo de uso em template:
  ```django
  <style>body { background: {{ tema_exemplo_cor_primaria }}; }</style>
  ```

---

## Contexto dos Templates
- O context processor `active_theme` injeta no contexto:
  - `active_theme`: slug do tema ativo
  - `base_template`: caminho do base.html do tema
  - `theme_slug`, `path_theme`, `theme_files`
- O context processor `theme_variables` injeta todas as variáveis do tema.
- O context processor `background_setting` injeta a imagem de fundo ativa.

---

## Renderização de Páginas
- Função `render_theme_page` (em `utils/render_theme_page.py`):
  - Tenta renderizar o template do tema ativo.
  - Se não existir, faz fallback para o template padrão.
- Exemplo de uso:
  ```python
  return render_theme_page(request, 'public', 'index.html', context)
  ```

---

## Servindo Arquivos do Tema
- View `serve_theme_file` permite servir arquivos HTML do tema ativo de forma segura.
- Verifica existência do arquivo e retorna 404 se não encontrado.

---

## Segurança
- Apenas arquivos com extensões permitidas são extraídos.
- Caminhos são validados para evitar path traversal.
- Tamanho máximo do ZIP: 30MB.

---

## Dicas
- Sempre inclua um `base.html` no tema para herança de templates.
- Use variáveis para facilitar customização sem editar arquivos.
- Teste o tema em múltiplos idiomas. 