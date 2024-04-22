// Initialize Video.js
var player = videojs('videoPlayer');
const HOST_NAME = 'movies.eggpoker.com';

player.on('loadedmetadata', function () {
    // Set the initial playback position if the stream is live
    if (player.duration() === Infinity) {
        player.currentTime(0);
    }
});
player.on('seeking', function () {
    if (player.currentTime() > player.buffered().end(0)) {
        player.currentTime(player.buffered().end(0)); // Prevent seeking beyond the buffered content
    }
});
player.on('play', function () {
    if (player.paused() && player.currentTime() < player.buffered().end(0)) {
        player.currentTime(player.buffered().end(0));
    }
});

function fetchActiveStreams() {
    fetch(`https://${HOST_NAME}/stat`, {
        method: 'GET',
        mode: 'cors'
    })
        .then(response => response.text())
        .then(data => {
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(data, "text/xml");
            updateStreamList(xmlDoc);
        })
        .catch(error => console.error('Error fetching the active streams:', error));
}

function updateStreamList(xmlDoc) {
    const streamsList = document.getElementById('streams-list');
    streamsList.innerHTML = ''; // Clear existing entries

    // Loop through each application
    const applications = xmlDoc.getElementsByTagName('rtmp')[0]
        .getElementsByTagName('server')[0]
        .getElementsByTagName('application');
    for (let app of applications) {
        const appName = app.getElementsByTagName('name')[0].textContent;
        if (appName == 'private') continue; // Skip 'private' application

        const live = app.getElementsByTagName('live')[0];
        const streams = live.getElementsByTagName('stream');

        // Add each stream under this application to the list
        for (let stream of streams) {
            const streamName = stream.getElementsByTagName('name')[0].textContent;
            const meta = stream.getElementsByTagName('meta')[0];
            const li = document.createElement('li');

            li.addEventListener('click', function () {
                playStream(streamName,
                    parseInt(meta.getElementsByTagName('width')[0].textContent),
                    parseInt(meta.getElementsByTagName('height')[0].textContent)
                );
            });
            li.textContent = streamName;
            li.className = 'clickable-item'; // Apply the CSS class        

            streamsList.appendChild(li);
        }
    }

    if (streamsList.children.length === 0) {
        const li = document.createElement('li');
        li.textContent = 'No active streams';
        streamsList.appendChild(li);
    }
}

function resizeVideoPlayer(desiredWidth, desiredHeight) {
    // Assuming 'player' refers to your video.js player instance.
    var playerContainer = document.getElementById(player.id()).parentElement;
    var aspectRatio = desiredWidth / desiredHeight;

    if (aspectRatio < 1) {
        var containerWidth = playerContainer.offsetWidth;
        var newHeight = containerWidth / aspectRatio;

        player.width(containerWidth);
        player.height(newHeight);

        playerContainer.style.height = `${newHeight}px`;
    } else {
        var containerHeight = playerContainer.offsetHeight;
        var newWidth = containerHeight * aspectRatio;

        player.width(newWidth);
        player.height(containerHeight);

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
    console.log(`Playing video from URL: ${url} with type ${type}`);

    const videoTitle = document.getElementById('videoTitle')
    videoTitle.textContent = url;
    resizeVideoPlayer(width, height);

    player.src({
        type: type,
        src: url,
    });
    player.play();
}

function getSearchResult(query) {
    $.ajax({
        url: `/search_video?searchInput=${query}`,
        type: "GET",
        success: function (videos) {
            var html = "";
            for (var i = 0; i < videos.length; i++) {
                var video = videos[i];
                html += `<li>
                    <img src="${video.thumbnail}" alt="${video.title} Thumbnail" onclick="playFromURL('${video.url}', '${video.width}', '${video.height}', 'video/youtube')">
                    <span>${video.title}</span>
                </li>`;
            }
            $("#search-results").html(html);
        },
        error: function (xhr, status, error) {
            console.log(error);
        }
    });
}

// set up stream list
window.onresize = function () {
    const playerContainer = document.getElementById(player.id()).parentElement;
    const playerWidth = playerContainer.clientWidth;
    const playerHeight = playerContainer.clientHeight;
    resizeVideoPlayer(playerWidth, playerHeight);
}

resizeVideoPlayer(1080, 720);
setInterval(fetchActiveStreams, 1000);