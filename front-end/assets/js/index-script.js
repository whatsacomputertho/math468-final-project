function setInputBitValues()
{
    bitToggles = document.querySelectorAll('.input-bit-toggle__value');
    bitValues = document.querySelectorAll('.input-display__value');
    for(i = 0; i < bitToggles.length; i++)
    {
        bitValues[i].innerHTML = '';
        if(bitToggles[i].checked)
        {
            bitValues[i].appendChild(document.createTextNode('1'));
        }
        else
        {
            bitValues[i].appendChild(document.createTextNode('0'));
        }
    }
    setChannelBitValues();
}

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

function setChannelBitValues()
{
    //TODO: Talk to back-end encoder
}

function flipChannelBit(bitValue)
{
    if(bitValue.innerHTML === '0')
    {
        bitValue.innerHTML = '';
        bitValue.appendChild(document.createTextNode('1'));
    }
    else
    {
        bitValue.innerHTML = '';
        bitValue.appendChild(document.createTextNode('0'));
    }
}

function createBitFlipCallback(bitValue)
{
    bitFlipCallback = function()
    {
        flipChannelBit(bitValue);
    }
    return bitFlipCallback;
}

function prepareChannelBitToggles()
{
    bitToggles = document.querySelectorAll('.channel-bit-toggle__value');
    bitValues = document.querySelectorAll('.channel-display__value');
    for(i = 0; i < bitToggles.length; i++)
    {
        bitToggles[i].addEventListener('change', createBitFlipCallback(bitValues[i]));
    }
}

prepareInputBitToggles();
prepareChannelBitToggles();
setInputBitValues();