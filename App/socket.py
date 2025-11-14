from flask_socketio import emit, join_room, leave_room
from flask import request
from .extension import socketio, r
from datetime import datetime

# Store phone to socket ID mapping
user_sockets = {}

def emit_to_user(phone, event, data):
    """Emit an event to a specific user by their phone number"""
    if phone in user_sockets:
        socketio.emit(event, data, room=user_sockets[phone])
        return True
    return False


@socketio.on('connect')
def handle_connect():
    print(f"[SocketIO] Client connected: {request.sid}")
    emit('connection_status', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[SocketIO] Client disconnected: {request.sid}")
    # Remove user from mapping
    phone_to_remove = None
    for phone, sid in user_sockets.items():
        if sid == request.sid:
            phone_to_remove = phone
            break
    if phone_to_remove:
        del user_sockets[phone_to_remove]

@socketio.on('register_user_socket')
def handle_register_user_socket(data):
    """Register user phone number with their socket ID"""
    phone = data.get('phone')
    if phone:
        user_sockets[phone] = request.sid
        print(f"[SocketIO] Registered user {phone} with socket {request.sid}")
        emit('user_registered', {'status': 'registered'})

@socketio.on('join_room')
def handle_join(data):
    room = data.get('room')
    user = data.get('user')
    if not room or not user:
        return emit('error', {'message': 'Missing room or user'})
    join_room(room)
    emit('user_joined', {'user': user}, room=room)

@socketio.on('send_message')
def handle_message(data):
    room = data.get('room')
    sender = data.get('sender')
    message = data.get('message')
    if not all([room, sender, message]):
        return emit('error', {'message': 'Missing fields'})

    msg_data = {
        'sender': sender,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }

    # Save temporarily (optional)
    r.rpush(f"chat:{room}", str(msg_data))
    r.expire(f"chat:{room}", 86400)

    emit('receive_message', msg_data, room=room)
