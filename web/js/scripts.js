// @copyright: 2013 Single D Software - All Rights Reserved
// @summary: JavaScript logic for the Mix Maestro GUI

"use strict";

function updateInputs(inputs) {
    for(var input in inputs) {
        var name = inputs[input].name || "";
        if(name != "") {
            // TODO clean this up by saving some selections
            $('table td:nth-child(' + input + ') p:nth-child(4)').html(name);
            $('table td:nth-child(' + input + ')').show();
        }
        var auxes = inputs[input].auxes || {};
        for(var aux in auxes) {
            var level = (auxes[aux].level || "") + " dB" ;
            //var auxnum = parseInt(aux) - 1;
            //var inputnum = parseInt(input) - 1;
            // TODO fix this selector
            $('body div:nth-child(' + aux + ') table td:nth-child(' + input + ') p:nth-child(2)').html(level);
        }
    }
    setTimeout(pollInputs, 1000);
}

function pollInputs() {
    $.get('/inputs', updateInputs);
}

$(document).ready(function(e) {

    var inputadjuster = ''
    inputadjuster += '<td>';
    inputadjuster += '    <div data-role="controlgroup">';
    inputadjuster += '        <a data-role="button">+10</a>';
    inputadjuster += '        <a data-role="button">+1</a>';
    inputadjuster += '    </div>';
    inputadjuster += '    <p>&nbsp;</p>';
    inputadjuster += '    <div data-role="controlgroup">';
    inputadjuster += '        <a data-role="button">-1</a>';
    inputadjuster += '        <a data-role="button">-10</a>';
    inputadjuster += '    </div>';
    inputadjuster += '    <p>&nbsp;</p>';
    inputadjuster += '</td>';

    for(var c = 1; c <= 48; c++) {
        $('tr').append(inputadjuster);
    }
    $('tr').trigger('create');
    $('td').hide();

    pollInputs();

/*
    function updateI1(data) {
        $("#i1_level").html(data.level);
    }

    //TODO format string in display to 0.0 form

    $("#i1_up").click(function(e) {
        oldlevel = parseFloat($("#i1_level").html());
        newlevel = oldlevel + 1.0;
        leveldata = {"level": newlevel};
        $.ajax({ url:"/mixer/inputs/inputs/1", method:"PUT", headers: {"content-type": "application/json"}, data: JSON.stringify(leveldata), success: updateI1});
    });

    $("#i1_down").click(function(e) {
        oldlevel = parseFloat($("#i1_level").html());
        newlevel = oldlevel - 1.0;
        leveldata = {"level": newlevel};
        $.ajax({ url:"/mixer/inputs/inputs/1", method:"PUT", headers: {"content-type": "application/json"}, data: JSON.stringify(leveldata), success: updateI1});
    });
*/
});
