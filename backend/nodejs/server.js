const express = require("express");
const http = require("http");
const socketIo = require("socket.io");
const mongoose = require("mongoose");
const axios = require("axios");
const HealthData = require("./health-data"); // Assuming this is your Mongoose model

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

require("./db"); // Ensure MongoDB connection is established

// Serve static files from the "public" directory
app.use(express.static("public"));

// Route to serve 'detailHealth.html' and 'irled.html' directly
app.get("/detailHealth.html", (req, res) => {
  res.sendFile(__dirname + "/public/detailHealth.html");
});

app.get("/irled.html", (req, res) => {
  res.sendFile(__dirname + "/public/irled.html");
});

// Route to fetch health data from MongoDB
app.get("/health-data", async (req, res) => {
  try {
    const healthData = await HealthData.find({});
    res.json(healthData);
  } catch (err) {
    console.error("Error fetching health data:", err);
    res.status(500).send("Error fetching data");
  }
});

// Route to fetch processed MongoDB data from FastAPI
app.get("/process-mongodb-data", async (req, res) => {
  try {
    // Fetch data from FastAPI using Docker service name
    const response = await axios.get("http://fastapi-app2:8001/process-mongodb-data");
    res.json(response.data);
  } catch (err) {
    console.error("Error fetching MongoDB data:", err.message);
    res.status(500).send("Error fetching MongoDB data");
  }
});

// WebSocket connection handling
io.on("connection", async (socket) => {
  console.log("New client connected");
  socket.emit("message", "Welcome to the WebSocket server!");

  // Fetch the latest data from MongoDB on connection
  try {
    const latestData = await HealthData.findOne().sort({ DateTime: -1 });
    if (latestData) {
      socket.emit("healthDataUpdate", latestData);
    }
  } catch (err) {
    console.error("Error fetching latest data:", err);
  }

  // Watch the MongoDB collection for any new insertions or updates
  const changeStream = HealthData.watch();

  changeStream.on("change", async (change) => {
    if (change.operationType === "insert") {
      console.log("New PPG data inserted:", change.fullDocument);

      const ppgData = change.fullDocument.GreenLED;

      try {
        // Make a request to FastAPI to process the new PPG data
        const response = await axios.post(
          "http://fastapi-app:8000/api/process_and_detect",
          { GreenLED: ppgData }
        );

        console.log("FastAPI response:", response.data);

        // Emit the FastAPI prediction result to all connected clients
        io.emit("predictionResult", {
          ...change.fullDocument,
          predictions: response.data,
        });
        console.log("Prediction result sent to clients");
      } catch (err) {
        console.error("Error processing PPG data with FastAPI:", err);
      }
    }
  });

  socket.on("disconnect", () => {
    console.log("Client disconnected");
    changeStream.close();
  });
});

// Health check route to ensure server is running
app.get("/health", (req, res) => {
  res.send("Server is running and healthy!");
});

// Listen on specified port
const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
