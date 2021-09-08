import socket

def CarSocketServerProcess( CarSocketService ):
    HOST = '0.0.0.0'
    PORT = 3030

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(10)
    while True:
        conn, addr = server.accept()
        clientMessage = str(conn.recv(1024), encoding='utf-8')
        CarSocketService.setPosition( clientMessage )
        busPosition = CarSocketService.getPosition()
        busState = CarSocketService.getBusState()

        print('busPosition is:', busPosition)
        print('busPosition is:', busState)

        isLanding = CarSocketService.getLandingStatus()
        # print( 'isLanding: ', isLanding)
        conn.sendall(isLanding.encode())
        conn.close()
