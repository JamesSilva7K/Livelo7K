const axios = require('axios');
const env = require('../config/env');
const { signRequest } = require('../utils/hmac');
const { handleCarteira7Error } = require('../utils/errors');

class Carteira7Service {
    constructor() {
        this.client = axios.create({
            baseURL: env.API_BASE_URL,
            headers: {
                'Authorization': `Bearer ${env.C7_API_KEY}`,
                'Content-Type': 'application/json'
            }
        });
    }

    async executeRequest(method, endpoint, payload = null) {
        let headers = {};
        
        if (payload) {
            const bodyStr = JSON.stringify(payload);
            const { timestamp, nonce, signature } = signRequest(env.C7_API_SECRET, bodyStr);
            
            headers['X-C7-Timestamp'] = timestamp;
            headers['X-C7-Nonce'] = nonce;
            headers['X-C7-Signature'] = signature;
        }

        try {
            const response = await this.client({
                method,
                url: endpoint,
                data: payload,
                headers
            });
            return response.data;
        } catch (error) {
            if (error.response && error.response.status === 429) {
                // Rate limited implement backoff - simplistic version
                console.warn('Rate limited. Aguardando para tentar novamente...');
                await new Promise(resolve => setTimeout(resolve, 2000));
                return this.executeRequest(method, endpoint, payload); // Simplistic retry
            }
            throw handleCarteira7Error(error);
        }
    }

    async createPix(amount, externalId, callbackUrl) {
        const payload = {
            amount: parseFloat(amount),
            callbackUrl,
            externalId
        };
        return this.executeRequest('POST', '/payment/create', payload);
    }

    async getPaymentStatus(id) {
        return this.executeRequest('GET', `/payment/${id}/status`);
    }

    async getAccountBalance() {
        return this.executeRequest('POST', '/account/balance', {});
    }
}

module.exports = new Carteira7Service();
