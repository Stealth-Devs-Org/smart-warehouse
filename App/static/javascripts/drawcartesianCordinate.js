function drawCartesianCoordinates() {

    const canvas = document.getElementById('coordinateCanvas');
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    const gridSpacing = 20;
    
    ctx.clearRect(0, 0, width, height);

    // Draw grid lines
    ctx.strokeStyle = '#e0e0e0'; // Light gray for grid lines
    ctx.lineWidth = 1;
    
    // Draw vertical grid lines
    for (let x = 0; x <= width; x += gridSpacing) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
    }
    
    // Draw horizontal grid lines
    for (let y = 0; y <= height; y += gridSpacing) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
    }

    // Draw X and Y axes
    ctx.strokeStyle = 'black'; // Black for axes
    ctx.lineWidth = 2;

    // X axis
    ctx.beginPath();
    ctx.moveTo(-100, height - gridSpacing);
    ctx.lineTo(width + 100, height - gridSpacing);
    ctx.stroke();

    // Y axis
    ctx.beginPath();
    ctx.moveTo(gridSpacing, height + gridSpacing + 100);  // Extend grid below
    ctx.lineTo(gridSpacing, -gridSpacing - 100); // Extend above
    ctx.stroke();

    // Draw X-axis labels
    ctx.textAlign = 'center';
    ctx.textBaseline = 'bottom';
    ctx.font = '12px Arial';
    for (let x = 0; x <= width; x += gridSpacing) {
        if (x !== 0) {
            ctx.fillText(x / gridSpacing - 1, x, height - gridSpacing + 15);
        }
    }

    // Draw Y-axis labels
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    for (let y = 0; y <= height; y += gridSpacing) {
        if (y !== height) {
            ctx.fillText(y / gridSpacing - 1, gridSpacing - 6, height - y);
        }
    }



    ////////floor Plan Sketching //////////
    //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    // Variables for the rectangle position 
    function drawRectangle(color, strokeWidth, startXCordinateForShape, startYCordinateForShape, rectWidth, rectHeight) {
                    ctx.strokeStyle = color; // Set the stroke color
                    ctx.lineWidth = strokeWidth; // Set the stroke width
            
                    // Calculate the rectangle's top-left corner based on the offsets
                    const rectX1 = gridSpacing + startXCordinateForShape * 20;
                    const rectY1 = 620 - startYCordinateForShape * 20;
            
                    // Draw the rectangle
                    ctx.beginPath();
                    ctx.rect(rectX1, rectY1, rectWidth * gridSpacing, rectHeight * gridSpacing);
                    ctx.stroke();
                }
            
    function drawLine(color, strokeWidth, startXCord, startYCord, EndXCor, EndYCor) {
                    ctx.strokeStyle = color; // Set the stroke color
                    ctx.lineWidth = strokeWidth; // Set the stroke width
                    
                    const lineStartX = gridSpacing + startXCord * 20;
                    const lineStartY = 620 - startYCord * 20;
                    const lineEndX = gridSpacing + EndXCor * 20;
                    const lineEndY = 620 - EndYCor * 20;
                    ctx.beginPath();
                    ctx.moveTo(lineStartX, lineStartY); // Start the line
                    ctx.lineTo(lineEndX, lineEndY); // End the line
                    ctx.stroke(); // Draw the line
                }
                
            


        

        function build() {  
            //floor outline
            drawLine('maroon', 4, 0, 0, 47, 0);
            drawLine('maroon', 4, 47, 0, 47, 9);
            drawLine('maroon', 4, 47, 9, 55, 9);
            drawLine('maroon', 4, 55, 9, 55, 30);
            drawLine('maroon', 4, 0, 0, 0, 30);
            drawLine('maroon', 4, 0, 30, 55, 30);
    
            //storage racks
            drawRectangle('blue', 2, 10.5, 27.5, 12, 2);
            drawRectangle('blue', 2, 24.5, 27.5, 12, 2);
    
            drawRectangle('blue', 2, 10.5, 24.5, 12, 2);
            drawRectangle('blue', 2, 24.5, 24.5, 12, 2);
    
            drawRectangle('blue', 2, 10.5, 21.5, 12, 2);
            drawRectangle('blue', 2, 24.5, 21.5, 12, 2);
    
            drawRectangle('blue', 2, 10.5, 18.5, 12, 2);
            drawRectangle('blue', 2, 24.5, 18.5, 12, 2);
    
            //agv pathline 
            drawRectangle('orange', 2, 9, 29, 29, 14);
            drawRectangle('orange', 2, 10,28, 27, 12);
            drawRectangle('orange', 2, 17, 13, 13, 9);
            drawRectangle('orange', 2, 16, 14, 15, 11);
    
            drawLine('orange', 2, 23, 29, 23, 3);
            drawLine('orange', 2, 24, 29, 24, 3);
    
            drawLine('orange', 2, 30, 12, 36,12);
            drawLine('orange', 2, 30, 11, 37,11);
            drawLine('orange', 2, 30, 10, 38,10);
            drawLine('orange', 2, 30, 9, 39,9);
    
    
            drawLine('orange', 2, 36, 12, 36,15);
            drawLine('orange', 2, 37, 11, 37,15);
            drawLine('orange', 2, 38, 10, 38,15);
            drawLine('orange', 2, 39, 9, 39,15);
            drawLine('orange', 2, 38, 15, 39,15);
    
    
            //charging dock
            drawRectangle('red', 2, 35.5, 13.5,1, 1);
            drawRectangle('red', 2, 36.5, 13.5, 1, 1);
            drawRectangle('red', 2, 37.5, 13.5, 1, 1);
            drawRectangle('red', 2, 38.5, 13.5, 1, 1);
    
    
    
            //inbound outbound racks
            drawRectangle('green', 2, 17.5, 12.5, 2, 8);
            drawRectangle('green', 2, 20.5, 12.5, 2, 8);
    
            drawRectangle('red', 2, 24.5, 12.5, 2, 8);
            drawRectangle('red', 2, 27.5, 12.5, 2, 8);
    
            // control room
            drawRectangle('black', 3, 0, 12, 5, 12);
    
    
    
        }


        build ();
            

        
             
    

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

}