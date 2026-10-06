const express = require('express');
const webhookAuth = require('../middlewares/webhookAuth');
const { handleWebhook } = require('../controllers/webhookController');

const router = express.Router();

router.post('/', webhookAuth, handleWebhook);

module.exports = router;
