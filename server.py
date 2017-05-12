import socket
import threading


class Server:
    def __init__(self):
        self.socket = self.start()
        self.sessions = []
        self.test = "bobobbboboobbo"

    def start(self):
        self.socket = socket.socket()
        self.socket.bind(("localhost", 5000))
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


    def accept(self):
        self.socket.listen(5)
        while True:
            connection, address = self.socket.accept()

            threading.Thread(target=self.menu, args=(connection,address,)).start()

    def menu(self, connection, address):
        connection.send(self.test.encode())
        key = connection.recv(1024).decode()
        self.test = key
        #self.sessions.append((address,key))



        #connection.close()



        #connection.send("Please give the server your public key!")
        #data = connection.recv(1024).decode()
        #print("Your key is {}".format(data))
        #self.sessions.append(
        #while True:
        #    print ("connection from: " + str(address))

        #    data = connection.recv(1024).decode()
        #    if not data:
        #        connection.close()
        #        break

        #    self.send(connection, data)


    def send(self, connection, data):
        print ("from connectionected  user: " + str(data))

        data = str(data).upper()
        print ("sending: " + str(data))
        connection.send(data.encode())





def main():
    server = Server()
    server.start()
    server.accept()


    #host = "127.0.0.1"
    #port = 5000

    #mySocket = socket.socket()
    ##mySocket.bind((host,port))

    #mySocket.listen(1)
    #connection, addr = mySocket.accept()
    #print ("connectionection from: " + str(addr))
    #while True:
    #        data = connection.recv(1024).decode()
    #        if not data:
    #                break
    #        print ("from connectionected  user: " + str(data))
#
#            data = str(data).upper()
#            print ("sending: " + str(data))
#            connection.send(data.encode())

#    connection.close()

if __name__ == '__main__':
    main()
