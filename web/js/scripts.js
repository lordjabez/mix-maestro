// @copyright: 2013 Single D Software - All Rights Reserved
// @summary: JavaScript logic for the Mix Maestro GUI

"use strict";

var JSON_HEADER = {'content-type': 'application/json'}

var CHANNEL_POLL_DELAY = 1000;

var id = location.search.split('=')[1];

var stripsPerPage = 1;
var currPage = 1;
var numPages = 1;

var channel;

function updateStrip(snum) {
    var inum = (currPage - 1) * stripsPerPage + snum + 1;
    var name = channel['inputs'][inum].name || '';
    var level = channel['inputs'][inum].level;
    if(level !== undefined) {
        level = level.toFixed(1) + " dB";
    }
    else {
        level = '&nbsp;';
    }
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
        $('.channel-strip').each(updateStrip);
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

function adjustChannel() {
    var stripElem = $(this).parents('.channel-strip');
    var snum = stripElem.index();
    var inum = (currPage - 1) * stripsPerPage + snum + 1;
    var delta = parseFloat($(this).find('.ui-btn-text').html());
    var level = parseFloat(stripElem.find('.ind-level').html());
    var url = '/auxes/' + id + '/inputs/' + inum;
    var data = JSON.stringify({'level': level + delta});
    $.ajax({ url: url, method: 'PUT', headers: JSON_HEADER, data: data});
}

$(document).bind('pageinit', function() {

    stripsPerPage = $('.channel-strip').size();

    $('#button-first-page').bind('tap', firstPage);
    $('#button-prev-page').bind('tap', prevPage);
    $('#button-this-page').bind('tap', thisPage);
    $('#button-next-page').bind('tap', nextPage);
    $('#button-last-page').bind('tap', lastPage);
    
    $('.channel-strip a').bind('tap', adjustChannel);
    
    updatePage();
    pollChannel();

});

