const mongoose = require("mongoose");

const tuningInformationSchema = new mongoose.Schema(
  {
    DeviceID: { type: String, required: true },
    AutoTuneIdeal: { type: Boolean, default: false },
    ESPUTD: { type: Boolean, default: false },
    TuningData: {
      LED1_CURRENT: { type: Number, default: 0 },
      LED3_CURRENT: { type: Number, default: 0 },
      GAIN: { type: Number, default: 0 },
      TIA_CAPACITOR: { type: Number, default: 0 },
      DateTime: { type: String, default: "" },
    },
    Battery: {
      Percentage: { type: Number, default: 0 },
    },
    IntervalSchedule: {
      IntervalMinutes: { type: Number, default: 10 },
    },
    MPU6050: {
      MotionDuration: { type: Number, default: 1 },
      Threshold: { type: Number, default: 20 },
    },
    MostRecentReadings: {
      GreenLED: { type: String, default: "" },
      IRLED: { type: String, default: "" },
      DateTime: { type: String, default: "" },
      LastUpdated: { type: String, default: "" },
      BatteryPercentage: { type: Number, default: 0 },
    },
    DateTime: { type: String, default: "" },
    LastUpdated: { type: String, default: "" },
  },
  { collection: "TuningInformation" } // Explicitly define the collection name
); // Allow additional fields

const TuningInformation = mongoose.model(
  "TuningInformation",
  tuningInformationSchema
);

module.exports = TuningInformation;
