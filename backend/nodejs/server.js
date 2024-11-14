const express = require("express");
const http = require("http");
const socketIo = require("socket.io");
const mongoose = require("mongoose");
const HealthData = require("./health-data"); // HealthData model
const ProcessedData = require("./processedData"); // ProcessedData model
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

app.get("/irled.html", (req, res) => {
  res.sendFile(__dirname + "/public/irled.html");
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
/*
// Route to fetch processed MongoDB data from FastAPI
app.get("/process-mongodb-data", async (req, res) => {
  try {
    const response = await axios.get(
      "http://fastapi-app2:8001/process-mongodb-data"
    );
    res.json(response.data);
  } catch (err) {
    console.error("Error fetching MongoDB data:", err.message);
    res.status(500).send("Error fetching MongoDB data");
  }
});
*/ 

// Route to fetch processed MongoDB data from FastAPI
app.get("/process-mongodb-data", async (req, res) => {
  const { deviceId } = req.query; // Retrieve deviceId from query parameters
  const fastApiUrl = `http://fastapi-app2:8001/process-mongodb-data${deviceId ? `?deviceId=${deviceId}` : ""}`;

  try {
    const response = await axios.get(fastApiUrl);
    res.json(response.data);
  } catch (err) {
    console.error("Error fetching MongoDB data:", err.message);
    res.status(500).send("Error fetching MongoDB data");
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
      console.log("New HealthData entry detected:", change.fullDocument);

      const { DeviceID, IRLED, RedLED, MPU6050, DateTime } =
        change.fullDocument;
      const mpuValues = MPU6050.split(",").map(parseFloat);

      if (mpuValues.length === 6) {
        const [Ax, Ay, Az, Gx, Gy, Gz] = mpuValues;

        try {
          // Send data to FastAPI for processing
          const response = await axios.post(
            "http://localhost:8000/process_and_detect",
            {
              IRLED: IRLED,
              RedLED: RedLED,
            }
          );

          console.log("FastAPI response:", response.data);

          // Extract predictions and other fields from the response
          const {
            heart_rate,
            spo2,
            message,
            combined_prediction,
            reliability_score,
            model_predictions,
            lstm_prediction,
            lstm_confidence,
            explanation,
          } = response.data;

          // Ensure predictions exist before saving
          if (!model_predictions) {
            console.error("Predictions are missing in the FastAPI response");
          }

          const processedDataEntry = new ProcessedData({
            clientID: DeviceID, // Use DeviceID from MongoDB change event
            DateTime: new Date(), // Use DateTime from MongoDB change or the current date
            mpuData: {
              Ax,
              Ay,
              Az,
              Gx,
              Gy,
              Gz,
            },
            predictions: {
              combined_prediction, // Save combined prediction
              reliability_score, // Save reliability score
              model_predictions: {
                svm_prediction: model_predictions.svm_prediction,
                svm_confidence: model_predictions.svm_confidence,
                rf_prediction: model_predictions.rf_prediction,
                rf_confidence: model_predictions.rf_confidence,
                knn_prediction: model_predictions.knn_prediction,
                knn_confidence: model_predictions.knn_confidence,
                xgb_prediction: model_predictions.xgb_prediction,
                xgb_confidence: model_predictions.xgb_confidence,
              },
              lstm_prediction, // Save LSTM prediction
              lstm_confidence, // Save LSTM confidence
              explanation, // Save explanation
            },
            heart_rate, // Store heart rate from FastAPI response
            spo2, // Store SpO2 from FastAPI response
          });

          // Save the combined data to MongoDB
          await processedDataEntry.save();
          console.log(
            "Prediction result saved to ProcessedData:",
            processedDataEntry
          );

          // Emit the prediction result to all connected clients in real-time via Socket.IO
          io.emit("predictionResult", {
            ...change.fullDocument, // Send the original MongoDB data
            predictions: processedDataEntry.predictions, // Include the entire predictions object
            heart_rate, // Send heart rate
            spo2, // Send SpO2
          });
          console.log("Prediction result sent to clients");
        } catch (err) {
          console.error("Error processing data with FastAPI:", err);
        }
      } else {
        console.error("MPU6050 data is malformed or missing values:", MPU6050);
      }
    }
  });

  socket.on("disconnect", () => {
    console.log("Client disconnected");
    changeStream.close();
  });
});

// Endpoint to fetch all distinct device IDs (clientID)
app.get("/availableDeviceIds", async (req, res) => {
  try {
    // Fetch all unique client IDs (device IDs) from ProcessedData collection
    const deviceIds = await ProcessedData.distinct("clientID");
    res.json(deviceIds); // Return the list of available device IDs
  } catch (err) {
    console.error("Error fetching device IDs:", err);
    res.status(500).send("Error fetching device IDs");
  }
});

app.get("/latestProcessedData", async (req, res) => {
  const { deviceId } = req.query; // Get the deviceId from query params

  try {
    if (!deviceId) {
      return res.status(400).send("Device ID is required");
    }

    const latestData = await ProcessedData.find({ clientID: deviceId })
      .sort({ DateTime: -1 })
      .limit(1);

    if (latestData.length > 0) {
      res.json(latestData[0]); // Send the latest data as a response
    } else {
      res.status(404).send(`No data found for device: ${deviceId}`);
    }
  } catch (err) {
    console.error("Error fetching latest processed data:", err);
    res.status(500).send("Error fetching data");
  }
});

// Endpoint to fetch all data for a specific device ID from ProcessedData
app.get("/allProcessedData", async (req, res) => {
  const { deviceId } = req.query; // Get the deviceId from query params

  try {
    if (!deviceId) {
      return res.status(400).send("Device ID is required");
    }

    // Fetch all data entries for the specified clientID (device ID) and select only the desired fields
    const allData = await ProcessedData.find({ clientID: deviceId }, {
      _id: 1,
      clientID: 1,
      DateTime: 1,
      heart_rate: 1,
      spo2: 1
    }).sort({ DateTime: 1 });

    if (allData.length > 0) {
      res.json(allData); // Send the filtered data as a response
    } else {
      res.status(404).send(`No data found for device: ${deviceId}`);
    }
  } catch (err) {
    console.error("Error fetching all processed data:", err);
    res.status(500).send("Error fetching data");
  }
});


const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
