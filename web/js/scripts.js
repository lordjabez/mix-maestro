// @copyright: 2013 Single D Software - All Rights Reserved
// @summary: JavaScript logic for the Mix Maestro GUI

"use strict";

// TODO read this from JSON
var chanPerPage = 8
var currPage = 1
var numPages = 6

function updateInputs(inputs) {
    for(var input in inputs) {
        var name = inputs[input].name || "";
        var inputElem = $('#chan-00');
        if(name != "") {
            inputElem.show();
            inputElem.find('ind-name').html(name);
        }
        else {
            chanElem.hide();
            inputElem.find('ind-name').html('&nbsp;');
        }
        var auxes = inputs[input].auxes || {};
        for(var aux in auxes) {
            var level = (auxes[aux].level || "") + " dB" ;
            inputElem.find('
            $('body div:nth-child(' + aux + ') table td:nth-child(' + input + ') p:nth-child(2)').html(level);
        }
    }
    setTimeout(pollInputs, 1000);
}

// TODO use query string to poll right value
function pollInputs() {
    $.get('/auxes/1/inputs', updateInputs);
}

function refreshPageInfo() {
    $('#this-page .ui-btn-text').html(currPage + '/' + numPages);
}

function firstPage() {
    currPage = 1;
    refreshPageInfo();
}

function prevPage() {
    currPage = Math.max(1, currPage - 1);
    refreshPageInfo();
}

function nextPage() {
    currPage = Math.min(currPage + 1, numPages);
    refreshPageInfo();
}

function lastPage() {
    currPage = numPages;
    refreshPageInfo();
}

$(document).bind('pageinit', function() {

    $('#first-page').bind('tap', firstPage);
    $('#prev-page').bind('tap', prevPage);
    $('#next-page').bind('tap', nextPage);
    $('#last-page').bind('tap', lastPage);
    
    refreshPageInfo();
    
    pollInputs();

/*

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
