# Administrator Manual

## Admin Access
- URL: `/admin/`
- Use the superuser created during installation.

## Management
- Users, permissions, content, and settings can be managed via the admin.
- Custom apps may have their own sections in the admin.

## Monitoring
- Logs are in `logs/`.
- Monitor Celery tasks via Flower (`/flower/`).
- Check the status of containers with `docker-compose ps`.

## Maintenance
- Run migrations whenever you update models:
  ```bash
  python manage.py migrate
  ```
- Use the admin for quick adjustments to data and settings.
- Data backup can be done via scripts in `setup/`. 