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
import json

import sys

sys.path.append('./Chatbot/examples/')

import Example

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins='*')  # 可以跨域了

def ack():
    print('message was received!')

@socketio.on('connection')
def handle_connection():
    print('connection')
    socketio.emit("connected")

@socketio.on('connect')
def handel_connection():
    print('connect')

@socketio.on('get_msg')
def handle_data_data(data):
    print("received message: "+ data)
    msg = Example.chatrobot_handle(data)
    # msg = chat(data)
    socketio.emit('post_msg', msg, callback=ack)

@socketio.on('require_stock')
def handle_require_data(data):
    print('received message: ' + data)

    # there is handle InPut to return
    # 并发都无所谓
    # socketio.emit('response_data', handle(data)) data: str
    with open(data+".JSON", "r") as fp:
        data_return = json.load(fp)
        fp.close()
    data_response = json.dumps(data_return)
    socketio.emit('response_stock', data_response, callback= ack)
#     data_return = {
#   "trick": "AAPL",
#   "seqnum": 2,
#   "positive" : 10,
#   "negative" : 5,
#   "neutral": 20,
#   "total": 35,
#   "news": [
#     {"title": "1",
#     "context": "11",
#     "link": "https://111.com",
#     "type": "success"},
#     {"title": "2",
#       "context": "22",
#       "link": "https://222.com",
#       "type": "info"},
#     {"title": "3",
#       "context": "33",
#       "link": "https://333.com",
#       "type": "danger"},
#   ]
# }
#     with open("wordcloud.txt", "r") as fp:
#         data_return["wordcloud"] = fp.read()
#     with open("linear_model.txt", "r") as fp:
#         data_return["linear_model"] = fp.read()
#     with open("svm_model.txt", "r") as fp:
#         data_return['svm_model'] = fp.read()
#     with open("decisiontree_model.txt", "r") as fp:
#         data_return["decisiontree_model"] = fp.read()


if __name__ == "__main__":
    socketio.run(app, host='localhost', port=4321)
