document.addEventListener("DOMContentLoaded", function () {
  const deviceSelect = document.getElementById("device-select");
  const tuningInfoSection = document.getElementById("tuning-info");
  const updateTuningBtn = document.getElementById("update-tuning-btn");
  const autoTuneIdealInput = document.getElementById("autoTuneIdeal");
  const intervalMinutesInput = document.getElementById("intervalMinutes");

  // Fetch available device IDs
  fetch("/availableDeviceIds")
    .then((response) => response.json())
    .then((deviceIds) => {
      console.log("Available Device IDs:", deviceIds);

      // Populate the device select dropdown
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
        option.textContent = deviceId; // Text is the deviceId
        deviceSelect.appendChild(option);
      });
    })
    .catch((error) => {
      console.error("Error fetching device IDs:", error);
    });

  // Fetch tuning info for the selected device
  deviceSelect.addEventListener("change", (e) => {
    const selectedDeviceId = e.target.value;
    if (!selectedDeviceId) return; // Skip if no device is selected

    console.log("Fetching tuning information for deviceId:", selectedDeviceId); // Debugging line

    fetch(`/api/tuning/tuningInformation?deviceId=${selectedDeviceId}`)
      .then((response) => {
        console.log("Response status:", response.status); // Log status
        if (!response.ok) {
          console.error("Error fetching tuning info: ", response.status);
          throw new Error("Failed to fetch tuning info");
        }
        return response.json();
      })
      .then((data) => {
        console.log("Tuning info for device:", data); // Debugging line

        // Check if data is an array and access the first element
        const tuningData = Array.isArray(data) ? data[0] : data;

        // Display the tuning information
        tuningInfoSection.innerHTML = `
          <p>Device ID: ${tuningData.DeviceID}</p>
          <p>Auto Tune Ideal: ${tuningData.AutoTuneIdeal ? "Yes" : "No"}</p>
          <p>Interval Minutes: ${
            tuningData.IntervalSchedule
              ? tuningData.IntervalSchedule.IntervalMinutes
              : "N/A"
          }</p>
        `;

        // Populate the inputs for editing
        autoTuneIdealInput.checked = tuningData.AutoTuneIdeal;
        intervalMinutesInput.value = tuningData.IntervalSchedule
          ? tuningData.IntervalSchedule.IntervalMinutes
          : "";
      })
      .catch((error) => {
        console.error("Error fetching tuning info:", error);
        tuningInfoSection.innerHTML =
          "<p>Error fetching tuning information. Please check the device ID or try again later.</p>";
      });
  });

  // Update tuning information
  updateTuningBtn.addEventListener("click", () => {
    const selectedDeviceId = deviceSelect.value;
    const autoTuneIdeal = autoTuneIdealInput.checked;
    const intervalMinutes = intervalMinutesInput.value;

    if (!selectedDeviceId) {
      alert("Please select a device.");
      return;
    }

    if (intervalMinutes <= 0) {
      alert("Please enter a valid interval.");
      return;
    }

    console.log("Sending updated tuning information:", {
      deviceId: selectedDeviceId,
      autoTuneIdeal,
      intervalMinutes,
    }); // Debugging line

    // Send updated tuning information to the backend
    fetch("/api/tuning/updateTuningInformation", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        deviceId: selectedDeviceId,
        autoTuneIdeal,
        intervalMinutes,
      }),
    })
      .then((response) => {
        console.log("Update response status:", response.status); // Debugging line
        return response.json();
      })
      .then((data) => {
        console.log("Tuning info updated successfully:", data); // Debugging line
        alert("Tuning information updated successfully!");

        // Optionally update the UI with the new values
        tuningInfoSection.innerHTML = `
        <p>Device ID: ${data.DeviceID}</p>
        <p>Auto Tune Ideal: ${data.AutoTuneIdeal ? "Yes" : "No"}</p>
        <p>Interval Minutes: ${data.IntervalSchedule.IntervalMinutes}</p>
      `;
      })
      .catch((error) => {
        console.error("Error updating tuning info:", error);
        alert("Error updating tuning information. Please try again.");
      });
  });
});
