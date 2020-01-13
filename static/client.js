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
    remoteVideos.appendChild(remoteVideo);
}

let ws = new WebSocket('wss://' + location.host + '/ws')

ws.onmessage = function (e) {
    rcvMessage = JSON.parse(e.data);

    if (rcvMessage.type == 'userlist') {
        console.log(rcvMessage.userlist);
        for (let user of rcvMessage.userlist) {
            console.log(user);
            addRemoteVideo(user);
        }
    } else if (rcvMessage.type == 'join') {
        addRemoteVideo(rcvMessage.user);
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
    let video = document.getElementById('local-video');

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
    console.log(video.clientWidth);
    console.log(video.clientHeight);
    videoFrame.width = video.clientWidth;
    videoFrame.height = video.clientHeight;
    let ctx = videoFrame.getContext('2d');

    let frameMessage = new Message('frame');

    video.addEventListener("timeupdate", () => {
        ctx.drawImage(video, 0, 0, video.clientWidth, video.clientHeight);
        frameMessage.frame = videoFrame.toDataURL("image/webp");
        ws.send(JSON.stringify(frameMessage));
    });
}

document.getElementById('join-button').addEventListener('click', join);

