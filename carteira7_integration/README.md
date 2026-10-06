# Integração Carteira do 7

Integração completa, segura e profissional com a API da Carteira do 7.

## Configuração

1. Clone o repositório
2. Rode `npm install`
3. Copie `.env.example` para `.env` e preencha as credenciais.
4. Rode `npm run dev`

## Rotas Internas

- `POST /api/payments`: Cria um pagamento PIX
- `GET /api/payments/:id/status`: Consulta o status
- `POST /api/account/balance`: Consulta saldo

## Webhook

- `POST /webhook`: Recebe notificações de pagamento aprovado. Validado via HMAC-SHA256.
