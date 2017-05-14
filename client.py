import socket
import Crypto
from Crypto.PublicKey import RSA


class Client:
	"""
	Client class that handles the user.
	1) socket - the socket to send messages too
	2) house_key = the public key the house uses, used for encryption
	3) private_key = the private key used for decryption
	"""
	def __init__(self):
		self.socket = None
		self.house_key = None
		self.private_key = None
		
	def start(self):
		self.socket = socket.socket()
		self.socket.connect(("localhost", 5000))
		self.private_key = RSA.generate(1024)
		
	def encrypt(self, message):
		return self.house_key.encrypt(message, None)
		
	def decrypt(self, message):
		return self.private_key.decrypt(message)
	
	
	def play(self):
		counter = 0
		max = 3
		
		
		#Send public key to the house
		public_key = self.private_key.publickey()
		self.socket.send(public_key.exportKey().encode())
		
		
		#Receive the house key for encryption
		self.house_key = RSA.importKey(self.socket.recv(1024).decode())

		
		#Three rounds max for poker game
		while counter < max:
			#Print cards
			print(self.decrypt(self.socket.recv(1024)))

			
			#Get choice and send
			message = self.encrypt(str(input(" -> ")))
			self.socket.send(message[0])

			#Get status of round
			print(self.decrypt(self.socket.recv(1024)))

			counter += 1
			
		#Print who won or lost or tied
		print(self.decrypt(self.socket.recv(1024)))

		#Cleanup socket
		self.socket.close()

		
def main():
	client = Client()
	client.start()
	client.play()
	

if __name__ == '__main__':
	main()
