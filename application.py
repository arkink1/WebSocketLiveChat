import os
from datetime import datetime

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

messages = {'General':[]}
channels = ['General']
users = []

@app.route("/")
def index():
    return render_template("index.html", channels=channels)

@socketio.on('madeUsername')
def madeUsername(data):
    users.append(data['username'])

@socketio.on('startWebsite')
def startWebsite():
    emit("showWebsite")

@socketio.on('getChannel')
def getChannel(data):
    wire = messages[data['channel']]
    emit("formatChannel", {'channelMsgs':wire, 'channels':channels, 'channel':data['channel'], 'singlemsg':0})

@socketio.on('sendMessage')
def sendMessage(data):
    info = []
    channel = data['channel']
    sender = data['sender']
    message = data['message']
    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    info.append(sender)
    info.append(message)
    info.append(now)
    messages[channel].append(info)
    if len(messages[channel]) > 100:
        messages[channel].pop(0)
        emit('formatChannel', {'channelMsgs':messages[channel], 'channels':channels, 'channel':channel, 'singlemsg':0}, broadcast = True)
    else:
        emit('formatChannel', {'channelMsgs':[info], 'channels':channels, 'channel':channel, 'singlemsg':1}, broadcast = True)

@socketio.on('newChannel')
def newChannel(data):
    chan = data['channel']
    channels.append(chan)
    messages[chan] = []
    emit('moreChannel', {'channel':chan, 'channelMsgs':messages[chan], 'username':data['username'], 'singlemsg':0}, broadcast = True)

@socketio.on('delChat')
def delChat(data):
    count = -1
    for z in messages[data['channel']]:
        count+=1
        if z[2] == data['msgtime']:
            messages[data['channel']].pop(count)
            emit('didit', {'channel':data['channel']}, broadcast=True)
