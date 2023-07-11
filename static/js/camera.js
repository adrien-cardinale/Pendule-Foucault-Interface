

const videoStream = document.getElementById('video-stream');

//SET THE RTSP STREAM ADDRESS HERE
var address = "rtsp://root:pendule2023@pendule.einet.ad.eivd.ch:554/axis-media/media.amp";

var output = '<object width="640" height="480" id="qt" classid="clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B" codebase="http://www.apple.com/qtactivex/qtplugin.cab">';
    output += '<param name="src" value="'+address+'">';
    output += '<param name="autoplay" value="true">';
    output += '<param name="controller" value="false">';
    output += '<embed id="plejer" name="plejer" src="/poster.mov" bgcolor="000000" width="640" height="480" scale="ASPECT" qtsrc="'+address+'"  kioskmode="true" showlogo=false" autoplay="true" controller="false" pluginspage="http://www.apple.com/quicktime/download/">';
    output += '</embed></object>';

    //SET THE DIV'S ID HERE
    document.getElementById("the_div_that_will_hold_the_player_object").innerHTML = output;

var button = document.getElementsByClassName("nav-link");
for (var i = 0; i < button.length; i++) {
  button[i].addEventListener('click', function () {
    console.log("click");
    videoStream.src = "";
  });
}

