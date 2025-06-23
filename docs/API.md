# Documentação de API

## Autenticação
- A maioria dos endpoints requer autenticação via sessão Django ou token.
- Exemplo de header:
  ```http
  Authorization: Token <seu-token>
  ```

## Endpoints Principais

### Exemplo: Ranking de Jogadores
- `GET /api/lineage/top-level/?limit=10`
- Resposta:
  ```json
  [
    {"char_name": "Hero", "level": 80, "clan_name": "Lendas", ...},
    ...
  ]
  ```

### Exemplo: Status de Castelo
- `GET /api/lineage/siege/`
- Resposta:
  ```json
  [
    {"castle": "Aden", "owner": "ClanX", "siege_date": "2024-06-01"},
    ...
  ]
  ```

## Formatos de Erro
- Respostas de erro seguem o padrão:
  ```json
  {"error": "Mensagem de erro"}
  ```

## Observações
- Consulte o código em `apps/lineage/server/views/` para mais exemplos de endpoints. 