require('dotenv').config(); 
const express = require('express');

var app = express();
app.set('view engine', 'ejs');

var bodyParser = require('body-parser');
app.use(bodyParser.urlencoded({ extended: true }));
require('dotenv').config();



app.set('port', (process.env.PORT || 3000));


app.get('/', function(req, res){ 
  res.render('index',{user: "Great User",GOOGLE_MAPS_API_KEY:process.env.GOOGLE_MAPS_API_KEY});
});

app.listen(app.get('port'), function() {
  console.log('listening port 3000')
});

