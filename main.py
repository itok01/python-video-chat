from collections import defaultdict
import json
import sys

from flask import Flask, render_template
from flask_sockets import Sockets
from geventwebsocket.websocket import WebSocket

app = Flask(__name__)
sockets = Sockets(app)

client_conn = defaultdict(WebSocket)
room_users = defaultdict(list)
user_to_room = defaultdict(str)


@app.route('/room/<room_id>', methods=['GET'])
def get_room(room_id):
    return render_template('room.html')


@sockets.route('/ws')
def ws_service(ws):
    try:
        while not ws.closed:
            message = ws.receive()
            data = json.loads(message)

            if data.get('type') == 'join':
                user_to_room[data.get('user')] = data.get('room')

                userlist_message_obj = {'type': 'userlist',
                                        'userlist': room_users.get(data.get('room'))}
                userlist_message = json.dumps(userlist_message_obj)
                ws.send(userlist_message)

                client_conn[data.get('user')] = ws
                room_users[data.get('room')].append(data.get('user'))

                join_message_obj = {'type': 'join', 'user': data.get('user')}
                join_message = json.dumps(join_message_obj)
                for user in room_users.get(data.get('room')):
                    if data.get('user') != user:
                        client_conn.get(user).send(join_message)

            elif data.get('type') == 'frame':
                frame_message_obj = {'type': 'frame', 'user': data.get('user'),
                                     'frame': data.get('frame')}
                frame_message = json.dumps(frame_message_obj)
                for user in room_users.get(data.get('room')):
                    if data.get('user') != user:
                        client_conn.get(user).send(frame_message)
    except:
        print(sys.exc_info())

        for user, conn in client_conn.items():
            if conn == ws:
                leave_user = user
                leave_message_obj = {'type': 'leave', 'user': leave_user}
                leave_message = json.dumps(leave_message_obj)
                for user in room_users.get(user_to_room.get(leave_user)):
                    if user != leave_user:
                        client_conn.get(user).send(leave_message)
                del client_conn['leave_user']
                room_users.get(user_to_room['leave_user']).remove(leave_user)
                del user_to_room['leave_user']
                break


if __name__ == '__main__':
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('0.0.0.0', 443), app, handler_class=WebSocketHandler,
                               certfile='localhost.pem', keyfile='localhost-key.pem')
    server.serve_forever()
