# Disability Care Data Logger - Node.js Server

This is the Node.js backend for the Disability Care Data Logger project, responsible for real-time health data monitoring, serving data from MongoDB, and interacting with FastAPI for anomaly detection.

## Features

- Real-time health data updates using **Socket.IO**.
- Integration with **MongoDB** for health data storage and updates.
- Communicates with **FastAPI** for processing PPG data and anomaly detection.

## Prerequisites

- **Node.js**: v16 or higher
- **MongoDB**: Ensure MongoDB is running either locally or using MongoDB Atlas.
- **FastAPI**: Ensure your FastAPI service is running on `localhost:8000`.

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/disability-care-data-logger.git
   cd disability-care-data-logger/backend/nodejs
   ```

2. Install the dependencies:

   ```bash
   npm install
   ```

3. Set up your environment variables in a `.env` file:

   ```
   MONGO_URI=mongodb+srv://FYPUSERS:k1iTgwyFFzGlAkeN@fyptestdb.d7zdlnq.mongodb.net/FYPData
   ```

4. Run the server:
   ```bash
   npm start
   ```

The server will be running at `http://localhost:3000
