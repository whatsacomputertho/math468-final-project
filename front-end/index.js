const express = require('express');
const dotenv = require('dotenv').config();
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
    res.render('extended-golay-code-simulator', {
        host: process.env.BACK_END_HOST,
        port: process.env.BACK_END_PORT
    });
});

//NASA voyager 1 simulator page
app.get('/nasa-voyager-1-simulator', (req, res) => {
    res.render('nasa-voyager-1-simulator', {
        host: process.env.BACK_END_HOST,
        port: process.env.BACK_END_PORT
    });
});

//Serve the report PDF
app.get('/report', (req, res) => {
    res.download('./assets/pdf/math468-final-project-report.pdf');
});

//About page
app.get('/about', (req, res) => {
    res.render('about');
});

app.listen(process.env.PORT, process.env.HOST);
console.log(`Server is listening on http://${process.env.HOST}:${process.env.PORT}`);