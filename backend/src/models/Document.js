const mongoose = require('mongoose');

const documentSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
  },
  filename: {
    type: String,
    required: true,
  },
  originalName: {
    type: String,
    required: true,
  },
  mimeType: {
    type: String,
    required: true,
  },
  size: {
    type: Number,
    required: true,
  },
  path: {
    type: String,
    required: true,
  },
  status: {
    type: String,
    enum: ['pending', 'processing', 'analyzed', 'error'],
    default: 'pending',
  },
  type: {
    type: String,
    enum: ['w2', '1099', 'other'],
    required: true,
  },
  analysis: {
    type: mongoose.Schema.Types.Mixed,
    default: null,
  },
  metadata: {
    type: mongoose.Schema.Types.Mixed,
    default: {},
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
  updatedAt: {
    type: Date,
    default: Date.now,
  },
});

// Update timestamp on save
documentSchema.pre('save', function(next) {
  this.updatedAt = Date.now();
  next();
});

// Index for faster queries
documentSchema.index({ user: 1, createdAt: -1 });
documentSchema.index({ status: 1 });

const Document = mongoose.model('Document', documentSchema);

module.exports = Document; 