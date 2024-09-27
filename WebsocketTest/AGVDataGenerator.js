const WebSocket = require('ws');
const port = process.env.PORT || 8080;


const wss = new WebSocket.Server({ port });


function generateRandomAGVData() {                            //generate random AGV data
  const agv = {
    agv_id: Math.floor(Math.random() * 100),  
    location: {
      x: Math.floor(Math.random() * 10),    
      y: Math.floor(Math.random() * 10),    
    },
    segment: Math.floor(Math.random() * 5),   
    status: Math.floor(Math.random() * 4),    // 0: idle, 1: moving, 2: loading, 3: unloading
    timestamp: new Date().toISOString()      
  };
  return agv;
}


wss.on('connection', (ws) => {
  console.log('Client connected');


  ws.send('Welcome');

  // AGV data every 5 seconds
  const interval = setInterval(() => {
    const agvData = generateRandomAGVData();
    ws.send(JSON.stringify(agvData));  
  }, 5000);


  ws.on('message', (message) => {
    console.log(`Received from client: ${message}`);
    ws.send(`You said: ${message}`);
  });


  ws.on('close', () => {
    console.log('Client disconnected');
    clearInterval(interval);  
  });
});


console.log(`WebSocket server is running on ws://localhost:${port}`);
