# Documentação de Integrações

## Banco do L2
- Integração via `apps.lineage.server.database.LineageDB`.
- Queries SQL diretas para dados do jogo.

## Pagamentos
- Integração com gateways de pagamento (ex: PagSeguro, PayPal, etc).
- Verifique o app `apps.lineage.payment` para detalhes.

## Notificações
- Envio de e-mails, notificações no site e integrações com Discord.
- Consulte `apps/main/notification/`.

## Como adicionar novas integrações
- Crie um app Django separado ou módulo em `utils/`.
- Siga o padrão de uso de variáveis de ambiente para segredos. 