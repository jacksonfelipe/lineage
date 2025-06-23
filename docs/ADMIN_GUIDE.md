# Manual do Administrador

## Acesso ao Admin
- URL: `/admin/`
- Use o superusuário criado na instalação.

## Gerenciamento
- Usuários, permissões, conteúdos e configurações podem ser gerenciados via admin.
- Apps customizados podem ter seções próprias no admin.

## Monitoramento
- Logs em `logs/`.
- Monitoramento de tarefas Celery via Flower (`/flower/`).
- Verifique o status dos containers com `docker-compose ps`.

## Manutenção
- Rode migrações sempre que atualizar modelos:
  ```bash
  python manage.py migrate
  ```
- Use o admin para ajustes rápidos em dados e configurações.
- Backup dos dados pode ser feito via scripts em `setup/`. 