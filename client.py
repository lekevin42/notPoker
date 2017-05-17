import socket
import Crypto
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
import os

class Client:
	"""
	Client class that handles the user.
	1) socket - the socket to send messages too
	2) house_key = the public key the house uses, used for encryption
	3) private_key = the private key used for decryption
	"""
	def __init__(self):
		self.socket = None
		self.symmetric_key = None
		self.cipher = None
		
		
	def start(self):
		self.socket = socket.socket()
		self.socket.connect(("localhost", 5000))
		self.private_key = RSA.generate(1024)
		self.symmetric_key = os.urandom(16)
		self.cipher = AES.new(self.symmetric_key, AES.MODE_ECB)
		
		
	def house_encrypt(self, house_key, message):
		"""
		Simple function to encrypt a message using the house's public key
		Parameters:
			1) house_key = use the house's public key
			2) message = the message to encrypt
			
		returns: encrypted message(str)
		"""
		return house_key.encrypt(message, None)
		
		
	def encrypt(self, message):
		"""
		Simple function to encrypt a message using a symmetric key
		Parameters:
			1) message = the message to encrypt
			
		returns: encrypted message(str)
		"""
		message = self.pad(message)
		return self.cipher.encrypt(message)
		
		
	def decrypt(self, message):
		"""
		Simple function to decrypt a message using a symmetric key
		Parameters:
			1) message = the message to decrypt
			
		returns: decrypted message(str)
		"""
		message = self.cipher.decrypt(message)
		return self.unpad(message)

		
	def pad(self, message):
		"""
		Simple function to pad the message to a mod of 16
		Parameters:
			1) message = the message to pad
			
		returns: padded message(str)
		"""
		if len(message) % 16 != 0:
			message += " "
		
		while len(message) % 16 != 0:
			message += "0"
			
		return message
		
	
	def unpad(self, message):
		"""
		Simple function to unpad the message
		Parameters:
			1) message = the message to unpad
			
		returns: encrypted message(str)
		"""
		message = message.rstrip("0")
		size = len(message)
		return message[:size-1]
	
	
	def play(self):
		counter = 0
		max = 3
		
		
		#Receive the house key for encryption
		house_key = RSA.importKey(self.socket.recv(1024).decode())
		
		#Send symmetric key to the house
		self.socket.send(house_key.encrypt(self.symmetric_key, None)[0])

		
		#Three rounds max for poker game
		while counter < max:
			#Print cards
			print(self.decrypt(self.socket.recv(1024)))

			
			#Get choice and send
			message = self.encrypt(str(input(" -> ")))
			self.socket.send(message)

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
