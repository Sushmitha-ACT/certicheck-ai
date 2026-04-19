const express = require('express');
const mongoose = require('mongoose');
const dotenv = require('dotenv');
const cors = require('cors');

dotenv.config();

const app = express();

app.use(cors());
app.use(express.json({ type: ['application/json', 'text/plain'] }));

const certificateRoutes = require('./routes/certificates');
const authRoutes = require('./routes/auth');
const chatController = require('./controllers/chatController');

app.use('/api/auth', authRoutes);
app.post('/api/chat', chatController.chat);
app.use('/api', certificateRoutes);

mongoose.connect(process.env.MONGO_URI)
.then(() => console.log("MongoDB connected"))
.catch(err => console.log("MongoDB error:", err));

app.get('/', (req, res) => {
    res.send("CertiCheck API Running");
});

const PORT = process.env.PORT || 5000;


app.listen(PORT, () => {
    console.log(`CertiCheck backend running on port ${PORT}`);
});
