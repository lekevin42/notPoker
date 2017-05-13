import socket
import threading
import random
import time
import Crypto
from Crypto.PublicKey import RSA

class Session:
	def __init__(self, key, cards):
		self.key = key
		self.cards = cards
		self.wins = 0
		
	def encrypt(self, message):
		return self.key.encrypt(message, None)
		


class Server:
	def __init__(self):
		self.socket = None
		self.sessions = {}
		self.session_keys = []
		self.chosen_cards = []
		self.private_key = None
		
		

	def start(self):
		self.socket = socket.socket()
		self.socket.bind(("localhost", 5000))
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.private_key = RSA.generate(1024)
		
	def decrypt(self, message):
		return self.private_key.decrypt(message)


	def accept(self):
		self.socket.listen(5)
		while True:
			connection, address = self.socket.accept()
			self.session_keys.append(address[1])
			threading.Thread(target=self.play, args=(connection,address,)).start()
		

	#def encrypt(self, address, message):
	#	return self.sessions[address].encrypt(message)
		

	def play(self, connection, address):
		counter = 0
		cards=  []
		
		
		
		while counter < 3:
			num = random.randint(1, 15)
			cards.append(num)
			counter += 1
			

		
		key = connection.recv(1024).decode()
		
		
		key = RSA.importKey(key)
		
		#print(key)
		
		connection.send(self.private_key.publickey().exportKey().encode())
		session = Session(key, cards)
			
		self.sessions[address[1]] = session
		
		#print(self.sessions[address[1]].encrypt("WTF"))
		
		
		
		while len(self.sessions[address[1]].cards) != 0:
			message = ""
			
			for card in self.sessions[address[1]].cards:
				message += "{} ".format(card)
				
			message = "{}\nPlease select a card".format(message)
			message = self.sessions[address[1]].encrypt(message)
				
			connection.send(message[0])
			

			chosen_card = int(self.decrypt(connection.recv(1024)))
			#print(chosen_card)
			#print(self.sessions[address[1]].cards)
			
			#chosen_card = self.sessions[address[1]].decrypt(chosen_card)
			
			#print(self.decrypt(chosen_card))

			self.chosen_cards.append((address[1], chosen_card))
	
			self.sessions[address[1]].cards.remove(chosen_card)

			while len(self.chosen_cards) != 2:
				pass
				
	
			time.sleep(1)

			if self.chosen_cards[0][1] == self.chosen_cards[1][1]:
				connection.send(self.sessions[address[1]].encrypt("Tied for the round!")[0])
					
			elif self.chosen_cards[0][1] > self.chosen_cards[1][1]:
				if address[1] == self.chosen_cards[0][0]:
					connection.send(self.sessions[address[1]].encrypt("You have won the round! ")[0])
					self.sessions[address[1]].wins += 1
				
				else:
					connection.send(self.sessions[address[1]].encrypt("You have lost the round!")[0])
					
			else:
				if address[1] == self.chosen_cards[1][0]:
					connection.send(self.sessions[address[1]].encrypt("You have won the round!")[0])
					self.sessions[address[1]].wins += 1
					
				else:
					connection.send(self.sessions[address[1]].encrypt("You have lost the round!")[0])
					
			time.sleep(1)
			
			
			#self.chosen_cards.clear()
			
			del self.chosen_cards[:]
			
		first_player = self.session_keys[0]
		second_player = self.session_keys[1]
		
		if self.sessions[first_player].wins == self.sessions[second_player].wins:
			connection.send(self.sessions[address[1]].encrypt("Tied!")[0])
		
		elif self.sessions[first_player].wins > self.sessions[second_player].wins:
			if first_player == address[1]:
				connection.send(self.sessions[address[1]].encrypt("Winner!")[0])
			
			else:
				connection.send(self.sessions[address[1]].encrypt("Loser!")[0])
				
		elif self.sessions[second_player].wins > self.sessions[first_player].wins:
			if second_player == address[1]:
				connection.send(self.sessions[address[1]].encrypt("Winner!")[0])
			
			else:
				connection.send(self.sessions[address[1]].encrypt("Loser!")[0])
			

def main():
	server = Server()
	server.start()
	server.accept()


if __name__ == '__main__':
	main()
