const mongoose = require("mongoose");

const deviceDataSchema = new mongoose.Schema(
  {
    _id: { type: mongoose.Schema.Types.ObjectId },
    DeviceID: { type: String, required: true }, // Adjusted to String to match your data
    DateTime: { type: String, required: true },
    GreenLED: { type: String, required: true },
    IRLED: { type: String, required: true },
    RedLED: { type: String, required: true },
    MPU6050: {
      Ax: { type: Number, required: true },
      Ay: { type: Number, required: true },
      Az: { type: Number, required: true },
      Gx: { type: Number, required: true },
      Gy: { type: Number, required: true },
      Gz: { type: Number, required: true },
    },
  },
  {
    collection: "HealthData", // Ensure this is the correct collection name in MongoDB
  }
);

const DeviceData = mongoose.model("DeviceData", deviceDataSchema);

module.exports = DeviceData;
