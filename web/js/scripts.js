// @copyright: 2013 Single D Software - All Rights Reserved
// @summary: Provides the HTTP server for Mix Maestro.

var channels = []
for (i = 0; i < 8; i++) {
    channels[i] = "I" + i;
}

$(window).load(function(e) {
 
    for (c in channels) {
            
    }
    
    $("#serialsend").click(function(e) {
        $.ajax({ url:"/serial", method:"PUT", data:$("#serialinput").val() });
    });
   
});
