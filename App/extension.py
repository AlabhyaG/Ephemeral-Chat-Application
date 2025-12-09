from flask_socketio import SocketIO
import redis
socketio = SocketIO(cors_allowed_origins='*')
import os
from dotenv import load_dotenv
load_dotenv()

r = redis.StrictRedis(
    host=os.getenv('REDIS_HOST'),
    port=int(os.getenv('REDIS_PORT')),
    db=0,
    decode_responses=True,
    username=os.getenv('REDIS_USERNAME'),
    password=os.getenv('REDIS_PASSWORD')
)
