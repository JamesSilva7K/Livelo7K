const crypto = require("crypto");
const env = require("../config/env");

function signRequest(apiSecret, bodyStr) {
    const timestamp = Math.floor(Date.now() / 1000).toString();
    const nonce = crypto.randomUUID();
    const signature = crypto
        .createHmac("sha256", apiSecret)
        .update(timestamp + "." + nonce + "." + bodyStr)
        .digest("hex");
    return { timestamp, nonce, signature };
}

function verifySignature(apiSecret, timestamp, bodyStr, receivedSignature) {
    // Validação de tempo (max 5 mins)
    const now = Math.floor(Date.now() / 1000);
    if (Math.abs(now - parseInt(timestamp)) > 300) {
        return false;
    }

    const expectedSignature = crypto
        .createHmac("sha256", apiSecret)
        .update(timestamp + "." + bodyStr)
        .digest("hex");

    return crypto.timingSafeEqual(
        Buffer.from(expectedSignature, 'utf8'),
        Buffer.from(receivedSignature, 'utf8')
    );
}

module.exports = { signRequest, verifySignature };
