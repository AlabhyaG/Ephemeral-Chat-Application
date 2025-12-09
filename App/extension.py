from flask_socketio import SocketIO
import redis
socketio = SocketIO(cors_allowed_origins='*')

r = redis.StrictRedis(
    host='redis-18900.c276.us-east-1-2.ec2.cloud.redislabs.com',
    port=18900,
    db=0,
    decode_responses=True
)