# Integrations Documentation

## L2 Database
- Integration via `apps.lineage.server.database.LineageDB`.
- Direct SQL queries for game data.

## Payments
- Integration with payment gateways (e.g., PagSeguro, PayPal, etc).
- Check the `apps.lineage.payment` app for details.

## Notifications
- Sending emails, on-site notifications, and integrations with Discord.
- See `apps/main/notification/`.

## How to add new integrations
- Create a separate Django app or a module in `utils/`.
- Follow the pattern of using environment variables for secrets. 