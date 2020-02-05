const user = crypto.getRandomValues(new Uint32Array(1))[0];
const room = location.pathname.split('/')[2];

class Message {
    constructor(type) {
        this.type = type;
        this.user = user;
        this.room = room;
        this.frame = '';
    }
}

const remoteVideos = document.getElementById('remote-videos');

function addRemoteVideo(user) {
    let remoteVideo = document.createElement('img');
    remoteVideo.id = user + '-video';
    remoteVideo.classList.add('aesthetic-effect-crt');
    remoteVideos.appendChild(remoteVideo);
}

function removeRemoteVideo(user) {
    let remoteVideo = document.getElementById(rcvMessage.user + '-video');
    remoteVideo.remove();
}

let ws = new WebSocket('wss://' + location.host + '/ws')

ws.onmessage = function (e) {
    rcvMessage = JSON.parse(e.data);

    if (rcvMessage.type == 'userlist') {
        for (let user of rcvMessage.userlist) {
            addRemoteVideo(user);
        }
    } else if (rcvMessage.type == 'join') {
        addRemoteVideo(rcvMessage.user);
    } else if (rcvMessage.type == 'leave') {
        removeRemoteVideo(rcvMessage.user);
    } else if (rcvMessage.type == 'frame') {
        let remoteVideo = document.getElementById(rcvMessage.user + '-video');
        remoteVideo.src = rcvMessage.frame;
    }
}

const constraints = {
    audio: true,
    video: true
}

function join() {
    let video = document.createElement('video');

    ws.send(JSON.stringify(new Message('join')));

    navigator.mediaDevices.getUserMedia(constraints)
        .then(function (mediaStream) {
            video.srcObject = mediaStream;
            video.onloadedmetadata = function (e) {
                video.play();
            };
        })
        .catch(function (err) {
            console.log(err.name + ": " + err.message);
        });

    let videoFrame = document.createElement('canvas');
    let ctx = videoFrame.getContext('2d');

    remoteVideos.appendChild(videoFrame);

    let frameMessage = new Message('frame');


    video.addEventListener("timeupdate", () => {
        if (ws.readyState == ws.CLOSED || ws.readyState == ws.CLOSING) {
            location.href = location.origin + "/error";
        }

        ctx.drawImage(video, 0, 0, videoFrame.width, videoFrame.height);
        frameMessage.frame = videoFrame.toDataURL("image/webp");
        ws.send(JSON.stringify(frameMessage));
    });
}

ws.onopen = join;
