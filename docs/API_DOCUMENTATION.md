# API Documentation - Lineage 2 PDL

## Visão Geral

Esta API fornece acesso público aos dados do servidor Lineage 2, incluindo rankings, status de bosses, informações da Olimpíada e muito mais.

## Base URL

```
https://seu-dominio.com/api/
```

## Autenticação

As APIs públicas não requerem autenticação, mas possuem rate limiting para proteger contra abuso.

## Rate Limiting

- **APIs Públicas**: 30 requisições por minuto por IP
- **APIs de Usuário**: 100 requisições por minuto por usuário autenticado

## Endpoints

### Servidor

#### Jogadores Online
```http
GET /api/server/players-online/
```

**Resposta:**
```json
{
    "online_count": 150,
    "fake_players": 10,
    "real_players": 140
}
```

#### Ranking PvP
```http
GET /api/server/top-pvp/?limit=10
```

**Parâmetros:**
- `limit` (opcional): Número de registros (padrão: 10, máximo: 100)

**Resposta:**
```json
[
    {
        "char_name": "HeroPlayer",
        "level": 80,
        "clan_name": "Lendas",
        "class_name": "Warlord",
        "pvp_count": 1500
    }
]
```

#### Ranking PK
```http
GET /api/server/top-pk/?limit=10
```

**Parâmetros:**
- `limit` (opcional): Número de registros (padrão: 10, máximo: 100)

#### Ranking de Clãs
```http
GET /api/server/top-clan/?limit=10
```

**Resposta:**
```json
[
    {
        "clan_name": "Lendas",
        "leader_name": "HeroPlayer",
        "level": 5,
        "member_count": 50,
        "reputation": 10000
    }
]
```

#### Ranking de Riqueza (Adena)
```http
GET /api/server/top-rich/?limit=10
```

#### Ranking de Tempo Online
```http
GET /api/server/top-online/?limit=10
```

#### Ranking de Nível
```http
GET /api/server/top-level/?limit=10
```

### Olimpíada

#### Ranking da Olimpíada
```http
GET /api/server/olympiad-ranking/
```

**Resposta:**
```json
[
    {
        "char_name": "HeroPlayer",
        "class_name": "Warlord",
        "points": 2500,
        "rank": 1
    }
]
```

#### Todos os Heróis da Olimpíada
```http
GET /api/server/olympiad-heroes/
```

#### Heróis Atuais da Olimpíada
```http
GET /api/server/olympiad-current-heroes/
```

**Resposta:**
```json
[
    {
        "char_name": "HeroPlayer",
        "class_name": "Warlord",
        "hero_type": "current",
        "hero_count": 3,
        "hero_date": "2024-01-15"
    }
]
```

### Bosses

#### Status dos Grand Bosses
```http
GET /api/server/grandboss-status/
```

**Resposta:**
```json
[
    {
        "boss_name": "Antharas",
        "boss_id": 29019,
        "is_alive": false,
        "respawn_time": "2024-01-16T10:00:00Z",
        "location": "Antharas Lair"
    }
]
```

#### Localizações dos Boss Jewels
```http
GET /api/server/boss-jewel-locations/?ids=6656,6657,6658
```

**Parâmetros:**
- `ids` (obrigatório): IDs dos jewels separados por vírgula

**IDs Válidos:** 6656, 6657, 6658, 6659, 6660, 6661, 8191

**Resposta:**
```json
[
    {
        "jewel_id": 6656,
        "jewel_name": "Antharas Jewel",
        "location": "Antharas Lair",
        "coordinates": "131983, 114509, -3718",
        "respawn_time": "2024-01-16T10:00:00Z"
    }
]
```

### Cercos

#### Status dos Cercos
```http
GET /api/server/siege/
```

**Resposta:**
```json
[
    {
        "castle_name": "Aden",
        "castle_id": 1,
        "owner_clan": "Lendas",
        "siege_date": "2024-01-20T20:00:00Z",
        "is_under_siege": false
    }
]
```

#### Participantes do Cerco
```http
GET /api/server/siege-participants/1/
```

**Parâmetros:**
- `castle_id` (path): ID do castelo (1-9)

**Resposta:**
```json
[
    {
        "clan_name": "Lendas",
        "leader_name": "HeroPlayer",
        "member_count": 50,
        "registration_date": "2024-01-15T10:00:00Z"
    }
]
```

## Códigos de Status HTTP

- `200 OK`: Requisição bem-sucedida
- `400 Bad Request`: Parâmetros inválidos
- `404 Not Found`: Endpoint não encontrado
- `429 Too Many Requests`: Rate limit excedido
- `500 Internal Server Error`: Erro interno do servidor

## Exemplos de Uso

### JavaScript (Fetch)
```javascript
// Buscar jogadores online
fetch('/api/server/players-online/')
    .then(response => response.json())
    .then(data => console.log(data));

// Buscar top 10 PvP
fetch('/api/server/top-pvp/?limit=10')
    .then(response => response.json())
    .then(data => console.log(data));
```

### Python (Requests)
```python
import requests

# Buscar jogadores online
response = requests.get('https://seu-dominio.com/api/server/players-online/')
data = response.json()
print(data)

# Buscar top 10 PvP
response = requests.get('https://seu-dominio.com/api/server/top-pvp/', params={'limit': 10})
data = response.json()
print(data)
```

### cURL
```bash
# Jogadores online
curl -X GET "https://seu-dominio.com/api/server/players-online/"

# Top 10 PvP
curl -X GET "https://seu-dominio.com/api/server/top-pvp/?limit=10"
```

## Cache

As APIs utilizam cache para melhorar a performance:
- **Jogadores Online**: 30 segundos
- **Rankings**: 1 minuto
- **Olimpíada**: 5 minutos
- **Bosses**: 1 minuto
- **Cercos**: 5 minutos

## Documentação Interativa

Acesse a documentação interativa da API em:
```
https://seu-dominio.com/api/schema/swagger-ui/
```

## Suporte

Para suporte técnico ou dúvidas sobre a API, entre em contato através do Discord ou email do servidor. 