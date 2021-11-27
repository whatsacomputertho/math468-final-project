const HOST = document.querySelector('#page-data').dataset.host;
const PORT = document.querySelector('#page-data').dataset.port;

//This is the function to run any time an information bit value is adjusted
function setInputBitValues()
{
    //The function gets all input bit toggles and values
    bitToggles = document.querySelectorAll('.input-bit-toggle__value');
    bitValues = document.querySelectorAll('.input-display__value');

    //Loop through all input bit toggles and values
    for(i = 0; i < bitToggles.length; i++)
    {
        //Reset the input bit value
        bitValues[i].innerHTML = '';

        //If the input bit toggle is checked, let the input bit value be 1
        if(bitToggles[i].checked)
        {
            bitValues[i].appendChild(document.createTextNode('1'));
        }
        //Otherwise, let it be 0
        else
        {
            bitValues[i].appendChild(document.createTextNode('0'));
        }
    }

    //Update the channel bits accordingly
    setChannelBitValues(getInputBits());
}

//This function prepares the input bit toggles by adding an event listener
//The event listener runs the above function on click (i.e. setInputBitValues())
function prepareInputBitToggles()
{
    bitToggles = document.querySelectorAll('.input-bit-toggle__value');
    for(i = 0; i < bitToggles.length; i++)
    {
        bitToggles[i].addEventListener('click', function(){
            setInputBitValues();
        });
    }
}

//This function simply inverts the bit value that it is given (i.e. it's a not function)
function flipChannelBit(bitValue)
{
    //If it receives zero, it sets it equal to 1
    if(bitValue.innerHTML === '0')
    {
        bitValue.innerHTML = '';
        bitValue.appendChild(document.createTextNode('1'));
    }
    //If it receives anything else, it sets it equal to 0
    else
    {
        bitValue.innerHTML = '';
        bitValue.appendChild(document.createTextNode('0'));
    }
}

//This function creates a callback function referencing flipChannelBit with its
//respective bit value
function createBitFlipCallback(bitValue)
{
    //Create the flip channel bit callback
    bitFlipCallback = function()
    {
        //Flip the channel bit
        flipChannelBit(bitValue);

        //Re-decode the channel bits
        decodeChannelBits(getChannelBits());
    }

    //Return the callback
    return bitFlipCallback;
}

//This function prepares the channel bit toggles by equipping them with a change
//listener containing the callback generated in the above function
function prepareChannelBitToggles()
{
    //Get all channel bit values and all channel bit toggles
    bitToggles = document.querySelectorAll('.channel-bit-toggle__value');
    bitValues = document.querySelectorAll('.channel-display__value');

    //Loop through both lists simultaneously (they are guaranteed to be the same length)
    for(i = 0; i < bitToggles.length; i++)
    {
        //Reset the event listener for new bit value by cloning the old toggle and replacing it with a new one
        var newToggle = bitToggles[i].cloneNode(true);
        newToggle.addEventListener('change', createBitFlipCallback(bitValues[i]));
        bitToggles[i].parentNode.replaceChild(newToggle, bitToggles[i]);
    }
}

//This function returns the input bits as a list for API calls
function getInputBits()
{
    //Initialize the input list
    var inputBits = [];

    //Add a try-catch in case there is no integer present in one of the bit displays
    try
    {
        var bitValues = document.querySelectorAll('.input-display__value');
        for(i = 0; i < bitValues.length; i++)
        {
            inputBits.push(parseInt(bitValues[i].innerHTML));
        }
    }
    catch(err)
    {
        console.log(err);
        inputBits = [];
    }

    //Return the bit values as a list
    return inputBits;
}

//This function returns the channel bits as a list for API calls
function getChannelBits()
{
    //Initialize the input list
    var channelBits = [];

    //Add a try-catch in case there is no integer present in one of the bit displays
    try
    {
        var bitValues = document.querySelectorAll('.channel-display__value');
        for(i = 0; i < bitValues.length; i++)
        {
            channelBits.push(parseInt(bitValues[i].innerHTML));
        }
    }
    catch(err)
    {
        console.log(err);
        channelBits = [];
    }

    //Return the bit values as a list
    return channelBits;
}

//This function actually displays the channel bit values
function displayChannelBitValues(codeWord)
{
    //Get all channel bit values and all channel bit toggles
    var bitToggles = document.querySelectorAll('.channel-bit-toggle__value');
    var bitValues = document.querySelectorAll('.channel-display__value');

    //Loop through both lists simultaneously (they are guaranteed to be the same length)
    for(i = 0; i < bitToggles.length; i++)
    {
        //Reset the innerHTML in the bit value
        bitValues[i].innerHTML = '';

        //If the bit toggle is checked be sure to invert the code word's value to start
        if(bitToggles[i].checked)
        {
            bitValues[i].appendChild(document.createTextNode((codeWord[i] + 1) % 2));
        }
        else
        {
            bitValues[i].appendChild(document.createTextNode(codeWord[i]));
        }
    }

    //Reset the callback functions for the new values
    prepareChannelBitToggles();
}

//This function actually displays the decoded bit values
function displayDecodedInformationBits(informationBits)
{
    //Get the information display element
    var informationDisplay = document.querySelector('#decoded__code-word');

    //Clear its current value
    informationDisplay.innerHTML = '';

    //Loop through the returned information bits
    for(i = 0; i < informationBits.length; i++)
    {
        //Append each bit onto the value for display
        informationDisplay.innerHTML += '' + informationBits[i];
    }
}

//This function sends a request to the back-end to encode the user's input according to the extended Golay generator matrix
function setChannelBitValues(informationBits)
{
    var req = new XMLHttpRequest();
    req.open("POST", `http://${HOST}:${PORT}/extended-binary/encode`);
    req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    //This function will execute when the request is fulfilled
    req.onload = function()
    {
        //Get response
        data = JSON.parse(this.response);

        //Display the response
        displayChannelBitValues(data.codeWord);

        //Decode the channel bits
        decodeChannelBits(getChannelBits());
    };

    //Send the request
    req.send(JSON.stringify({ "informationBits" : informationBits }));
}

//This function sends a request to the back-end to decode the message with added noise
function decodeChannelBits(message)
{
    var req = new XMLHttpRequest();
    req.open("POST", `http://${HOST}:${PORT}/extended-binary/decode`);
    req.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    //This function will execute when the request is fulfilled
    req.onload = function()
    {
        //Get response
        data = JSON.parse(this.response);

        //Display the response
        displayDecodedInformationBits(data.informationBits);
    };

    //Send the request
    req.send(JSON.stringify({ "message" : message }));
}

//Initialize the webpage to start
prepareInputBitToggles();
prepareChannelBitToggles();
setInputBitValues();