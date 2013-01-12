 
  function drawgraphs(data) {
   console.log("Function definitely works."+ data[0]);   
   var container = document.getElementById("editor-render-0");  
    horizontal = false, // Show horizontal bars
    d1 = [],                                  // First data series
    d2 = [];                               // Second data series
   var point;                                    // Data point variable declaration
   var i;

  for (i = 0; i < 4; i++) {
      point = [i, data[i]];
      d1.push(point);
      point = [i+0.5,data[i]-1];
      d2.push(point);
  };
              
  // Draw the graph
  Flotr.draw(
    container,
    [d1, d2],
    {
      bars : {
        show : true,
        horizontal : horizontal,
        shadowSize : 0,
        barWidth : 0.5
      },
      mouse : {
        track : true,
        relative : true
      },
      yaxis : {
        min : 0,
        autoscaleMargin : 1
      }
    }
  );
  }