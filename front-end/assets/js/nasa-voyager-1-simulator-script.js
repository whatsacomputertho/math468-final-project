//TODO: Refactor
const HOST = '127.0.0.1';
const PORT = 3000;

var isDrawing = false;
var restoreArray = [];
var index = -1;

function prepareSlider()
{
    //Get slider element
    var slider = document.querySelector('#noisy-encoded-drawing__slider');
    slider.defaultValue = 0;    
}

function prepareCanvas()
{
    //Get canvas elements
    var canvases = document.querySelectorAll('.drawing__canvas')

    //Fill canvas elements with all white
    for(i = 0; i < canvases.length; i++)
    {
        var width = canvases[i].width;
        var height = canvases[i].height;
        var context = canvases[i].getContext("2d");
        context.fillStyle = "white";
        context.fillRect(0, 0, width, height);
    }
}

function prepareDrawing()
{
    //Get drawing canvas
    var canvas = document.querySelector('#drawing__canvas');

    //Get drawing controls
    var clearButton = document.querySelector('#controls__clear-button');
    var undoButton = document.querySelector('#controls__undo-button');
    var stroke = document.querySelector('#controls__stroke-slider');
    var errorRateSlider = document.querySelector('#noisy-encoded-drawing__slider')

    //Add canvas event listeners
    canvas.addEventListener("touchstart", start, false);
    canvas.addEventListener("mousedown", start, false);
    canvas.addEventListener("touchmove", draw, false);
    canvas.addEventListener("mousemove", draw, false);
    canvas.addEventListener("touchend", stop, false);
    canvas.addEventListener("mouseup", stop, false);
    canvas.addEventListener("mouseout", stop, false);

    //Add controls event listeners
    clearButton.addEventListener("click", clear, false);
    undoButton.addEventListener("click", undo, false);
    errorRateSlider.addEventListener("change", reTransmit, false);

    //Set default stroke
    stroke.defaultValue = 2;
}

function start(event)
{
    //Get drawing canvas
    var canvas = document.querySelector('#drawing__canvas');

    //Get canvas context
    var context = canvas.getContext("2d");
    
    //Set the drawing flag
    isDrawing = true;

    //Prepare the path
    context.beginPath();
    context.moveTo(event.clientX - canvas.offsetLeft, event.clientY - canvas.offsetTop);
    event.preventDefault();
}

function draw(event)
{
    if(isDrawing)
    {
        //Get drawing canvas
        var canvas = document.querySelector('#drawing__canvas');

        //Get stroke and color control values
        var stroke = document.querySelector('#controls__stroke-slider');
        var color = document.querySelector('#controls__color-picker');

        //Get canvas context
        var context = canvas.getContext("2d");

        //Actually draw the path
        context.lineTo(event.clientX - canvas.offsetLeft, event.clientY - canvas.offsetTop);
        context.strokeStyle = color.value;
        context.lineWidth = stroke.value;
        context.lineCap = "round";
        context.lineJoin = "round";
        context.stroke();
    }
}

function stop(event)
{
    if(isDrawing)
    {
        //Get drawing canvas
        var canvas = document.querySelector('#drawing__canvas');

        //Get canvas context
        var context = canvas.getContext("2d");

        //End the path
        context.stroke();
        context.closePath();
        isDrawing = false;
        event.preventDefault();

        //Write the updated image data to memory for undo
        var width = canvas.width;
        var height = canvas.height;
        restoreArray.push(context.getImageData(0, 0, width, height));
        index += 1;
        if(restoreArray.length > 32)
        {
            restoreArray.splice(0, 1);
        }

        encodeImage(context.getImageData(0, 0, width, height));
    }
}

function clear()
{
    //Get drawing canvas
    var canvas = document.querySelector('#drawing__canvas');

    //Get canvas context
    var context = canvas.getContext("2d");

    //Overwrite the entire canvas with white
    var width = canvas.width;
    var height = canvas.height;
    context.fillStyle = "white";
    context.fillRect(0, 0, width, height);

    //Overwrite the restore array and reset index
    restoreArray = [];
    index = -1
}

function undo()
{
    //If index is 0 or -1 we know that there has been at most 1 line drawn
    if(index <= 0)
    {
        //We simply clear the canvas
        clear();
    }
    else
    {
        //Get drawing canvas
        var canvas = document.querySelector('#drawing__canvas');

        //Get canvas context
        var context = canvas.getContext("2d");

        //Overwrite the entire canvas with previous image data
        index -= 1;
        restoreArray.pop();
        context.putImageData(restoreArray[index], 0, 0);
    }
}

function writeImage(canvas, imageData)
{
    //Get canvas context
    var context = canvas.getContext("2d");

    //Write the image data
    context.putImageData(imageData, 0, 0);
}

function reTransmit()
{
    //Get encoded image data
    var canvas = document.querySelector('#encoded-drawing__canvas');
    var width = canvas.width;
    var height = canvas.height;
    var context = canvas.getContext("2d");
    imageData = context.getImageData(0, 0, width, height)

    //Get error rate slider
    var errorRateSlider = document.querySelector('#noisy-encoded-drawing__slider')

    //Transmit the image
    transmitImage(imageData, errorRateSlider.value);
}

function encodeImage(imageData)
{
    //Instantiate the request
    var req = new XMLHttpRequest();
    req.open("POST", `http://${HOST}:${PORT}/extended-binary/encode-image`);
    req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    //This function will execute when the request is fulfilled
    req.onload = function()
    {
        //Get response
        var data = JSON.parse(this.response);
        
        //Convert array to Uint8ClampedArray
        data.data = new Uint8ClampedArray(data.data);

        //Create ImageData
        var encodedImage = new ImageData(data.data, data.width, data.height);

        //Display ImageData
        var canvas = document.querySelector('#encoded-drawing__canvas');
        writeImage(canvas, encodedImage);

        //Get error rate slider
        var errorRateSlider = document.querySelector('#noisy-encoded-drawing__slider')

        //Transmit the image
        transmitImage(encodedImage, errorRateSlider.value);
    };

    //Send the request
    req.send(JSON.stringify({ "height" : imageData.height, "width" : imageData.width, "informationBits" : imageData.data }));
}

function transmitImage(imageData, errorRate)
{
    //Instantiate the request
    var req = new XMLHttpRequest();
    req.open("POST", `http://${HOST}:${PORT}/binary-channel/transmit-image`);
    req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    console.log("running")

    //This function will execute when the request is fulfilled
    req.onload = function()
    {
        //Get response
        var data = JSON.parse(this.response);

        console.log(data);
        
        //Convert array to Uint8ClampedArray
        data.data = new Uint8ClampedArray(data.data);

        //Create ImageData
        var noisyImage = new ImageData(data.data, data.width, data.height);

        //Display ImageData
        var canvas = document.querySelector('#noisy-encoded-drawing__canvas');
        writeImage(canvas, noisyImage);
    };

    //Send the request
    req.send(JSON.stringify({ "height" : imageData.height, "width" : imageData.width, "encodedImage" : imageData.data, "errorRate" : errorRate }));
}

prepareSlider();
prepareCanvas();
prepareDrawing();