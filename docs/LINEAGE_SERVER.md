# Documentação do apps.lineage.server

## Visão Geral

O app `apps.lineage.server` é responsável por integrar o Django com o banco de dados do servidor Lineage 2 (L2), permitindo que a aplicação web acesse, consulte e manipule dados do jogo em tempo real, sem misturar os dados do Django com os dados do L2.

---

## Estrutura do app

- **models.py**: Modelos Django para configurações, preços de serviços, apoiadores, etc. (dados do site, não do L2)
- **database.py**: Classe `LineageDB` para conexão e operações no banco do L2 (MySQL), usando SQLAlchemy.
- **querys/**: Diversos arquivos com queries SQL e classes utilitárias para acessar dados do L2 (ex: personagens, clãs, rankings, etc).
- **views/**: Endpoints Django que expõem dados do L2 para o frontend ou APIs.
- **utils/**: Utilitários, cache, etc.

---

## O Banco do L2

O banco do L2 é um banco MySQL separado, com tabelas como `characters`, `accounts`, `clan_data`, `castle`, etc. Ele não é gerenciado pelo Django ORM, mas sim acessado diretamente via SQL puro.

- **Conexão**: Feita via SQLAlchemy, usando variáveis de ambiente para host, usuário, senha, etc.
- **Classe principal**: `LineageDB` (singleton, thread-safe)
- **Operações**: select, insert, update, delete, execute_raw, com cache opcional.
- **Exemplo de uso**:
  ```python
  from apps.lineage.server.database import LineageDB
  result = LineageDB().select("SELECT * FROM characters WHERE char_name = :name", {"name": "Hero"})
  ```

---

## Relação Django x Banco do L2

- **Django ORM**: Usado apenas para dados do site (usuários, configurações, compras, etc).
- **Banco do L2**: Acesso via SQL puro, sem models Django, para garantir performance e compatibilidade com o servidor do jogo.
- **Integração**: Funções utilitárias e endpoints Django usam a `LineageDB` para buscar dados do L2 e exibir no site (ex: rankings, status de castelo, personagens online, etc).
- **Exemplo de endpoint**:
  ```python
  # views/server_views.py
  @endpoint_enabled('top_level')
  @safe_json_response
  def top_level(request):
      limit = int(request.GET.get("limit", 10))
      return LineageStats.top_level(limit=limit)
  ```
  Aqui, `LineageStats.top_level` executa uma query SQL no banco do L2 e retorna o ranking de personagens por level.

---

## Exemplo de fluxo

1. Usuário acessa uma página de ranking no site.
2. O Django chama uma função utilitária (ex: `LineageStats.top_level`) que executa uma query SQL no banco do L2 via `LineageDB`.
3. O resultado é retornado e exibido no frontend.

---

## Vantagens dessa abordagem
- **Isolamento**: Dados do jogo e do site ficam separados, evitando conflitos e facilitando manutenção.
- **Performance**: Queries otimizadas diretamente no banco do L2.
- **Flexibilidade**: Possível adaptar para diferentes versões de banco do L2 (acis, essence, lucera, etc) apenas mudando as queries.

---

## Observações
- O acesso ao banco do L2 pode ser desativado via variável de ambiente (`LINEAGE_DB_ENABLED`).
- O cache interno reduz a carga em queries repetidas.
- Alterações no banco do L2 devem ser feitas com cuidado para não afetar o servidor do jogo. 