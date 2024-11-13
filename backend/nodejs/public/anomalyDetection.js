const socket = io();

// Fetch available device IDs to populate the dropdown
function fetchAvailableDeviceIds() {
  fetch("/availableDeviceIds")
    .then((response) => response.json())
    .then((deviceIds) => {
      const deviceSelect = document.getElementById("device-select");
      deviceSelect.innerHTML = ""; // Clear existing options

      // Add default option
      const defaultOption = document.createElement("option");
      defaultOption.value = "";
      defaultOption.textContent = "Please select a device";
      deviceSelect.appendChild(defaultOption);

      // Populate the dropdown with available device IDs
      deviceIds.forEach((deviceId) => {
        const option = document.createElement("option");
        option.value = deviceId;
        option.textContent = deviceId;
        deviceSelect.appendChild(option);
      });
    })
    .catch((error) => {
      console.error("Error fetching device IDs:", error);
    });
}

// Fetch and display the latest data for the selected device
function fetchLatestData() {
  const deviceId = document.getElementById("device-select").value;

  // Check if deviceId is selected
  if (!deviceId) {
    alert("Please select a device");
    return;
  }

  fetch(`/latestProcessedData?deviceId=${deviceId}`)
    .then((response) => response.json())
    .then((data) => {
      console.log("Latest data received:", data);

      // Update Combined Prediction and Reliability Score
      document.getElementById("combined-prediction").textContent =
        data.predictions.combined_prediction || "N/A";
      document.getElementById("reliability-score").textContent =
        data.predictions.reliability_score || "-";

      // Update individual model predictions and confidence
      updateModelPrediction(
        "svm",
        data.predictions.model_predictions.svm_prediction,
        data.predictions.model_predictions.svm_confidence
      );
      updateModelPrediction(
        "rf",
        data.predictions.model_predictions.rf_prediction,
        data.predictions.model_predictions.rf_confidence
      );
      updateModelPrediction(
        "xgb",
        data.predictions.model_predictions.xgb_prediction,
        data.predictions.model_predictions.xgb_confidence
      );
      updateModelPrediction(
        "knn",
        data.predictions.model_predictions.knn_prediction,
        data.predictions.model_predictions.knn_confidence
      );

      // Update LSTM Prediction and Confidence for Stress Detection
      updateLstmPrediction(
        data.predictions.lstm_prediction,
        data.predictions.lstm_confidence
      );
    })
    .catch((error) => {
      console.error("Error fetching latest data:", error);
    });
}

// Function to update model predictions and confidence, keeping confidence as decimal with 2 points
function updateModelPrediction(model, prediction, confidence) {
  document.getElementById(`${model}-prediction`).textContent =
    prediction || "N/A";
  const confidenceDecimal = confidence ? confidence.toFixed(2) : "-";
  document.getElementById(`${model}-confidence`).textContent =
    confidenceDecimal || "-";
}

// Function to update LSTM prediction and confidence, keeping confidence as decimal with 2 points
function updateLstmPrediction(prediction, confidence) {
  document.getElementById("lstm-prediction").textContent = prediction || "N/A";
  const confidenceDecimal = confidence ? confidence.toFixed(2) : "-";
  document.getElementById("lstm-confidence").textContent =
    confidenceDecimal || "-";
}

// Event listener for device select dropdown change
document
  .getElementById("device-select")
  .addEventListener("change", fetchLatestData);

// Initial fetch for available device IDs when the page loads
fetchAvailableDeviceIds();
