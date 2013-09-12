// @copyright: 2013 Single D Software - All Rights Reserved
// @summary: JavaScript logic for the Mix Maestro GUI

"use strict";

var channeladjuster = ''

channeladjuster += '<td>'
channeladjuster += '    <div data-role="controlgroup">'
channeladjuster += '        <a data-role="button">+10</a>'
channeladjuster += '        <a data-role="button">+1</a>'
channeladjuster += '    </div>'
channeladjuster += '    <p></p>'
channeladjuster += '    <div data-role="controlgroup">'
channeladjuster += '        <a data-role="button">-1</a>'
channeladjuster += '        <a data-role="button">-10</a>'
channeladjuster += '    </div>'
channeladjuster += '    <p></p>'
channeladjuster += '</td>'

            

//$(document).bind('pageinit', function(e) {
$(document).ready(function(e) {

    $.get('/auxes', function(auxes) {
        /*var navbarhtml = '<ul>';
        for(var aux in auxes) {
            var name = auxes[aux].name;
            if(name !== undefined) {
                if(navbarhtml == '<ul>') {
                    navbarhtml += '<li><a class="ui-btn-active">' + name + '</a></li>';
                }
                else {
                    navbarhtml += '<li><a>' + name + '</a></li>';
                }
            }
        }
        navbarhtml += '</ul>';
        var headerdiv = $('div[data-role="header"]')
        var navbardiv = $('div', {
            'data-role':'navbar',
            'html':'<ul><li><a id="some">First</a></li></ul>'
        }).appendTo(headerdiv).navbar();*/
        
        for(var c = 0; c < 24; c++) {
            $('tr').append(channeladjuster);
        }
        
        console.log('did it');
        
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
