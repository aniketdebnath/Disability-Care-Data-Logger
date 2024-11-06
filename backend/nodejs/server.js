const express = require("express");
const http = require("http");
const socketIo = require("socket.io");
const mongoose = require("mongoose");
const axios = require("axios");

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

// Serve static files from the "public" directory
app.use(express.static("public"));

// Route to serve irled.html directly
app.get("/irled.html", (req, res) => {
  res.sendFile(__dirname + "/public/irled.html");
});

// Route to fetch processed MongoDB data from FastAPI
app.get("/process-mongodb-data", async (req, res) => {
  try {
    // Fetch data from FastAPI
    const response = await axios.get("http://localhost:8000/process-mongodb-data");
    res.json(response.data);
  } catch (err) {
    console.error("Error fetching MongoDB data:", err);
    res.status(500).send("Error fetching MongoDB data");
  }
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
