const crypto = require("crypto");

function generateNonce() {
    return crypto.randomUUID();
}

module.exports = { generateNonce };
