// @copyright: 2013 Single D Software - All Rights Reserved
// @summary: JavaScript logic for the Mix Maestro GUI

"use strict";

$(document).ready(function(e) {

    var channeladjuster = ''
    channeladjuster += '<td>';
    channeladjuster += '    <div data-role="controlgroup">';
    channeladjuster += '        <a data-role="button">+10</a>';
    channeladjuster += '        <a data-role="button">+1</a>';
    channeladjuster += '    </div>';
    channeladjuster += '    <p>&nbsp;</p>';
    channeladjuster += '    <div data-role="controlgroup">';
    channeladjuster += '        <a data-role="button">-1</a>';
    channeladjuster += '        <a data-role="button">-10</a>';
    channeladjuster += '    </div>';
    channeladjuster += '    <p>&nbsp;</p>';
    channeladjuster += '</td>';

    for(var c = 1; c <= 48; c++) {
        $('tr').append(channeladjuster);
    }
    $('tr').trigger('create');
    $('td').hide();
    
    $.get('/channels', function(channels) {
        console.log(channels);
        for(var channel in channels) {
            var name = channels[channel].name || "";
            if(name != "") {
                // TODO clean this up by saving some selections
                $('table td:nth-child(' + channel + ') p:nth-child(4)').html(name);
                $('table td:nth-child(' + channel + ')').show();
            }
            var auxes = channels[channel].auxes || {};
            for(var aux in auxes) {
                var level = (auxes[aux].level || "") + " dB" ;
                $('body div:nth-child(' + aux + ') table td:nth-child(' + channel + ') p:nth-child(2)').html(level);
            }
        }
        
    });

/*
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
*/
});
