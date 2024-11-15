const socket = io();

// Connect event: Fired when the client connects to the server
socket.on("connect", () => {
  console.log("Connected to server");
});

// Fetch available device IDs (clientIDs) to populate the dropdown
fetchAvailableDeviceIds();

// Function to fetch available device IDs from the backend
function fetchAvailableDeviceIds() {
  fetch("/availableDeviceIds")
    .then((response) => response.json())
    .then((deviceIds) => {
      console.log("Available Device IDs:", deviceIds);

      // Populate the device select dropdown
      const deviceSelect = document.getElementById("device-select");
      deviceSelect.innerHTML = ""; // Clear existing options

      // Add a default "Please select a device" option
      const defaultOption = document.createElement("option");
      defaultOption.value = "";
      defaultOption.textContent = "Please select a device";
      deviceSelect.appendChild(defaultOption);

      // Add each device ID as an option
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

// Listen for the latest processed data updates from the server
socket.on("latestDataUpdate", (data) => {
  console.log("Latest data received:", data);

  // Update heart rate and oxygen saturation (SpO₂) on the page
  updateData("heart-rate-value", data.heart_rate, "Heart Rate");
  updateData("spo2-value", data.spo2, "Oxygen Saturation (SpO₂)");

  // Update accelerometer data (MPU)
  if (data.mpuData) {
    updateAccelerometerData(data.mpuData);
  }
});

// General function to update health data sections
function updateData(elementId, value, label) {
  const element = document.getElementById(elementId);
  element.textContent = `${label}: ${value || "N/A"}`;
}

// Function to update accelerometer data display
function updateAccelerometerData(accelData) {
  document.getElementById("ax").textContent = accelData.Ax
    ? accelData.Ax.toFixed(3)
    : "N/A";
  document.getElementById("ay").textContent = accelData.Ay
    ? accelData.Ay.toFixed(3)
    : "N/A";
  document.getElementById("az").textContent = accelData.Az
    ? accelData.Az.toFixed(3)
    : "N/A";
}

// Function to fetch the latest data for the selected device
function fetchLatestData() {
  const deviceId = document.getElementById("device-select").value;

  // Check if deviceId is selected
  if (!deviceId) {
    alert("Please select a device");
    return;
  }

  // Fetch the latest data for the selected device
  fetch(`/latestProcessedData?deviceId=${deviceId}`)
    .then((response) => response.json())
    .then((data) => {
      // Update the dashboard with the fetched data
      updateData("heart-rate-value", data.heart_rate, "Heart Rate");
      updateData("spo2-value", data.spo2, "Oxygen Saturation (SpO₂)");

      // Update accelerometer data (MPU)
      if (data.mpuData) {
        updateAccelerometerData(data.mpuData);
      }
    })
    .catch((error) => {
      console.error("Error fetching latest data:", error);
    });
}

// Event listener for device select dropdown change
document
  .getElementById("device-select")
  .addEventListener("change", fetchLatestData);

// Initial fetch for available device IDs when the page loads
fetchAvailableDeviceIds();
