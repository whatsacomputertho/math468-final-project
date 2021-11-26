const express = require('express');
var app = express();

//Enable js and css to be served with rendered ejs
app.use(express.static(__dirname + '/assets'));

//Set the view engine to ejs
app.set('view engine', 'ejs');

//Home page
app.get('/', (req, res) => {
    res.render('index');
});

//Extended golay code simulator page
app.get('/extended-golay-code-simulator', (req, res) => {
    res.render('extended-golay-code-simulator');
});

//NASA voyager 1 simulator page
app.get('/nasa-voyager-1-simulator', (req, res) => {
    res.render('nasa-voyager-1-simulator');
});

//TODO: Serve the report PDF
app.get('/report', (req, res) => {
    res.render('report');
});

//About page
app.get('/about', (req, res) => {
    res.render('about');
});

app.listen(8080);
console.log('Server is listening on http://localhost:8080');