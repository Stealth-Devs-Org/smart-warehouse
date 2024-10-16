// // Initialize the MQTT client
// const client = new Paho.MQTT.Client("localhost", 8000, "clientId-" + Math.random());

// client.onConnectionLost = onConnectionLost;
// client.onMessageArrived = onMessageArrived;

// function connectMQTT() {
//     const options = {
//         onSuccess: onConnect,
//         onFailure: onFailure
//     };
//     client.connect(options);
// }

// function onConnect() {
//     console.log("Connected to MQTT broker");
//     client.subscribe("/sensor_temperature");
// }

// function onFailure(err) {
//     console.error("Failed to connect to MQTT broker:", err);
// }

// function onConnectionLost(responseObject) {
//     if (responseObject.errorCode !== 0) {
//         console.error("Connection lost:", responseObject.errorMessage);
//         connectMQTT(); // Reconnect
//     }
// }

// function onMessageArrived(message) {
//     console.log("Message received:", message.payloadString);
//     const sensorData = JSON.parse(message.payloadString);  // Assuming sensor_state is sent as JSON
//     updateCanvas(sensorData);
// }

// function updateCanvas(sensorData) {
//     // Assuming the sensorData contains coordinates and temperature values
//     // Modify canvas drawing logic to place temperature points based on coordinates and temperature
//     const canvas = document.getElementById('coordinateCanvas');
//     const ctx = canvas.getContext('2d');

//     // Clear the canvas first
//     ctx.clearRect(0, 0, canvas.width, canvas.height);

//     // For example, if the sensorData contains { sensor_id: "(2,2)", temperature: 23.5 }
//     const sensorId = sensorData.sensor_id;  // Get the sensor coordinate
//     const temperature = sensorData.temperature;  // Get the temperature value
//     const coords = sensorId.replace(/[()]/g, '').split(',');  // Extract x, y coordinates

//     const x = parseInt(coords[0]) * 20;  // Scaling factor for the canvas
//     const y = parseInt(coords[1]) * 20;

//     // Draw temperature point
//     ctx.fillStyle = 'red';
//     ctx.beginPath();
//     ctx.arc(x, y, 10, 0, 2 * Math.PI);
//     ctx.fill();

//     // Display temperature value next to the point
//     ctx.fillStyle = 'black';
//     ctx.font = '12px Arial';
//     ctx.fillText(`${temperature}°C`, x + 15, y + 5);
// }

// window.onload = function () {
//     connectMQTT();
//     drawCartesianCoordinates();  // Assuming this function initializes the grid
// };
