from collections import defaultdict
import json
import sys

from flask import Flask, render_template
from flask_sockets import Sockets
from geventwebsocket.websocket import WebSocket

app = Flask(__name__)
sockets = Sockets(app)

# ユーザーのコネクションを管理するディクト
client_conn = defaultdict(WebSocket)
# ルームごとにユーザーリストを管理するディクト
room_users = defaultdict(list)
# ユーザーからルームを参照するディクト
user_to_room = defaultdict(str)

# ホーム
@app.route('/', methods=['GET'])
def get_index():
    return render_template('index.html')

# ルーム
@app.route('/room/<room_id>', methods=['GET'])
def get_room(room_id):
    return render_template('room.html')

# ホーム
@app.route('/error', methods=['GET'])
def get_error():
    return render_template('error.html')

# ビデオチャット用のWebSocket
@sockets.route('/ws')
def ws_service(ws):
    try:
        while not ws.closed:
            message = ws.receive()
            data = json.loads(message)

            # ユーザーが参加したとき
            if data.get('type') == 'join':
                print(str(data.get('user')) + ': joined.')
                for c in client_conn:
                    print(c)

                # 参加したユーザーにルームにいるユーザーを通知
                userlist_message_obj = {'type': 'userlist',
                                        'userlist': room_users.get(data.get('room'))}
                userlist_message = json.dumps(userlist_message_obj)
                ws.send(userlist_message)

                # ユーザーが入っているルームを記録
                user_to_room[data.get('user')] = data.get('room')

                # クライアントリストにユーザーを追加
                client_conn[data.get('user')] = ws

                # ルームにユーザーを追加
                room_users[data.get('room')].append(data.get('user'))

                # ルームにユーザーの参加をブロードキャスト
                join_message_obj = {'type': 'join', 'user': data.get('user')}
                join_message = json.dumps(join_message_obj)
                broadcastRoom(data.get('user'), data.get(
                    'room'), join_message)

            # ビデオフレームの受信
            elif data.get('type') == 'frame':
                # ルームにビデオフレームをブロードキャスト
                frame_message_obj = {'type': 'frame', 'user': data.get('user'),
                                     'frame': data.get('frame')}
                print(type(data.get('frame')))
                frame_message = json.dumps(frame_message_obj)
                broadcastRoom(data.get('user'), data.get(
                    'room'), frame_message)

    except:
        print(sys.exc_info())

        # closeConn(ws)


# ユーザーからルームにブロードキャスト
def broadcastRoom(send_user, room, message):
    for user in room_users.get(room):
        if send_user != user:
            # コネクションが切断されてたら管理ディクトから除外
            if client_conn.get(user).closed:
                print(str(user) + ' is closed.')
                closeConn(client_conn.get(user))
            # メッセージを送信
            else:
                client_conn.get(user).send(message)


# コネクションを切断
def closeConn(close_conn):
    for user, conn in client_conn.items():
        if conn == close_conn:
            leave_user = user
            print(str(leave_user) + ': left.')
            leave_message_obj = {'type': 'leave', 'user': leave_user}
            leave_message = json.dumps(leave_message_obj)
            for user in room_users.get(user_to_room.get(leave_user)):
                if user != leave_user:
                    client_conn.get(user).send(leave_message)
            del client_conn['leave_user']
            room_users.get(user_to_room['leave_user']).remove(leave_user)
            del user_to_room['leave_user']
            for c in client_conn:
                print(c)


if __name__ == '__main__':
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('0.0.0.0', 443), app, handler_class=WebSocketHandler,
                               certfile='localhost.pem', keyfile='localhost-key.pem')
    server.serve_forever()
