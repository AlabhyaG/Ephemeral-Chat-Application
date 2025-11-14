from flask_socketio import SocketIO
import redis
socketio = SocketIO(cors_allowed_origins='*')

r = redis.StrictRedis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)