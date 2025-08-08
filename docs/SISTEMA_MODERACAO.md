# 🛡️ Sistema de Moderação - Documentação

## 📋 Visão Geral

O sistema de moderação foi desenvolvido para manter a qualidade e segurança da rede social, permitindo que moderadores gerenciem conteúdo, usuários e denúncias de forma eficiente e transparente.

## 🏗️ Arquitetura do Sistema

### Modelos Principais

#### 1. **Report** (Denúncias)
- **Propósito**: Gerenciar denúncias de conteúdo ou usuários
- **Campos principais**:
  - `reporter`: Usuário que fez a denúncia
  - `report_type`: Tipo da denúncia (spam, inappropriate, harassment, etc.)
  - `status`: Status da denúncia (pending, reviewing, resolved, dismissed)
  - `priority`: Prioridade baseada no tipo (urgent, high, medium, low)
  - `reported_post/comment/user`: Conteúdo reportado
  - `assigned_moderator`: Moderador responsável
  - `moderator_notes`: Notas do moderador

#### 2. **ModerationAction** (Ações de Moderação)
- **Propósito**: Registrar ações tomadas pelos moderadores
- **Tipos de ação**:
  - `warn`: Advertência
  - `hide_content`: Ocultar conteúdo
  - `delete_content`: Deletar conteúdo
  - `suspend_user`: Suspender usuário
  - `ban_user`: Banir usuário
  - `restrict_user`: Restringir usuário
  - `approve_content`: Aprovar conteúdo
  - `feature_content`: Destacar conteúdo

#### 3. **ContentFilter** (Filtros de Conteúdo)
- **Propósito**: Filtros automáticos para detectar conteúdo inadequado
- **Tipos de filtro**:
  - `keyword`: Palavras-chave específicas
  - `regex`: Expressões regulares
  - `spam_pattern`: Padrões de spam
  - `url_pattern`: Padrões de URL
- **Ações**:
  - `flag`: Marcar para revisão
  - `auto_hide`: Ocultar automaticamente
  - `auto_delete`: Deletar automaticamente
  - `notify_moderator`: Notificar moderador

#### 4. **ModerationLog** (Logs de Moderação)
- **Propósito**: Registrar todas as ações de moderação para auditoria
- **Campos**:
  - `moderator`: Moderador que executou a ação
  - `action_type`: Tipo da ação
  - `target_type/id`: Alvo da ação
  - `description`: Descrição da ação
  - `ip_address`: IP do moderador
  - `user_agent`: User agent do navegador

## 🎯 Funcionalidades Principais

### 1. **Sistema de Denúncias**

#### Para Usuários:
- Denunciar posts, comentários ou usuários
- Selecionar tipo de denúncia
- Fornecer descrição detalhada
- Receber confirmação da denúncia

#### Para Moderadores:
- Visualizar denúncias por prioridade
- Atribuir denúncias a moderadores
- Aplicar ações de moderação
- Resolver denúncias com notas

### 2. **Painel de Moderação**

#### Dashboard Principal:
- Estatísticas em tempo real
- Denúncias pendentes e urgentes
- Ações recentes
- Gráficos de atividade
- Links rápidos para ações

#### Lista de Denúncias:
- Filtros avançados (tipo, status, prioridade, data)
- Busca por texto
- Ordenação personalizada
- Ações em massa
- Paginação

### 3. **Filtros Automáticos**

#### Tipos de Filtro:
- **Spam**: Palavras comerciais, medicamentos, jogos de azar
- **Linguagem**: Palavrões, expressões inadequadas
- **URLs**: Encurtadores suspeitos, múltiplas URLs
- **Conteúdo**: Repetitivo, CAPS excessivo

#### Ações Automáticas:
- Marcar para revisão manual
- Ocultar automaticamente
- Deletar automaticamente
- Notificar moderadores

### 4. **Sistema de Logs**

#### Auditoria Completa:
- Todas as ações registradas
- IP e user agent dos moderadores
- Histórico de mudanças
- Exportação de logs

## 🔧 Configuração e Instalação

### 1. **Migrações**
```bash
python manage.py makemigrations social
python manage.py migrate
```

### 2. **Configurar Filtros Padrão**
```bash
python manage.py setup_moderation
```

### 3. **Configurar Middleware**
Adicionar ao `settings.py`:
```python
MIDDLEWARE = [
    # ... outros middlewares
    'middlewares.content_filter_middleware.ContentFilterMiddleware',
    'middlewares.content_filter_middleware.SpamProtectionMiddleware',
]
```

### 4. **Configurar Permissões**
```python
# Criar grupo de moderadores
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.main.social.models import Report, ModerationAction, ContentFilter, ModerationLog

moderator_group = Group.objects.create(name='Moderadores')

# Adicionar permissões
permissions = [
    'social.can_moderate_reports',
    'social.can_view_reports',
    'social.can_take_moderation_actions',
    'social.can_view_moderation_actions',
    'social.can_view_moderation_logs',
]

for perm_name in permissions:
    permission = Permission.objects.get(codename=perm_name)
    moderator_group.permissions.add(permission)
```

## 📊 URLs do Sistema

### Denúncias:
- `/social/report/<content_type>/<content_id>/` - Denunciar conteúdo

### Painel de Moderação:
- `/social/moderation/` - Dashboard principal
- `/social/moderation/reports/` - Lista de denúncias
- `/social/moderation/reports/<id>/` - Detalhes da denúncia

### Filtros:
- `/social/moderation/filters/` - Gerenciar filtros
- `/social/moderation/filters/<id>/edit/` - Editar filtro
- `/social/moderation/filters/<id>/toggle/` - Ativar/desativar filtro

### Logs:
- `/social/moderation/logs/` - Visualizar logs

### Ações:
- `/social/moderation/bulk-action/` - Ações em massa

## 🎨 Interface do Usuário

### Templates Principais:
- `moderation/dashboard.html` - Painel principal
- `moderation/reports_list.html` - Lista de denúncias
- `moderation/report_detail.html` - Detalhes da denúncia
- `moderation/content_filters.html` - Gerenciar filtros
- `moderation/logs.html` - Logs de moderação
- `report_content.html` - Formulário de denúncia

### Características:
- Design responsivo com Bootstrap
- Ícones FontAwesome
- Gráficos interativos (Chart.js)
- Tabelas com ordenação e filtros
- Formulários com validação

## 🔒 Segurança e Permissões

### Permissões do Sistema:
- `can_moderate_reports`: Moderar denúncias
- `can_view_reports`: Visualizar denúncias
- `can_take_moderation_actions`: Tomar ações de moderação
- `can_view_moderation_actions`: Visualizar ações
- `can_view_moderation_logs`: Visualizar logs

### Controles de Acesso:
- Apenas usuários autenticados podem denunciar
- Apenas moderadores podem acessar painel
- Logs de todas as ações para auditoria
- Validação de entrada em todos os formulários

## 📈 Estatísticas e Analytics

### Métricas Coletadas:
- Total de denúncias
- Denúncias por tipo
- Tempo médio de resolução
- Ações por moderador
- Efetividade dos filtros
- Tendências de atividade

### Gráficos Disponíveis:
- Atividade dos últimos 30 dias
- Distribuição de tipos de denúncia
- Performance dos moderadores
- Efetividade dos filtros

## 🚀 Funcionalidades Avançadas

### 1. **Ações em Massa**
- Selecionar múltiplas denúncias
- Aplicar ação em lote
- Atribuir a moderadores
- Processamento assíncrono

### 2. **Filtros Inteligentes**
- Detecção automática de spam
- Análise de padrões
- Aprendizado com ações anteriores
- Configuração flexível

### 3. **Notificações**
- Alertas para denúncias urgentes
- Notificações de ações tomadas
- Relatórios periódicos
- Integração com sistema de notificações

### 4. **API de Moderação**
- Endpoints para ações programáticas
- Integração com sistemas externos
- Webhooks para notificações
- Autenticação via tokens

## 🔧 Manutenção e Monitoramento

### Comandos Úteis:
```bash
# Configurar filtros padrão
python manage.py setup_moderation

# Verificar estatísticas
python manage.py shell
>>> from apps.main.social.models import Report, ModerationAction
>>> Report.objects.count()
>>> ModerationAction.objects.filter(created_at__date=timezone.now().date()).count()

# Exportar logs
python manage.py shell
>>> from apps.main.social.models import ModerationLog
>>> logs = ModerationLog.objects.all()
>>> # Exportar para CSV
```

### Monitoramento:
- Verificar logs de erro
- Monitorar performance dos filtros
- Acompanhar estatísticas de uso
- Revisar ações dos moderadores

## 🎯 Melhorias Futuras

### Funcionalidades Planejadas:
1. **IA para Moderação**:
   - Detecção automática de conteúdo inadequado
   - Análise de sentimento
   - Sugestões de ação para moderadores

2. **Sistema de Apelação**:
   - Usuários podem apelar de ações
   - Revisão por supervisores
   - Processo transparente

3. **Moderação Comunitária**:
   - Usuários confiáveis podem moderar
   - Sistema de reputação
   - Votação em ações

4. **Integração Externa**:
   - APIs de verificação de spam
   - Serviços de análise de conteúdo
   - Integração com redes sociais

## 📞 Suporte

Para dúvidas ou problemas com o sistema de moderação:

1. Verificar logs de erro
2. Consultar documentação
3. Contatar equipe de desenvolvimento
4. Abrir issue no repositório

---

**Versão**: 1.0  
**Última atualização**: Dezembro 2024  
**Desenvolvido por**: Equipe de Desenvolvimento
