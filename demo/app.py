# -*- coding: utf-8 -*-
"""
---------------------------------------------------------
    File Name :         app                             
    Description :       flask echo server
    Author :            Karl                             
    Date :              2022-07-23                          
---------------------------------------------------------
    Change Activity :   2022-07-23
    
--------------------------------------------------------- 
"""

from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')  # 可以跨域了

def ack():
    print('message was received!')

@socketio.on('connection')
def handle_connection():
    print('build connection')


@socketio.on('require_stock')
def handle_require_data(data):
    print('received message: ' + data)
    # there is handle InPut to return
    # 并发都无所谓
    # socketio.emit('response_data', handle(data)) data: str
    socketio.emit('response_stock', data, callback=ack)

if __name__ == "__main__":
    socketio.run(app, host='localhost', port=4321)
