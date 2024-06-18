const express = require('express');
const multer = require('multer');
const path = require('path');
const app = express();
const port = 3000;

// Set up static files directory
app.use(express.static(path.join(__dirname, 'public')));

// Set up multer for file uploads
const storage = multer.diskStorage({
  destination: './public/uploads/',
  filename: (req, file, cb) => {
    cb(null, Date.now() + path.extname(file.originalname));
  }
});
const upload = multer({ storage });

// Home route
app.get('/', (req, res) => {
  res.render('live_w_locator.html');
});

// Start server
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
