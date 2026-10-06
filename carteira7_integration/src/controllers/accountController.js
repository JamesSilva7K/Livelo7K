const carteira7Service = require('../services/carteira7Service');

async function getBalance(req, res) {
    try {
        const response = await carteira7Service.getAccountBalance();
        res.json(response);
    } catch (error) {
        res.status(error.status || 500).json({ error: error.message || 'Erro interno' });
    }
}

module.exports = { getBalance };
