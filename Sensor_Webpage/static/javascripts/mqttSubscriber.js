// const mqtt = require('mqtt');

// const BROKER = "mqtt://localhost"; 
// const PORT = 1883;
// const TOPIC1 = "/sensor_temperature";
// const TOPIC2 = "/sensor_airquality";

// const client = mqtt.connect(BROKER, { port: PORT });

// client.on('connect', function () {
//     console.log("Connected to MQTT Broker!");

//     client.subscribe(TOPIC1, function (err) {
//         if (!err) {
//             console.log(`Subscribed to ${TOPIC1}`);
//         }
//     });

//     client.subscribe(TOPIC2, function (err) {
//         if (!err) {
//             console.log(`Subscribed to ${TOPIC2}`);
//         }
//     });
// });

// client.on('message', function (topic, message) {
//     const payload = message.toString();
//     console.log(`Received: ${topic}: ${payload}`);
// });

// client.on('error', function (error) {
//     console.error("MQTT Error:", error);
// });
