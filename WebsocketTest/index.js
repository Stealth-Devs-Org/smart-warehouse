const WebSocket = require('ws');
const port = process.env.PORT || 8080;  


const wss = new WebSocket.Server({ port });

wss.on('connection', (ws) => {
  console.log('Client connected');


  ws.send('Welcome');

 
  ws.on('message', (message) => {
    console.log(`Received: ${message}`);

    ws.send(`You said: ${message}`);
  });

  
  ws.on('close', () => {                    // Handle client disconnect
    console.log('Client disconnected');
  });
});

console.log(`WebSocket server is running on ws://localhost:${port}`);
