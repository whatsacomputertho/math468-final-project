const HOST = document.querySelector('#page-data').dataset.host;
const PORT = document.querySelector('#page-data').dataset.port;

var isDrawing = false;
var requestSent = false;
var encodeRequests = [];
var transmitRequests = [];
var decodeRequests = [];
var restoreArray = [];

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
    var boundingRect = canvas.getBoundingClientRect();
    context.beginPath();
    context.moveTo(event.clientX - boundingRect.left, event.clientY - boundingRect.top);
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
        var boundingRect = canvas.getBoundingClientRect();
        context.lineTo(event.clientX - boundingRect.left, event.clientY - boundingRect.top);
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
        if(restoreArray.length > 32)
        {
            restoreArray.splice(0, 1);
        }

        //Encode the most recent image
        encodeImage(restoreArray[restoreArray.length - 1], 0);
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
    restoreArray = [context.getImageData(0, 0, width, height)];

    //Encode the most recent image
    encodeImage(restoreArray[restoreArray.length - 1], 0);
}

function undo()
{
    //If index is 0 or -1 we know that there has been at most 1 line drawn
    if(restoreArray.length == 1)
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
        restoreArray.pop();
        context.putImageData(restoreArray[restoreArray.length - 1], 0, 0);

        //Encode the most recent image
        encodeImage(restoreArray[restoreArray.length - 1], 0);
    }
}

function writeImage(canvas, imageData)
{
    //Get canvas context
    var context = canvas.getContext("2d");

    //Write the image data
    context.putImageData(imageData, 0, 0);
}

function writeImageRow(canvas, imageData, rowIndex)
{
    //Get canvas context
    var context = canvas.getContext("2d");

    //Write the image data
    context.putImageData(imageData, 0, rowIndex);
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
    transmitImage(imageData, errorRateSlider.value, 0);
}

function encodeImage(imageData, rowIndex)
{
    //Set loading element visible on encoding request
    var loader = document.querySelector('#encoded-drawing__loading');
    loader.hidden = false;

    //Instantiate the request
    var req = new XMLHttpRequest();
    req.open("POST", `http://${HOST}:${PORT}/extended-binary/encode-image`);
    req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    //Check for existing requests and cancel them
    for(i = 0; i < encodeRequests.length; i++)
    {
        encodeRequests[i].abort();
    }
    for(i = 0; i < transmitRequests.length; i++)
    {
        transmitRequests[i].abort();
    }
    for(i = 0; i < decodeRequests.length; i++)
    {
        decodeRequests[i].abort();
    }

    //Add this request to the existing request list
    encodeRequests.push(req);

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
        writeImageRow(canvas, encodedImage, rowIndex);

        //Get error rate slider
        var errorRateSlider = document.querySelector('#noisy-encoded-drawing__slider')

        //Set loading element invisible after encoded image is displayed
        var loader = document.querySelector('#encoded-drawing__loading');
        loader.hidden = true;

        if(rowIndex < imageData.height - 1)
        {
            encodeImage(imageData, rowIndex + 1)
        }
        else
        {
            //Transmit the image
            transmitImage(canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height), errorRateSlider.value, 0);
        }
    };

    //Get the ith row of the image
    imageRow = imageData.data.slice((rowIndex * imageData.width * 4), ((rowIndex + 1) * imageData.width * 4))

    //Send the request
    req.send(JSON.stringify({ "height" : 1, "width" : imageData.width, "informationBits" : imageRow }));
}

function transmitImage(imageData, errorRate, rowIndex)
{
    //Set loading element visible on transmission request
    var loader = document.querySelector('#noisy-encoded-drawing__loading');
    loader.hidden = false;

    //Instantiate the request
    var req = new XMLHttpRequest();
    req.open("POST", `http://${HOST}:${PORT}/binary-channel/transmit-image`);
    req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    //Check for existing requests and cancel them
    for(i = 0; i < transmitRequests.length; i++)
    {
        transmitRequests[i].abort();
    }
    for(i = 0; i < decodeRequests.length; i++)
    {
        decodeRequests[i].abort();
    }

    //Add this request to the existing request list
    transmitRequests.push(req);

    //This function will execute when the request is fulfilled
    req.onload = function()
    {
        //Get response
        var data = JSON.parse(this.response);
        
        //Convert array to Uint8ClampedArray
        data.data = new Uint8ClampedArray(data.data);

        //Create ImageData
        var noisyImage = new ImageData(data.data, data.width, data.height);

        //Display ImageData
        var canvas = document.querySelector('#noisy-encoded-drawing__canvas');
        writeImageRow(canvas, noisyImage, rowIndex);

        //Set loading element invisible after noisy encoded image is displayed
        var loader = document.querySelector('#noisy-encoded-drawing__loading');
        loader.hidden = true;

        if(rowIndex < imageData.height - 1)
        {
            //Transmit the next row
            transmitImage(imageData, errorRate, rowIndex + 1);
        }
        else
        {
            //Decode the transmitted image
            decodeImage(canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height), 0);
        }
    };

    //Get the ith row of the image
    imageRow = imageData.data.slice((rowIndex * imageData.width * 4), ((rowIndex + 1) * imageData.width * 4))

    //Send the request
    req.send(JSON.stringify({ "height" : 1, "width" : imageData.width, "encodedImage" : imageRow, "errorRate" : errorRate }));
}

function decodeImage(imageData, rowIndex)
{
    //Set loading element visible on decoding request
    var loader = document.querySelector('#decoded-drawing__loading');
    loader.hidden = false;

    //Instantiate the request
    var req = new XMLHttpRequest();
    req.open("POST", `http://${HOST}:${PORT}/extended-binary/decode-image`);
    req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    //Check for existing requests and cancel them
    for(i = 0; i < decodeRequests.length; i++)
    {
        decodeRequests[i].abort();
    }

    //Add this request to the existing request list
    decodeRequests.push(req);

    //This function will execute when the request is fulfilled
    req.onload = function()
    {
        //Get response
        var data = JSON.parse(this.response);
        
        //Convert array to Uint8ClampedArray
        data.data = new Uint8ClampedArray(data.data);

        //Create ImageData
        var decodedImage = new ImageData(data.data, data.width, data.height);

        //Display ImageData
        var canvas = document.querySelector('#decoded-drawing__canvas');
        writeImageRow(canvas, decodedImage, rowIndex);

        //Set loading element invisible after noisy encoded image is displayed
        var loader = document.querySelector('#decoded-drawing__loading');
        loader.hidden = true;

        //Check to see if image is done loading, if so send a new request
        if(rowIndex != imageData.height - 1)
        {
            decodeImage(imageData, rowIndex + 1);
        }
    };

    //Get the ith row of the image to encode
    var imageRow = imageData.data.slice((rowIndex * imageData.width * 4), ((rowIndex + 1) * imageData.width * 4));

    //Send the request
    req.send(JSON.stringify({ "height" : 1, "width" : imageData.width, "noisyImage" : imageRow }));
}

prepareSlider();
prepareCanvas();
prepareDrawing();