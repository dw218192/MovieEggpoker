// Initialize Video.js
var player = videojs('videoPlayer');
var curAspectRatio = 9/16;
const HOST_NAME = 'movies.eggpoker.com';

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
        const live = app.getElementsByTagName('live')[0];
        const streams = live.getElementsByTagName('stream');

        // Add each stream under this application to the list
        for (let stream of streams) {
            const streamName = stream.getElementsByTagName('name')[0].textContent;
            const meta = stream.getElementsByTagName('meta')[0];
            const li = document.createElement('li');

            li.addEventListener('click', function() {
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

function updateSearchResults(keyword) {
}

function resizeVideoPlayer(){
    var width = document.getElementById(player.id()).parentElement.offsetWidth;
    player.width(width);
    player.height(width * curAspectRatio);
}

function playStream(streamName, width, height, type = 'application/x-mpegURL') {    
    const streamURL = `https://${HOST_NAME}/hls/${streamName}.m3u8`;
    console.log(`Playing stream: ${streamURL}`);

    const videoTitle = document.getElementById('videoTitle')
    videoTitle.textContent = streamName;
    curAspectRatio = height / width;
    resizeVideoPlayer();

    player.src({
        type: type,
        src: streamURL,
    });
    player.play();
}

// playing from Youtube, bilibili, or other video sites
function playFromURL(url, type = 'application/x-mpegURL') {
    console.log(`Playing from URL: ${url}`);
    player.src({
        type: type,
        src: url,
    });
    player.play();
}

// set up search bar
const searchForm = document.getElementById('searchButton');
searchForm.addEventListener('click', function() {
    const keyword = document.getElementById('searchInput').value;
    updateSearchResults(keyword);
});

// set up stream list
window.onresize = resizeVideoPlayer;
resizeVideoPlayer();
setInterval(fetchActiveStreams, 1000);