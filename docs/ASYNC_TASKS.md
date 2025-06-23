# Automations and Asynchronous Tasks

## Celery
- Used for asynchronous tasks (e.g., sending emails, data processing).
- Workers are defined in the `celery` service of Docker Compose.

## Celery Beat
- Scheduler for periodic tasks.
- Example: daily tasks, cleanups, notifications.

## Flower
- Dashboard for monitoring Celery tasks.
- Access via `/flower/`.

## How to add a task
- Create a function in the `tasks.py` of an app.
- Decorate it with `@shared_task` or `@app.task`.

## Tips
- Monitor the status of tasks using Flower.
- Check logs in case of failures. 