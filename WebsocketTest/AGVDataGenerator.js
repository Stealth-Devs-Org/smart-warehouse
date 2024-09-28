const WebSocket = require('ws');
const port = process.env.PORT || 8080;


const wss = new WebSocket.Server({ port });


function generateRandomAGVData() {
  const agv = {
    agv_id: 1,  
    location: [
      Math.floor(Math.random() * 10),        
      Math.floor(Math.random() * 10)         
    ],
    segment: Math.floor(Math.random() * 5),   
    status: Math.floor(Math.random() * 4),     // 0: idle, 1: moving, 2: loading, 3: unloading
    timestamp: new Date().toISOString()       
  };
  return agv;
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
