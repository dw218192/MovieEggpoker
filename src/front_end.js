import videojs from 'video.js';
const _ = require('./Youtube.js');


// Initialize Video.js
var player = videojs('videoPlayer');




// TODO: fix this function
function resizeVideoPlayer(desiredWidth, desiredHeight) {
    var playerContainer = document.getElementById(player.id()).parentElement;
    var aspectRatio = desiredWidth / desiredHeight;

    if (aspectRatio > 1) {
        var containerWidth = playerContainer.offsetWidth;
        var newHeight = containerWidth / aspectRatio;

        player.width(containerWidth);
        player.height(newHeight);

        console.log(`Setting player width to ${containerWidth}px and height to ${newHeight}px`);

        playerContainer.style.height = `${newHeight}px`;
    } else {
        var containerHeight = playerContainer.offsetHeight;
        var newWidth = containerHeight * aspectRatio;

        player.width(newWidth);
        player.height(containerHeight);

        console.log(`Setting player width to ${newWidth}px and height to ${containerHeight}px`);

        playerContainer.style.width = `${newWidth}px`;
    }
}

function playStream(streamName, width, height, type = 'application/x-mpegURL') {
    const streamURL = `https://${HOST_NAME}/hls/${streamName}.m3u8`;
    console.log(`Playing stream: ${streamURL}`);

    const videoTitle = document.getElementById('videoTitle')
    videoTitle.textContent = streamName;
    resizeVideoPlayer(width, height);

    player.src({
        type: type,
        src: streamURL,
    });
    player.play();
}

// playing from Youtube, bilibili, or other video sites
function playFromURL(url, width, height, type = 'application/x-mpegURL') {
    console.log(`Playing video from URL: ${url} with type ${type}, width ${width}, and height ${height}`);

    const videoTitle = document.getElementById('videoTitle')
    videoTitle.textContent = url;
    resizeVideoPlayer(width, height);

    player.src({
        type: type,
        src: url,
    });
    player.play();
}

function updateStreamList() {
    $.ajax({
        url: `fetch_streams`,
        type: "GET",
        success: function (data) {
            $("#stream-list").html(data.html);
        },
        error: function (xhr, status, error) {
            console.log(error);
        }
    });
}

function fillSearchResults(data) {
    $("#search-results").html(data.html);    
}

// set up stream list
window.onresize = function () {
    const playerContainer = document.getElementById(player.id()).parentElement;
    const playerWidth = playerContainer.clientWidth;
    const playerHeight = playerContainer.clientHeight;
    resizeVideoPlayer(playerWidth, playerHeight);
}

resizeVideoPlayer(1080, 720);
setInterval(updateStreamList, 1000);

const searchForm = document.getElementById('searchInputForm');
searchForm.addEventListener('submit', function (event) {
    event.preventDefault();
    const query = document.getElementById('searchInput').value;
    $.ajax({
        url: `/search_video?searchInput=${query}`,
        type: "GET",
        success: fillSearchResults,
        error: function (xhr, status, error) {
            console.log(error);
        }
    });
});

document.getElementById('nextPageButton').addEventListener('click', function () {
    $.ajax({
        url: `/next_page`,
        type: "GET",
        success: fillSearchResults,
        error: function (xhr, status, error) {
            console.log(error);
        }
    });
});
document.getElementById('prevPageButton').addEventListener('click', function () {
    $.ajax({
        url: `/prev_page`,
        type: "GET",
        success: fillSearchResults,
        error: function (xhr, status, error) {
            console.log(error);
        }
    });
});

// make sure this function is preserved by Webpack
window.playFromURL = playFromURL;

window.onbeforeunload = function () {
    player.dispose();
    $.ajax({
        url: `/user_disconnected`,
        type: "GET",
        success: function (data) {
            console.log(data);
        },
        error: function (xhr, status, error) {
            console.log(error);
        }
    });
}