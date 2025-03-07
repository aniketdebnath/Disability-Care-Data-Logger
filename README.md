# Disability Care Datalogger

## 🚀 Project Overview
The **Disability Care Datalogger** is a real-time health monitoring system that integrates machine learning with hardware-based signal processing. It is designed to analyze **Photoplethysmography (PPG) signals** for heart rate variability and stress detection using a range of ML models. The system processes data from an **ESP32-C6 microcontroller** and transmits it to a backend hosted on **AWS EC2** using **FastAPI** and **Node.js**, ensuring low-latency, real-time insights.

![Disability Care Datalogger](https://l7ewz3hqkc.ufs.sh/f/LFPunsIWlVM1gQ8IkYojsKw7v2ZFE4ekIofizhSymNHAJ3CR)
![Disability Care Datalogger](https://l7ewz3hqkc.ufs.sh/f/LFPunsIWlVM1xQBhnfKOFR20S6pdEeX1fn7JsaKVPTQuMC94)
![Disability Care Datalogger](https://l7ewz3hqkc.ufs.sh/f/LFPunsIWlVM14BJwpSgfeZQwYCLzMKq5dnuTHy0bhXlBcF7V)

---

## 📌 Features

- **Real-Time Health Monitoring:** Continuous PPG signal processing from an ESP32-C6 microcontroller.
- **ML-Driven Anomaly Detection:** Real-time anomaly detection using Random Forest, SVM, KNN, and XGBoost models.
- **Stress Prediction:** LSTM-based stress analysis model trained with WESAD dataset.
- **Backend-Frontend Integration:** FastAPI backend for real-time processing, with frontend visualization using Node.js.
- **Cloud Deployment:** Deployed using Docker and NGINX on AWS EC2 for high scalability and reliability.
- **Data Storage:** MongoDB for secure storage of sensor data and machine learning outputs.
- **Sensor Calibration:** Real-time sensor tuning using AI-based predictions.
- **Adaptive Signal Processing:** Preprocessing of PPG signals to calculate BPM and RR intervals.
- **Interrupt-Based Synchronization:** Implemented interrupt-based timing between AFE4404 and ESP32 for precise data alignment and reduced signal loss.
- **Auto-Tuning with AI Feedback:** Dynamic tuning of sensor parameters (LED current, sampling rate, gain) based on AI-generated feedback from Random Forest and LSTM models.
- **Motion-Compensated Signal Processing:** Integrated MPU6050 accelerometer data to correct for motion artifacts and improve signal consistency.
- **Multi-Model Consensus for Anomaly Detection:** Combined results from Random Forest, SVM, KNN, and XGBoost to improve reliability of anomaly detection.
- **Custom Peak Detection Algorithm:** Replaced HeartPy with a custom peak detection algorithm for higher accuracy in BPM and IBI calculation.
- **Secure Real-Time Transmission:** Optimized HTTP POST requests and added retry mechanisms to ensure reliable communication between ESP32 and FastAPI.
- **Adaptive Gain Control:** AI-based tuning of LED current and TIA gain to improve signal-to-noise ratio under different environmental conditions.
- **Custom REST API:** Developed custom REST API for real-time data updates, parameter tuning, and anomaly detection.

---

## 🛠️ Tech Stack

### **Hardware**
- **ESP32-C6 Microcontroller** – For real-time sensor data acquisition.
- **AFE4404** – For pulse oximetry signal processing.
- **MPU6050** – For accelerometer and gyroscope data.

### **Backend**
- **FastAPI** – For real-time health data processing.
- **Node.js** – For handling API requests and data flow.
- **Docker + NGINX** – For containerized deployment.
- **AWS EC2** – For scalable cloud hosting.

### **Machine Learning Models**
- **Random Forest** – For anomaly detection.
- **SVM (Support Vector Machine)** – For signal classification.
- **KNN (K-Nearest Neighbors)** – For pattern matching.
- **XGBoost** – For enhanced prediction accuracy.
- **LSTM (Long Short-Term Memory)** – For stress prediction using time-series data.

### **Database**
- **MongoDB** – For secure storage of sensor data and model outputs.

---

## 📊 Data Flow

1. **Data Acquisition:**
   - The ESP32-C6 microcontroller collects PPG data using the AFE4404 sensor.
   - The microcontroller sends the data to the FastAPI backend over Wi-Fi.

2. **Signal Processing:**
   - Raw PPG signals are preprocessed (noise filtering, RR interval calculation).
   - Processed data is stored in MongoDB.

3. **Anomaly Detection:**
   - ML models (Random Forest, SVM, KNN, XGBoost) analyze PPG signals for anomalies.
   - LSTM model predicts stress levels based on RR intervals and heart rate variability.

4. **Real-Time Visualization:**
   - Results are transmitted to the frontend for real-time charting and insights.

---

## 🌐 Deployment

### **Deployed on AWS EC2**
- **Containerized with Docker** – Ensures consistent deployment.
- **NGINX Routing** – Handles API requests and static file serving.
- **MongoDB Atlas** – Cloud-hosted database for scalable storage.

### **Custom Domain & DNS Setup**
- **Step 1:** Set up DNS records for the custom domain.
- **Step 2:** Configure NGINX to route incoming traffic.
- **Step 3:** Ensure secure SSL/TLS encryption.

---

## 📄 Project Report

### **Team Contributions**
- **Thomas Pettigrew** – Firmware development, quality reflection, and project management.
- **Aniket Debnath** – Software development, AI model integration, data processing, and backend infrastructure.
- **Nam Tran** – Hardware development and sensor integration.
- **MD Sabil Sayad** – Requirement gathering and stakeholder management.
- **Brishlav Kayastha** – Software development and solution optimization.

### **Challenges and Solutions**
- **Noise in PPG Signals:** Resolved using bandpass filtering and adaptive tuning with AI feedback.
- **Sensor Synchronization:** Implemented interrupt-based timing for real-time data alignment.
- **Machine Learning Latency:** Fine-tuned models and reduced feedback loop timing.
- **Real-Time Data Transmission:** Ensured consistent signal flow with optimized HTTP POST requests.

### **Achievements**
✅ Developed an end-to-end health monitoring system.
✅ Integrated machine learning for real-time anomaly and stress detection.
✅ Deployed scalable backend and database on AWS.
✅ Achieved high accuracy in stress and anomaly detection models.
✅ Improved real-time data acquisition using AI-based tuning and adaptive signal processing.

### **Future Improvements**
- **Reduce AI Feedback Latency:** Move AI models to edge devices.
- **Improve Memory Efficiency:** Optimize data transmission and JSON handling.
- **Enhanced Security:** Add encryption and stricter data handling policies.

---

## 📜 License
This project is licensed under the **MIT License**. Contributions and modifications are welcome.

---

## ⭐ Contributing
Contributions are encouraged! If you'd like to add new features or improve the system, feel free to submit a pull request.


