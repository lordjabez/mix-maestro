// @copyright: 2013 Single D Software - All Rights Reserved
// @summary: JavaScript logic for the Mix Maestro GUI

"use strict";

$(document).bind('pageinit', function() {

    var CHANNEL_POLL_DELAY = 1000;

    var id = location.search.split('=')[1];

    var stripsPerPage = 1;
    var currPage = 1;
    var numPages = 1;

    var channel;

    function updateStrip(snum) {
        var inum = (currPage - 1) * stripsPerPage + snum + 1;
        var name = channel['inputs'][inum].name || '';
        var level = (channel['inputs'][inum].level.toFixed(1) || '') + " dB";
        if(name) {
            $(this).removeClass('ui-disabled');
            $(this).find('.ind-name').html(name);
            $(this).find('.ind-level').html(level);
        }
        else {
            $(this).addClass('ui-disabled');
            $(this).find('.ind-name').html('&nbsp;');
            $(this).find('.ind-level').html('&nbsp;');
        }
    }

    function updatePage() {
        if(channel !== undefined) {
            numPages = Math.ceil(Object.keys(channel['inputs']).length / stripsPerPage);
            var pageHeader = channel.name + ' ' + currPage + '/' + numPages;
            $('#button-this-page .ui-btn-text').html(pageHeader);
            $('.chan-strip').each(updateStrip);
        }
    }

    function updateChannel(chan) {
        channel = chan;
        updatePage();
    }

    function setNextPoll() {
        setTimeout(pollChannel, CHANNEL_POLL_DELAY);
    }

    function pollChannel() {
        var channelUrl = '/auxes/' + id + '/inputs'
        $.ajax({url: channelUrl, success: updateChannel, complete: setNextPoll});
    }

    function firstPage(e) {
        e.stopImmediatePropagation();
        currPage = 1;
        updatePage();
    }

    function prevPage(e) {
        e.stopImmediatePropagation();
        currPage = Math.max(1, currPage - 1);
        updatePage();
    }

    function thisPage(e) {
        e.stopImmediatePropagation();
    }

    function nextPage(e) {
        e.stopImmediatePropagation();
        currPage = Math.min(currPage + 1, numPages);
        updatePage();
    }

    function lastPage(e) {
        e.stopImmediatePropagation();
        currPage = numPages;
        updatePage();
    }

    stripsPerPage = $('.chan-strip').size();

    $('#button-first-page').bind('tap', firstPage);
    $('#button-prev-page').bind('tap', prevPage);
    $('#button-this-page').bind('tap', thisPage);
    $('#button-next-page').bind('tap', nextPage);
    $('#button-last-page').bind('tap', lastPage);
    
    updatePage();
    pollChannel();

/*
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
