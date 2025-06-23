# Automatizações e Tarefas Assíncronas

## Celery
- Usado para tarefas assíncronas (ex: envio de e-mails, processamento de dados).
- Workers definidos no serviço `celery` do Docker Compose.

## Celery Beat
- Agendador de tarefas periódicas.
- Exemplo: tarefas diárias, limpezas, notificações.

## Flower
- Dashboard para monitoramento de tarefas Celery.
- Acesse via `/flower/`.

## Como adicionar uma tarefa
- Crie uma função em `tasks.py` de algum app.
- Decore com `@shared_task` ou `@app.task`.

## Dicas
- Monitore o status das tarefas pelo Flower.
- Consulte logs em caso de falhas. 