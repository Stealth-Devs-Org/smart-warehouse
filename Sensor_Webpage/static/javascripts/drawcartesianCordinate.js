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

    function drawTransparentPolygon(fillColor, strokeColor, strokeWidth, coordinates) {
                    // Set the stroke color for the border
                    ctx.strokeStyle = strokeColor; 
                    // Set the fill color with transparency using RGBA
                    ctx.fillStyle = fillColor;   
                    ctx.lineWidth = strokeWidth; // Set the stroke width
                    
                    // Start the path for the polygon
                    ctx.beginPath();
                    
                    // Move to the first point of the polygon
                    const startX = gridSpacing + coordinates[0][0] * 20;
                    const startY = 620 - coordinates[0][1] * 20;
                    ctx.moveTo(startX, startY);
                    
                    // Loop through the rest of the coordinates and draw lines to them
                    for (let i = 1; i < coordinates.length; i++) {
                        const x = gridSpacing + coordinates[i][0] * 20;
                        const y = 620 - coordinates[i][1] * 20;
                        ctx.lineTo(x, y);
                    }
                    
                    // Close the path and fill the polygon with transparency
                    ctx.closePath();
                    ctx.fill();   // Fill the polygon with the transparent color
                    ctx.stroke(); // Draw the slightly darker border
        }

        function drawTextLabel(text, xCoordinate, yCoordinate, fontSize, color) {
            // Set the text color and font size
            ctx.fillStyle = color || 'black';  // Default to black if no color is provided
            ctx.font = `${fontSize || 16}px Arial`;  // Default to 16px Arial if no font size is provided
            
            // Convert the coordinates to match the canvas' coordinate system
            const labelXPos = gridSpacing + xCoordinate * 20;
            const labelYPos = 620 - yCoordinate * 20;
            
            // Draw the text label at the specified coordinates
            ctx.fillText(text, labelXPos, labelYPos);
        }
        
        function drawFilledCircle(color, x, y, radius, label) {
            // Set the fill and stroke color for the circle
            ctx.fillStyle = color;
            ctx.strokeStyle = 'black';
            ctx.lineWidth = 1;
            
            // Calculate the coordinates based on the grid system
            const circleX = gridSpacing + x * 20;
            const circleY = 620 - y * 20;
            
            // Draw the filled circle
            ctx.beginPath();
            ctx.arc(circleX, circleY, radius, 0, Math.PI * 2, false);
            ctx.fill();  // Fill the circle with the specified color
            ctx.stroke(); // Draw the outline of the circle
            
            // Add text label
            ctx.fillStyle = 'black'; // Set text color
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.font = '6px Arial';
            ctx.fillText(label, circleX, circleY); // Display label at the circle's center
        }
        
                
            


        

        function build() {  
            // //floor outline
            drawLine('maroon', 4, 0, 0, 47, 0);
            drawLine('maroon', 4, 47, 0, 47, 9);
            drawLine('maroon', 4, 47, 9, 55, 9);
            drawLine('maroon', 4, 55, 9, 55, 30);
            drawLine('maroon', 4, 0, 0, 0, 30);
            drawLine('maroon', 4, 0, 30, 55, 30);


            
            // outer black box for HVAC
            drawTransparentPolygon('rgba(0, 0, 0, 1)', 'rgb(0, 0, 0)', 1,[
                [55,26],
                [58,26],
                [58, 30],
                [55,30]
            ]);
    
            // //storage racks
            // drawRectangle('blue', 2, 10.5, 27.5, 12, 2);
            // drawRectangle('blue', 2, 24.5, 27.5, 12, 2);
    
            // drawRectangle('blue', 2, 10.5, 24.5, 12, 2);
            // drawRectangle('blue', 2, 24.5, 24.5, 12, 2);
    
            // drawRectangle('blue', 2, 10.5, 21.5, 12, 2);
            // drawRectangle('blue', 2, 24.5, 21.5, 12, 2);
    
            // drawRectangle('blue', 2, 10.5, 18.5, 12, 2);
            // drawRectangle('blue', 2, 24.5, 18.5, 12, 2);
    
            // //agv pathline 
            // drawRectangle('orange', 2, 9, 29, 29, 14);
            // drawRectangle('orange', 2, 10,28, 27, 12);
            // drawRectangle('orange', 2, 17, 13, 13, 9);
            // drawRectangle('orange', 2, 16, 14, 15, 11);
    
            // drawLine('orange', 2, 23, 29, 23, 3);
            // drawLine('orange', 2, 24, 29, 24, 3);
    
            // drawLine('orange', 2, 30, 12, 36,12);
            // drawLine('orange', 2, 30, 11, 37,11);
            // drawLine('orange', 2, 30, 10, 38,10);
            // drawLine('orange', 2, 30, 9, 39,9);
    
    
            // drawLine('orange', 2, 36, 12, 36,15);
            // drawLine('orange', 2, 37, 11, 37,15);
            // drawLine('orange', 2, 38, 10, 38,15);
            // drawLine('orange', 2, 39, 9, 39,15);
            // drawLine('orange', 2, 38, 15, 39,15);
    
    
            // //charging dock
            // drawRectangle('red', 2, 35.5, 13.5,1, 1);
            // drawRectangle('red', 2, 36.5, 13.5, 1, 1);
            // drawRectangle('red', 2, 37.5, 13.5, 1, 1);
            // drawRectangle('red', 2, 38.5, 13.5, 1, 1);
    
    
    
            // //inbound outbound racks
            // drawRectangle('green', 2, 17.5, 12.5, 2, 8);
            // drawRectangle('green', 2, 20.5, 12.5, 2, 8);
    
            // drawRectangle('red', 2, 24.5, 12.5, 2, 8);
            // drawRectangle('red', 2, 27.5, 12.5, 2, 8);
    
            // // control room
            // drawRectangle('black', 3, 0, 12, 5, 12);


            
            
            
            
            // partitions ####################################################
            
            drawTransparentPolygon('rgba(88, 42, 42, 0.5)', 'rgb(88, 42, 42)', 1,[
                [0,0],
                [5,0],
                [5, 12],
                [0,12]
            ]);

            drawTransparentPolygon('rgba(139, 0, 0, 0.5)', 'rgb(139, 0, 0)', 1,[
                [7.5,14.5],
                [7.5,30],
                [0, 30],
                [0,12],
                [5,12]
            ]);

            drawTransparentPolygon('rgba(0, 0, 139, 0.5)', 'rgb(0, 0, 239)', 1,[
                [7.5,14.5],
                [23.5,14.5],
                [23.5, 30],
                [7.5,30]
            ]);

            drawTransparentPolygon('rgba(0, 139, 0, 0.5)', 'rgb(0, 239, 0)', 1,[
                [5,12],
                [5,0],
                [23.5, 0],
                [23.5, 14.5],
                [7.5,14.5]
            ]);

            drawTransparentPolygon('rgba(0, 139, 139, 0.5)', 'rgb(0, 239, 239)', 1,[
                [23.5,0],
                [47,0],
                [47,9],
                [41, 14.5],
                [23.5, 14.5]
            ]);

            drawTransparentPolygon('rgba(139, 139, 0, 0.5)', 'rgb(239, 239, 0)', 1,[
                [23.5,14.5],
                [41,14.5],
                [41,30 ],
                [23.5, 30]
            ]);

            drawTransparentPolygon('rgba(139, 0, 139, 0.5)', 'rgb(239,0, 239)', 1,[
                [47,9],
                [55,9],
                [55,30 ],
                [41, 30],
                [41,14.5]
            ]);

            // // Draw the labels for each partition
            drawTextLabel("Part 0", 3.5, 6, 16);
            drawTextLabel("Part 1", 14.5, 7, 16);
            drawTextLabel("Part 2", 35, 7, 16);
            drawTextLabel("Part 3", 4, 21, 16);
            drawTextLabel("Part 4", 16, 22, 16);
            drawTextLabel("Part 5", 33, 22, 16);
            drawTextLabel("Part 6", 49, 20, 16);




            ////////////////// Sensor Sketch Part //////////////////////////////
            
            function drawSensors( partitions, color) {
                let labelCounter = 1; // Label for the sensors
                let colorused = color;
                partitions.forEach((partition, partitionIndex) => {
                    partition.forEach(coordinate => {
                        const [x, y] = coordinate.split(',').map(Number); // Split and convert coordinates to numbers
                        drawFilledCircle(colorused, x, y,6, labelCounter.toString()); // Draw the sensor
                        labelCounter++; // Increment label for the next sensor
                    });
                });
            }
            
            // // Draw the Temp sensors for each partition
            const partitionsTempSensors = [
                // Partition 1
                ["2,2", "2,10"],
                
                // Partition 2
                ["9,11", "19,11", "19,3", "9,3"],
                
                // Partition 3
                ["28,11", "41,11", "28,3", "41,3"],
                
                // Partition 4
                ["5,15", "2,28", "5,28", "2,19"],
                
                // Partition 5
                ["12,27", "19,27", "19,17", "12,17"],
                
                // Partition 6
                ["52,13", "52,26", "46,17", "46,24"],

                // Partition 7
                ["28,18", "36,18", "28,27", "36,27"]
                
            ];

 
            // // Draw the Air Quality sensors for each partition
            const partitionsAirQualitySensors = [
                // Partition 1
                ["2,4", "2,8"],
                
                // Partition 2
                ["14,3", "14,11"],
                
                // Partition 3
                ["34,3", "34,11"],
                
                // Partition 4
                ["3,16", "3,26"],
                
                // Partition 5
                ["15,17", "15,27"],
                
                // Partition 6
                ["32,18", "32,27"],

                // Partition 7
                ["49,14", "49,27"]
                
            ];
            

             // // Draw the Air Quality sensors for each partition
             const partitionsHumiditySensors = [
                // No partion for humidty

                ["4,3","4,9","3,22","15,23","36,6"]

                
 
                
            ];

             // // Draw the Smoke sensors for each partition
             const partitionsSmokeSensors = [

                [
                    "1,29", "3,29", "5,29", "7,29", "9,29", "11,29", "13,29", "15,29", "17,29", "19,29",
                    "21,29", "23,29", "25,29", "27,29", "29,29", "31,29", "33,29", "35,29", "37,29", "39,29",
                    "41,29", "43,29", "45,29", "47,29", "49,29", "51,29", "53,29"
                ],


                [
                    "54,10", "54,12", "54,14", "54,16", "54,18", "54,20", "54,22", "54,24", "54,26", "54,28"
                ],

                ["52,10","50,10", "48,10","46,10"],

                [
                    "1,1", "3,1", "5,1", "7,1", "9,1", "11,1", "13,1", "15,1", "17,1", "19,1",
                    "21,1", "23,1", "25,1", "27,1", "29,1", "31,1", "33,1", "35,1", "37,1", "39,1",
                    "41,1", "43,1", "45,1"
                ],

                [
                    "1,3", "1,5", "1,7", "1,9", "1,11", "1,13", "1,15", "1,17", "1,19", "1,21",
                    "1,23", "1,25", "1,27"
                ],
                [
                    "46,2", "46,4", "46,6", "46,8"
                ]
            ];
            


            drawSensors(partitionsTempSensors,'red');
            drawSensors(partitionsAirQualitySensors,'green');
            drawSensors(partitionsHumiditySensors,'lightblue');
            drawSensors(partitionsSmokeSensors,'grey');

        }


            
    build();
    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

}