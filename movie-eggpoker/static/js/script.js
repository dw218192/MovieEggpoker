function playVideo(channel) {
    var videoPlayer = document.getElementById('video');
    videoPlayer.src = `rtmp://localhost:6666/${channel}`;
    videoPlayer.load();
    videoPlayer.play();
}
