const express = require('express');
const cors = require('cors');
const env = require('./config/env');

const paymentRoutes = require('./routes/paymentRoutes');
const accountRoutes = require('./routes/accountRoutes');
const webhookRoutes = require('./routes/webhookRoutes');

const app = express();

// Middleware para salvar o raw body necessário para validação do HMAC do webhook
app.use(express.json({
    verify: (req, res, buf) => {
        req.rawBody = buf.toString('utf8');
    }
}));

app.use(cors());

// Rotas internas do sistema
app.use('/api/payments', paymentRoutes);
app.use('/api/account', accountRoutes);

// Rotas para receber webhooks externos da Carteira 7
app.use('/webhook', webhookRoutes);

app.listen(env.PORT, () => {
    console.log(`🚀 API Carteira do 7 Server rodando na porta ${env.PORT}`);
});
