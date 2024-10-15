const express = require("express");
const http = require("http");
const socketIo = require("socket.io");
const mongoose = require("mongoose");
const HealthData = require("./health-data"); // Assuming this is your Mongoose model
const axios = require("axios");

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

require("./db"); // Ensure your MongoDB connection is established

// Serve static files from the "public" directory
app.use(express.static("public"));

// Route to serve detailhealth.html directly
app.get("/detailHealth.html", (req, res) => {
  res.sendFile(__dirname + "/public/detailHealth.html");
});

// Route to fetch health data from MongoDB
app.get("/health-data", async (req, res) => {
  try {
    const healthData = await HealthData.find({});
    res.json(healthData);
  } catch (err) {
    console.error(err);
    res.status(500).send("Error fetching data");
  }
});

io.on("connection", async (socket) => {
  console.log("New client connected");

  // Fetch the latest data from MongoDB
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
          {
            GreenLED: ppgData,
          }
        );

        console.log("FastAPI response:", response.data);

        // Emit the FastAPI prediction result to all connected clients in real-time via Socket.IO
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

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
