from App import createApp,extension

stocketio = extension.socketio

if __name__=='__main__':
    app = createApp()
    stocketio.run(app,allow_unsafe_werkzeug=True,port=5000,host='0.0.0.0')
