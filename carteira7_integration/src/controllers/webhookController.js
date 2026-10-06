const { paymentsDB } = require('./paymentController');

// Mecanismo simples de idempotência
const processedWebhooks = new Set();

async function handleWebhook(req, res) {
    try {
        const payload = req.body;
        
        if (payload.event !== 'payment.confirmed') {
            return res.status(200).json({ message: 'Evento ignorado' });
        }

        const paymentData = payload.data;
        const identifier = paymentData.identifier;

        // Idempotência
        if (processedWebhooks.has(identifier)) {
            return res.status(200).json({ message: 'Webhook já processado' });
        }

        // Simula verificação no DB
        const payment = paymentsDB.get(identifier);
        
        if (payment) {
            payment.status = 'approved';
            payment.webhookProcessed = true;
            payment.updatedAt = new Date();
            paymentsDB.set(identifier, payment);
            
            // Marca como processado na idempotência
            processedWebhooks.add(identifier);
            
            console.log(`[Webhook] Pagamento ${identifier} aprovado com sucesso.`);
            return res.status(200).json({ received: true });
        } else {
            console.warn(`[Webhook] Pagamento ${identifier} não encontrado no banco de dados.`);
            return res.status(404).json({ error: 'Pagamento não encontrado' });
        }

    } catch (error) {
        console.error('Erro no processamento do webhook:', error);
        res.status(500).json({ error: 'Erro ao processar webhook' });
    }
}

module.exports = { handleWebhook };
