function joinRoom() {
    let roomForm = document.getElementById('room-form');
    let roomName = document.getElementById('room-name');

    roomForm.method = 'get';
    roomForm.action = 'room/' + roomName.value;
}

let roomForm = document.getElementById('room-form');
roomForm.onsubmit = joinRoom;
