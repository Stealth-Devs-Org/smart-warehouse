const WebSocket = require('ws');
const port = process.env.PORT || 8080;


const wss = new WebSocket.Server({ port });


// function generateRandomAGVData() {  //random data
//   const agv = {
//     agv_id: 1,  
//     location: [
//       Math.floor(Math.random() * 10),        
//       Math.floor(Math.random() * 10)         
//     ],
//     segment: Math.floor(Math.random() * 5),   
//     status: Math.floor(Math.random() * 4),     // 0: idle, 1: moving, 2: loading, 3: unloading
//     timestamp: new Date().toISOString()       
//   };
//   return agv;
// }



// function generateRandomAGVData() {
//   const agv = {
//     agv_id: 1,  
//     location: [
//       15,        
//       0        
//     ],
//     segment: Math.floor(Math.random() * 5),   
//     status: Math.floor(Math.random() * 4),     // 0: idle, 1: moving, 2: loading, 3: unloading
//     timestamp: new Date().toISOString()       
//   };
//   return agv;
// }


function generateRandomAGVData() {
  let agv = {
    agv_id: 1,
    location: [15, 0],  
    segment: Math.floor(Math.random() * 5),
    status: Math.floor(Math.random() * 4),  // 0: idle, 1: moving, 2: loading, 3: unloading
    timestamp: new Date().toISOString()
  };

  let y = 0;  // Initialize y-coordinate

  setInterval(() => {
    agv.location = [15, y];  // Update location with incrementing y
    agv.segment = Math.floor(Math.random() * 5);
    agv.status = Math.floor(Math.random() * 4);
    agv.timestamp = new Date().toISOString();

    console.log(agv);  // Output the AGV data (you can replace this with any action)

    y++;  // Increment y-coordinate
  }, 1001);  // Run every 1001 milliseconds
}









wss.on('connection', (ws) => {
  console.log('Client connected');


  ws.send('Welcome');

  // Send data every 100 mil seconds
  const interval = setInterval(() => {
    const agvData = generateRandomAGVData();
    ws.send(JSON.stringify(agvData));  // Send
  }, 1000);

  
  ws.on('message', (message) => {
    console.log(`Received from client: ${message}`);
    ws.send(`You said: ${message}`);
  });

  ws.on('close', () => {
    console.log('Client disconnected');
    clearInterval(interval)
  });
});


console.log(`WebSocket server is running on ws://localhost:${port}`);
