

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
           


            
    