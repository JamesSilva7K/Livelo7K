const carteira7Service = require('../services/carteira7Service');
const crypto = require('crypto');

// Estrutura em memória simulando DB
const paymentsDB = new Map();

async function createPayment(req, res) {
    try {
        const { amount } = req.body;
        
        if (!amount || amount <= 0) {
            return res.status(400).json({ error: 'Valor inválido' });
        }

        const externalId = `order_${crypto.randomUUID()}`;
        const callbackUrl = 'https://seusite.com/webhook'; // em prod usar domínio real

        const response = await carteira7Service.createPix(amount, externalId, callbackUrl);
        
        if (response && response.payment) {
            // Persistir no DB mock
            paymentsDB.set(response.payment.id, {
                id: response.payment.id,
                externalId,
                amount,
                status: 'pending',
                pixCopiaECola: response.payment.pixCopiaECola,
                qrCodeBase64: response.payment.qrCodeBase64,
                createdAt: new Date(),
                webhookProcessed: false
            });

            return res.json({
                success: true,
                payment: {
                    id: response.payment.id,
                    externalId,
                    amount,
                    status: response.payment.status,
                    pixCopiaECola: response.payment.pixCopiaECola,
                    qrCodeBase64: response.payment.qrCodeBase64,
                    expiresAt: response.payment.expiresAt
                }
            });
        }
        
        throw new Error('Falha na resposta da API');

    } catch (error) {
        console.error('Erro ao criar pagamento:', error.message || error);
        res.status(error.status || 500).json({ error: error.message || 'Erro interno' });
    }
}

async function getStatus(req, res) {
    try {
        const { id } = req.params;
        const response = await carteira7Service.getPaymentStatus(id);
        res.json(response);
    } catch (error) {
        res.status(error.status || 500).json({ error: error.message || 'Erro interno' });
    }
}

module.exports = { createPayment, getStatus, paymentsDB };
