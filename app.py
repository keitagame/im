from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app, cors_allowed_origins='*')

# メモリ上に保持する掲示板データ
messages = {"general": []}

@app.route('/')
def index():
    thread = request.args.get('thread', 'general')
    return render_template('index.html', thread=thread, messages=messages.get(thread, []))

@socketio.on('join')
def handle_join(data):
    thread = data.get('thread', 'general')
    join_room(thread)
    emit('joined', {'thread': thread})

@socketio.on('post')
def handle_post(data):
    thread = data.get('thread', 'general')
    author = (data.get('author') or 'anonymous').strip()[:32]
    body = (data.get('body') or '').strip()
    if not body:
        emit('error', {'message': '本文は必須です'})
        return

    msg = {
        'author': author,
        'body': body,
        'created_at': datetime.utcnow().isoformat()
    }
    messages.setdefault(thread, []).append(msg)
    emit('posted', msg, room=thread)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
