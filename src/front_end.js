import videojs from 'video.js';
const _ = require('./Youtube.js');

// Initialize Video.js
var player = videojs('videoPlayer');
player.loop(false);

class VideoJsUtils {
    static toggleLoop() {
        player.loop(!player.loop());
    }
    static playStream(url, title, width, height, type = 'application/x-mpegURL') {
        console.log(`Playing stream: ${url}`);
    
        const videoTitle = document.getElementById('videoTitle')
        videoTitle.textContent = title;
        // resizeVideoPlayer(width, height);
    
        player.src({
            type: type,
            src: url,
        });
        player.play();
    }
    static playFromURL(url, title, width, height, type = 'application/x-mpegURL') {
        console.log(`Playing video from URL: ${url} with type ${type}, width ${width}, and height ${height}`);
    
        const videoTitle = document.getElementById('videoTitle')
        videoTitle.textContent = title;
        // resizeVideoPlayer(width, height);
    
        player.src({
            type: type,
            src: url,
        });
        player.play();
    }
}

// playing from Youtube, bilibili, or other video sites
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

setInterval(updateStreamList, 2000);

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

// make sure these are preserved by Webpack
window.playStream = VideoJsUtils.playStream;
window.playFromURL = VideoJsUtils.playFromURL;
window.toggleLoop = VideoJsUtils.toggleLoop;

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