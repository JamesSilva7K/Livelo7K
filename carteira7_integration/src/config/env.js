require('dotenv').config();

module.exports = {
    API_BASE_URL: process.env.API_BASE_URL || 'https://api.carteirado7.com/v2',
    C7_API_KEY: process.env.C7_API_KEY,
    C7_API_SECRET: process.env.C7_API_SECRET,
    C7_WEBHOOK_SECRET: process.env.C7_WEBHOOK_SECRET,
    PORT: process.env.PORT || 3000
};
