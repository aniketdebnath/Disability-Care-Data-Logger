const mongoose = require("mongoose");
require("dotenv").config(); // Load environment variables from .env file

const connectionString = process.env.MONGO_URI; // Fetch from environment variables

mongoose
  .connect(connectionString)
  .then(() => console.log("MongoDB connected successfully!"))
  .catch((err) => console.error("MongoDB connection error:", err));
