const mongoose = require('mongoose');

const healthDataSchema = new mongoose.Schema({
    DateTime: { type: Date, default: Date.now },
    DeviceID: { type: String, required: true },
    HealthData: {
        HeartRate: { type: Number, required: true },
        OxygenLevel: { type: Number, required: true },
        AccelerometerData: {
            Ax: { type: Number, required: true },
            Ay: { type: Number, required: true },
            Az: { type: Number, required: true }
        }
    }
});

const HealthData = mongoose.model('HealthData', healthDataSchema, 'HealthData');

module.exports = HealthData;
