from App import createApp,extension

stocketio = extension.socketio

if __name__=='__main__':
    app = createApp()
    stocketio.run(app,allow_unsafe_werkzeug=True)