const mongoose = require("mongoose");

const processedDataSchema = new mongoose.Schema(
  {
    clientID: { type: String, required: true },
    DateTime: { type: Date, default: Date.now },
    mpuData: {
      Ax: { type: Number },
      Ay: { type: Number },
      Az: { type: Number },
      Gx: { type: Number },
      Gy: { type: Number },
      Gz: { type: Number },
    },
    predictions: {
      combined_prediction: { type: String },
      reliability_score: { type: String },
      model_predictions: {
        svm_prediction: { type: String },
        svm_confidence: { type: Number },
        rf_prediction: { type: String },
        rf_confidence: { type: Number },
        knn_prediction: { type: String },
        knn_confidence: { type: Number },
        xgb_prediction: { type: String },
        xgb_confidence: { type: Number },
      },
      lstm_prediction: { type: String },
      lstm_confidence: { type: Number },
      explanation: { type: String },
    },
    heart_rate: { type: Number }, // Added heart_rate field
    spo2: { type: Number }, // Added spo2 field
  },
  {
    collection: "ProcessedData", // Ensure this is the correct collection name in MongoDB
  }
);

module.exports = mongoose.model("ProcessedData", processedDataSchema);
