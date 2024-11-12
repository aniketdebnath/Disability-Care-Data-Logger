const socket = io();

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('healthDataUpdate', function (data) {
    console.log('Data received:', data);
    if (data.HealthData) {
        updateData('heart-rate', data.HealthData.HeartRate, 'Heart Rate');
        updateData('oxygen-saturation', data.HealthData.OxygenLevel, 'Oxygen Saturation');
        updateAccelerometerData(data.HealthData.AccelerometerData);
    }
});

socket.on('processResult', function (data) {
    console.log('Data received:', data);
    if (data.processedData) {
        if (data.DeviceID === deviceID) {
            updateData('heart-rate', data.processedData.heart_rate.toFixed(2), 'Heart Rate');
        }
        //updateData('oxygen-saturation', data.HealthData.OxygenLevel, 'Oxygen Saturation');
        //updateAccelerometerData(data.HealthData.AccelerometerData);
    }
});

// Function to get query parameter by name
function getQueryParam(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// Retrieve deviceID from query string
const deviceID = getQueryParam('deviceID');
// Update the href with the DeviceID query parameter
document.querySelector('a[href="/irled.html"]').href = `/irled.html?DeviceID=${deviceID}`;

// Listen for prediction results and update the prediction section if deviceID matches
socket.on('predictionResult', function (data) {
    console.log('Prediction result received:', data);
    // Check if the deviceID in the data matches the one from the query string
    if (data.DeviceID === deviceID) {
        // Update SVM Prediction
        document.getElementById('svm-prediction').textContent = data.predictions.svm_prediction;
        document.getElementById('svm-confidence').textContent = `Confidence: ${data.predictions.svm_confidence.toFixed(2)}`;

        // Update Random Forest Prediction
        document.getElementById('rf-prediction').textContent = data.predictions.rf_prediction;
        document.getElementById('rf-confidence').textContent = `Confidence: ${data.predictions.rf_confidence.toFixed(2)}`;

        // Update KNN Prediction
        document.getElementById('knn-prediction').textContent = data.predictions.knn_prediction;
        document.getElementById('knn-confidence').textContent = `Confidence: ${data.predictions.knn_confidence.toFixed(2)}`;
    }
});


function updateData(elementId, value, label) {
    const element = document.getElementById(elementId);
    const content = `<h2>${label}</h2><p>Value: ${value}</p>`;
    element.innerHTML = content;
}

function updateAccelerometerData(accelData) {
    if (accelData) {
        document.getElementById('ax').textContent = accelData.Ax.toFixed(3);
        document.getElementById('ay').textContent = accelData.Ay.toFixed(3);
        document.getElementById('az').textContent = accelData.Az.toFixed(3);
    }
}

socket.on('disconnect', () => {
    console.log('Disconnected from server');
});

document.getElementById('detail-link').addEventListener('click', () => {
    const latestData = localStorage.getItem('latestHealthData');
    if (latestData) {
        localStorage.setItem('detailHealthData', latestData);
    }
});
