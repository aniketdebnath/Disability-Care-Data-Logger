const mongoose = require('mongoose');

// Define the ClientList schema
const clientListSchema = new mongoose.Schema({
    ClientFirstName: { type: String, required: true },
    ClientLastName: { type: String, required: true },
    DeviceID: { type: String, required: true },
    DateOfCreation: { type: Date, default: Date.now }
});

// Create the ClientList model
const ClientList = mongoose.model('ClientList', clientListSchema, 'ClientList');

// Export the ClientList model
module.exports = ClientList;
