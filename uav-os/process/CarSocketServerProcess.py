import socket

def CarSocketServerProcess( CarSocketService ):
    HOST = '0.0.0.0'
    PORT = 3030

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(10)
    while True:
        conn, addr = server.accept()
        # print(type(conn.recv(1024)))
        clientMessage = str(conn.recv(1024), encoding='utf-8')
        CarSocketService.setPosition( clientMessage )
        clientMessage = CarSocketService.getPosition()
        print('Client message is:', clientMessage)

        serverMessage = 'I\'m here!'
        conn.sendall(serverMessage.encode())
        conn.close()
