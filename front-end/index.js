const express = require('express');
var app = express();

//Enable js and css to be served with rendered ejs
app.use(express.static(__dirname + '/assets'));

//Set the view engine to ejs
app.set('view engine', 'ejs');

//Index page
app.get('/', function(req, res) {
    res.render('index');
});

app.listen(3000);
console.log('Server is listening on port 3000');