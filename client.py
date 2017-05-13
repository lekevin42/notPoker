import socket


class Client:
	def __init__(self):
		self.socket = None
		
	def start(self):
		self.socket = socket.socket()
		self.socket.connect(("localhost", 5000))
		
	def play(self):
		counter = 0
		max = 3
		
		while counter < max:
			data = self.socket.recv(1024).decode()
			print(data)
		
		
			message = input(" -> ")
			self.socket.send(str(message).encode())

			data = self.socket.recv(1024).decode()
			print(data)
			
			counter += 1
			
		data = self.socket.recv(1024).decode()

		print(data)

		self.socket.close()

def main():
	client = Client()
	client.start()
	client.play()
	

if __name__ == '__main__':
	main()
