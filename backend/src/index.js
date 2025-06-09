const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const fs = require('fs');
const path = require('path');

const app = express();
const port = process.env.PORT || 3001;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
app.use(limiter);

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

// Logging endpoint
app.post('/api/logs', (req, res) => {
  const { message, level = 'info' } = req.body;
  
  if (!message) {
    return res.status(400).json({ error: 'Message is required' });
  }

  const logEntry = {
    timestamp: new Date().toISOString(),
    level,
    message
  };

  // Ensure logs directory exists
  const logsDir = path.join(__dirname, '../logs');
  if (!fs.existsSync(logsDir)) {
    fs.mkdirSync(logsDir, { recursive: true });
  }

  // Write to log file
  const logFile = path.join(logsDir, 'tax-filer.log');
  fs.appendFileSync(logFile, JSON.stringify(logEntry) + '\n');

  res.json({ status: 'logged', entry: logEntry });
});

// Start server
if (require.main === module) {
  app.listen(port, () => {
    console.log(`Server running on port ${port}`);
  });
}

module.exports = app; // Export for testing 