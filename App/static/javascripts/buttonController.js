const heatPoints = [];

function updateValue(sliderId) {
    const slider = document.getElementById(sliderId);
    const valueDisplay = document.getElementById('value' + sliderId.charAt(sliderId.length - 1));
    valueDisplay.innerText = slider.value;
}

function addHeatPoint() {
    const tempValue = parseInt(document.getElementById('slider1').value);
    const tempRadius = parseInt(document.getElementById('slider2').value);
    
    // Example coordinates, you can modify this to get actual coordinates from user input
    const xCoordinate = Math.floor(Math.random() * 40);  // Random X-coordinate
    const yCoordinate = Math.floor(Math.random() * 30);  // Random Y-coordinate
    
    // Add the new heat point
    heatPoints.push({ x: xCoordinate, y: yCoordinate, tempValue: tempValue, radius: tempRadius });
    
    // Redraw the entire canvas
    redrawCanvas();
}

function redrawCanvas() {
    const canvas = document.getElementById('coordinateCanvas');
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    // Clear the canvas before redrawing
    ctx.clearRect(0, 0, width, height);
    drawCartesianCoordinates();

    // Draw all heat points
    heatPoints.forEach(point => {
        const centerX = point.x * 20 + 20;
        const centerY = height - (point.y * 20 + 20);
        
        ctx.beginPath();
        ctx.arc(centerX, centerY, point.radius, 0, 2 * Math.PI);
        ctx.fillStyle = `rgba(255, 0, 0, 0.2)`; // Semi-transparent red for heat point
        ctx.fill();
        ctx.strokeStyle = 'red';
        ctx.stroke();
        
        // Draw temperature text inside the circle
        ctx.fillStyle = 'black'; 
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.font = '10px Arial';
        ctx.fillText(`${point.tempValue}`+"°C", centerX, centerY);
    });
}


