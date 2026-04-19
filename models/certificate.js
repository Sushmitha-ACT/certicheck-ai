const mongoose = require('mongoose');

const ReasonSchema = new mongoose.Schema({
  issue: String,
  detail: String,
  severity: { type: String, enum: ['high', 'medium', 'low'] }
}, { _id: false });

const CertificateSchema = new mongoose.Schema({
  fileName: { type: String, required: true },
  filePath: String,
  fileSize: Number,
  mimeType: String,
  status: { type: String, enum: ['pending', 'processing', 'verified', 'error'], default: 'pending' },
  verificationResult: { type: String, enum: ['REAL', 'FAKE', 'SUSPICIOUS'] },
  confidenceScore: { type: Number, min: 0, max: 100 },
  analysisDetails: [ReasonSchema],
  institution: String,
  riskLevel: { type: String, enum: ['Low', 'Medium', 'High', 'Critical'] },
  aiReport: String,
  verifiedAt: Date
}, { timestamps: true });

module.exports = mongoose.model('Certificate', CertificateSchema);