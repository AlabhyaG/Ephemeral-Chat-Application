from flask import Flask,current_app
import os
from .extension import socketio
from .routes import routes_bp

def createApp():
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_dir = os.path.join(base_dir, 'Templates')
        app = Flask(__name__, template_folder=template_dir)
        app.register_blueprint(blueprint=routes_bp)
        socketio.init_app(app)
        return app
    except Exception as e:
        print(f"error : {str(e)}")
