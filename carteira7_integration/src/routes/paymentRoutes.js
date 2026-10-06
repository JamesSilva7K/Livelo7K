const express = require('express');
const { createPayment, getStatus } = require('../controllers/paymentController');

const router = express.Router();

router.post('/', createPayment);
router.get('/:id/status', getStatus);

module.exports = router;
