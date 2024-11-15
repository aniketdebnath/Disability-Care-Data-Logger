const mongoose = require("mongoose");

const connectionString =
  "mongodb+srv://FYPUSERS:k1iTgwyFFzGlAkeN@fyptestdb.d7zdlnq.mongodb.net/FYPData";

mongoose
  .connect(connectionString, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then(() => console.log("MongoDB connected successfully!"))
  .catch((err) => console.error("MongoDB connection error:", err));

module.exports = mongoose;
