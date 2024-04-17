// Initialize Video.js
var player = videojs('videoPlayer');
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
            // const fullName = `${appName}/${streamName}`;

            const li = document.createElement('li');

            li.textContent = streamName;
            li.addEventListener('click', function() {
                playStream(streamName);
            });
            li.style.cursor = 'pointer';
            li.style.color = 'blue';

            streamsList.appendChild(li);
        }
    }

    if (streamsList.children.length === 0) {
        const li = document.createElement('li');
        li.textContent = 'No active streams';
        streamsList.appendChild(li);
    }
}

function playStream(streamName, type = 'application/x-mpegURL') {    
    const streamURL = `https://${HOST_NAME}/hls/${streamName}.m3u8`;
    console.log(`Playing stream: ${streamURL}`);

    player.src({
        type: type,
        src: streamURL,
    });
    player.play();
}

setInterval(fetchActiveStreams, 1000);