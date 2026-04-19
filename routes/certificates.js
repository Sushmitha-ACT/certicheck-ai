const Certificate = require('../models/certificate');
const express = require('express');
const fs = require('fs');
const path = require('path');
const jwt = require('jsonwebtoken');
const router = express.Router();
const multer = require('multer');
const ctrl = require('../controllers/certificateController');

const JWT_SECRET = process.env.JWT_SECRET || 'certicheck_secret';
const uploadsDir = path.join(__dirname, '../uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

function verifyAuth(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Unauthorized.' });
  }
  const token = authHeader.split(' ')[1];
  try {
    const payload = jwt.verify(token, JWT_SECRET);
    req.user = payload;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid or expired token.' });
  }
}

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, 'uploads/'),
  filename: (req, file, cb) => cb(null, Date.now() + '-' + file.originalname)
});
const upload = multer({ storage, limits: { fileSize: 10 * 1024 * 1024 } });

router.post('/upload', verifyAuth, upload.single('certificate'), ctrl.uploadCertificate);
router.post('/verify', verifyAuth, upload.single('certificate'), ctrl.uploadAndVerifyCertificate);
router.post('/verify/:id', ctrl.verifyCertificate);
router.get('/history', ctrl.getHistory);
router.get('/result/:id', ctrl.getResult);

module.exports = router;
