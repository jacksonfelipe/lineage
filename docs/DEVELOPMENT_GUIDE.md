# Guia de Desenvolvimento

## Organização do Projeto
- Apps Django em `apps/`
- Frontend em `frontend/`
- Utilitários em `utils/`, `middlewares/`, etc.

## Convenções de Código
- Siga o PEP8 para Python.
- Use nomes descritivos para funções, variáveis e arquivos.
- Separe responsabilidades em apps e módulos.

## Fluxo de Trabalho
1. Crie uma branch para cada feature/bugfix:
   ```bash
   git checkout -b feature/nome-da-feature
   ```
2. Faça commits pequenos e descritivos.
3. Abra um Pull Request para revisão.
4. Use o arquivo `workflow.md` para seguir o fluxo de contribuição.

## Testes
- Testes em `test/`.
- Rode com:
  ```bash
  python manage.py test
  ```
- Escreva testes para novas funcionalidades.

## Linters e Qualidade
- Use `flake8`, `black` ou similares para manter o padrão de código.

## Dicas
- Consulte a documentação dos apps em `docs/`.
- Use variáveis de ambiente para configurações sensíveis. 