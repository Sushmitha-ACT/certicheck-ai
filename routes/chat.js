const express = require('express');
const router = express.Router();
const ctrl = require('../controllers/chatController');

router.post('/', ctrl.chat);
router.post('', ctrl.chat);

module.exports = router;
