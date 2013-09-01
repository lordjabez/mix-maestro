// @copyright: 2013 Single D Software - All Rights Reserved
// @summary: Provides the HTTP server for Mix Maestro.


$(window).load(function(e) {

    function updateI1(data) {
        $("#i1_level").html(data.level);
    }

    //TODO format string in display to 0.0 form

    $("#i1_up").click(function(e) {
        oldlevel = parseFloat($("#i1_level").html());
        newlevel = oldlevel + 1.0;
        leveldata = {"level": newlevel};
        $.ajax({ url:"/mixer/channels/inputs/1", method:"PUT", headers: {"content-type": "application/json"}, data: JSON.stringify(leveldata), success: updateI1});
    });

    $("#i1_down").click(function(e) {
        oldlevel = parseFloat($("#i1_level").html());
        newlevel = oldlevel - 1.0;
        leveldata = {"level": newlevel};
        $.ajax({ url:"/mixer/channels/inputs/1", method:"PUT", headers: {"content-type": "application/json"}, data: JSON.stringify(leveldata), success: updateI1});
    });

});
