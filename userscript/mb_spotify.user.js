// ==UserScript==
// @name        MusicBrainz Spotify Integration
// @description
// @version     1
// @author      -
// @namespace   http://critiquebrainz.org
//
// @include     *://musicbrainz.org/release-group/*
// @include     *://beta.musicbrainz.org/release-group/*
//
// ==/UserScript==


function injected() {

    var spotify_html_begin = '<iframe src="https://embed.spotify.com/?uri=';
    var spotify_html_end = '" width="218" height="80" style="margin-top: 10px" frameborder="0" allowtransparency="true"></iframe>';

    var no_match_html_begin = '<div width="218" height="80" style="margin-top:5px; padding:3px; background-color:#ccc">This release-group has not been matched to Spotify. Please <a href="http://critiquebrainz.org/matching/spotify/';
    var no_match_html_end = '">match this release group</a>.</div>';

    var error_html = '<div width="218" height="80" style="margin-top:5px; padding:3px; background-color:#ccc">An error has occurred looking up the release-group match.</div>';

    var mbid = window.location.pathname.split("/")[2];
    $.ajax({
        url: "http://mbspotify.musicbrainz.org/mapping-jsonp/" + mbid,
        data: JSON.stringify({"mbids": [mbid]}),
        dataType: "jsonp",
        jsonpCallback: "jsonCallback",
        contentType: "application/json; charset=utf-8",
        success: function (json) {
            if (json[mbid]) {
                $(".cover-art").append(spotify_html_begin + json[mbid] + spotify_html_end);
            } else {
                $(".cover-art").append(no_match_html_begin + mbid + no_match_html_end);
            }
        },
        error: function () {
            $(".cover-art").append(error_html);
        }
    });

}

var script = document.createElement("script");
script.appendChild(document.createTextNode("(" + injected + ")();"));
document.body.appendChild(script);
