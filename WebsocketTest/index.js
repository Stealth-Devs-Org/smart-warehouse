const WebSocket = require('ws');
const port = process.env.PORT || 8080;  // Use a dynamic port for deployment platforms like Replit

// Create WebSocket server
const wss = new WebSocket.Server({ port });

// When a client connects
wss.on('connection', (ws) => {
  console.log('Client connected');

  // Send a message to the connected client
  ws.send('Welcome to the WebSocket server!');

  // When a message is received from the client
  ws.on('message', (message) => {
    console.log(`Received: ${message}`);

    // Send a reply to the client
    ws.send(`You said: ${message}`);
  });

  // Handle client disconnect
  ws.on('close', () => {
    console.log('Client disconnected');
  });
});

console.log(`WebSocket server is running on ws://localhost:${port}`);
