if (Hls.isSupported()) {
  const videoElement = document.getElementById('videoElement');
  const hls = new Hls();

  hls.loadSource('http://pendule.iai-heig-vd.in:8083/stream/b969c61f-1d22-4ae6-a5f6-be5d283d9f21/channel/0/hls/live/index.m3u8');
  hls.attachMedia(videoElement);
  hls.on(Hls.Events.MANIFEST_PARSED, function() {
      videoElement.play();
  });
}

