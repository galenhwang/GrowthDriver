// API URL for searching across sectors: 
// https://api.intrinio.com/securities/search?conditions=sector~eq~BasicMaterials~basicmat,sector~eq~Technology~tech&logic=basicmat%20OR%20tech

// API URI: https://api.intrinio.com
// GET: /securities/search?conditions=sector~eq~{{user_input}}&order_column=marketcap&order_direction=desc&primary_only=true
// FULL URL: https://api.intrinio.com/securities/search?conditions=marketcap~gt~10.50&order_column=marketcap&order_direction=desc&primary_only=true

var https = require("https");

var username = "4872b493f830deda8e495aa572be0987";
var password = "6a442c8c745341f2ba6f38e799d893f5";
var auth = "Basic " + new Buffer(username + ':' + password).toString('base64');

var request = https.request({
    method: "GET",
    host: "api.intrinio.com",
    path: "/securities/search?conditions=marketcap~gt~10.50&order_column=marketcap&order_direction=desc&primary_only=true",
    headers: {
        "Authorization": auth
    }
}, function(response) {
    var json = "";
    response.on('data', function (chunk) {
        json += chunk;
    });
    response.on('end', function() {
        var company = JSON.parse(json);
        console.log(company);
    });
});

request.end();
