import socket

def Main():
        host = 'localhost'
        port = 5000

        mySocket = socket.socket()
        mySocket.connect((host,port))

        message = ""

        while message != 'q':
                data = mySocket.recv(1024).decode()

                print(data)
                message = input(" -> ")
                mySocket.send(message.encode())
                #data = mySocket.recv(1024).decode()

                #print ('Received from server: ' + data)

                #message = input(" -> ")

        mySocket.close()

if __name__ == '__main__':
    Main()
