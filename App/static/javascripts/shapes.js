
<script src="drawcartesianCordinate">     </script>

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