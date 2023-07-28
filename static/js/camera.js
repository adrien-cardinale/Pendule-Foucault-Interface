if (Hls.isSupported()) {
  const videoElement = document.getElementById('videoElement');
  const hls = new Hls();

  hls.loadSource('http://pendule.iai-heig-vd.in:8083/stream/0ca1a15b-077f-4141-8730-acb91cc1f71d/channel/0/hls/live/index.m3u8');
  hls.attachMedia(videoElement);
  hls.on(Hls.Events.MANIFEST_PARSED, function() {
      videoElement.play();
  });
}

