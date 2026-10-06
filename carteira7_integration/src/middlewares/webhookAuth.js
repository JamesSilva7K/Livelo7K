const env = require('../config/env');
const { verifySignature } = require('../utils/hmac');

function webhookAuth(req, res, next) {
    const signature = req.headers['x-c7-signature'];
    const timestamp = req.headers['x-c7-timestamp'];
    
    if (!signature || !timestamp) {
        return res.status(401).json({ error: 'Faltam headers de autenticação do webhook' });
    }

    // Importante: precisamos do raw body como string para a assinatura ser validada corretamente
    // Vamos assumir que o middleware express.json() guardou o body bruto em req.rawBody
    const bodyStr = req.rawBody || JSON.stringify(req.body);

    const isValid = verifySignature(env.C7_WEBHOOK_SECRET, timestamp, bodyStr, signature);

    if (!isValid) {
        return res.status(401).json({ error: 'Assinatura inválida ou expirada' });
    }

    next();
}

module.exports = webhookAuth;
