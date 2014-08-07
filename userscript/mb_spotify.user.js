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

function injected() 
{
    var spotify_html_begin = '<iframe src="https://embed.spotify.com/?uri=';
    var spotify_html_end = '" width="218" height="80" frameborder="0" allowtransparency="true"></iframe>';

    mbid = window.location.pathname.substr(15);
    $.ajax({
             url : "http://mbspotify.musicbrainz.org/mapping-jsonp/" + mbid,
             data : JSON.stringify({"mbids": [ mbid ]}),
             dataType : "jsonp",
             jsonpCallback: 'jsonCallback',
             contentType: "application/json; charset=utf-8",
             success: function(json)
             {
                 console.log(spotify_html_begin + json[mbid] + spotify_html_begin);
                 $(".cover-art").append(spotify_html_begin + json[mbid] + spotify_html_end);
             },
             error: function(xmlhttp, textStatus, error)
             {
             }
    });
}
var script = document.createElement('script');
script.appendChild(document.createTextNode('('+ injected +')();'));
document.body.appendChild(script);
