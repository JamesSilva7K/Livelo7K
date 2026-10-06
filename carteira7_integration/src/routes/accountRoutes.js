const express = require('express');
const { getBalance } = require('../controllers/accountController');

const router = express.Router();

router.post('/balance', getBalance);

module.exports = router;
