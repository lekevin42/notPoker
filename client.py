import socket
import Crypto
from Crypto.PublicKey import RSA


class Client:
	def __init__(self):
		self.socket = None
		self.house_key = None
		
	def start(self):
		self.socket = socket.socket()
		self.socket.connect(("localhost", 5000))
		
	def encrypt(self, message):
		return self.house_key.encrypt(message, None)
	
	
	def play(self):
		counter = 0
		max = 3
		

		private_key = RSA.generate(1024)
		
		#private_key = private_key.exportKey()
		
		public_key = private_key.publickey()
		
		#test = private_key.encrypt("BS", None)
		
		#print(test)
		
		#print(public_key.decrypt(test[0]))
		
		
		
		#print(public_key)
		#test = public_key.exportKey()
		
		#print(test)
		
		#print(RSA.importKey(test))
		
		#print(private_key, public_key)
		
		#encrypted = public_key.encrypt("BS", None)
		
		#print(private_key.decrypt(encrypted))
		
		
		self.socket.send(public_key.exportKey().encode())
		
		self.house_key = RSA.importKey(self.socket.recv(1024).decode())
		
		#print(self.house_key)
		
		#print(self.encrypt("wtf"))
		
		while counter < max:
			data = self.socket.recv(1024)
			print(private_key.decrypt(data))
		
		
			message = self.encrypt(str(input(" -> ")))
			#print(message)
			
			self.socket.send(message[0])

			data = self.socket.recv(1024)
			print(private_key.decrypt(data))
			
			counter += 1
			
		data = self.socket.recv(1024)

		print(private_key.decrypt(data))

		self.socket.close()

def main():
	client = Client()
	client.start()
	client.play()
	

if __name__ == '__main__':
	main()
