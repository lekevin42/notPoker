import socket
import threading
import random
import time
import Crypto
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES


class Session:
	"""
	Class used to handle a user's session.
	1) public_key = key used to encrypt messages to be sent
	2) cards = the three cards used to play
	3) wins = how many rounds did they win
	"""
	def __init__(self, key, connection, cards):
		self.symmetric_key = key
		self.cards = cards
		self.connection = connection
		self.wins = 0
		self.cipher = AES.new(self.symmetric_key, AES.MODE_ECB)
		
		
	def encrypt(self, message):
		"""
		Simple function to encrypt a message using a symmetric key
		Parameters:
			1) message = the message to encrypt
			
		returns: encrypted message(str)
		"""
		message = self.pad(message)
		return(self.cipher.encrypt(message))

		
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
		

class Server:
	"""
	Class used to handle the server using sockets. 
	Sessions are created using a thread.
	1) socket = the socket that is used to transport messages
	2) sessions = takes an address key and holds a user session
	3) chosen_cards = the cards chosen by the users
	4) private_key = used to decrypt messages sent to the server
	"""
	def __init__(self):
		self.socket = None
		self.sessions = {}
		self.session_keys = []
		self.chosen_cards = []
		self.private_key = None
		self.threads = []
		
		
	def start(self):
		"""
		Start the websocket and generate a private key for the house.
		"""
		self.socket = socket.socket()
		self.socket.bind(("localhost", 5000))
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.private_key = RSA.generate(1024)
		
		
	def decrypt(self, message):
		"""
		Use the private key to decrypt a message sent to the house.
		Parameters:
			1) message = the message to decrypt
			
		returns: decrypted message (str)
		"""
		return self.private_key.decrypt(message)


	def accept(self):
		"""
		Function used to accept connections and make a thread upon acceptance
		"""
		self.socket.listen(5)
		while True:
			connection, address = self.socket.accept()
			self.session_keys.append(address[1])
			self.threads.append(threading.Thread(target=self.play, args=(connection,address,)))
			
			while len(self.threads) != 2:
				self.accept()
		
			[thread.start() for thread in self.threads]
			[thread.join() for thread in self.threads]
			

			del self.threads[:]
			
			#After all three rounds are over decide who has won the game
			first_player = self.session_keys[0]
			second_player = self.session_keys[1]
			

			#if first player and second player have the same amount of round wins, tie
			if self.sessions[first_player].wins == self.sessions[second_player].wins:
				self.sessions[first_player].connection.send(self.sessions[first_player].encrypt("\nTied!\n"))
				self.sessions[second_player].connection.send(self.sessions[second_player].encrypt("\nTied!\n"))
			
			
			#if first player has more wins, send them the win message, else send a lose message
			elif self.sessions[first_player].wins > self.sessions[second_player].wins:
				self.sessions[first_player].connection.send(self.sessions[first_player].encrypt("\nWinner!\n"))
				self.sessions[second_player].connection.send(self.sessions[second_player].encrypt("\nLoser!\n"))

			
			#if the second player has more wins, send them the win message, else send a lose message
			elif self.sessions[second_player].wins > self.sessions[first_player].wins:
				self.sessions[first_player].connection.send(self.sessions[first_player].encrypt("\nLoser!\n"))
				self.sessions[second_player].connection.send(self.sessions[second_player].encrypt("\nWinner!\n"))

				
			#Delete keys for the next round
			del self.session_keys[:]


	def play(self, connection, address):
		"""
		Function used in the thread, handles playing and messages between the user and server
		Parameters:
			1) connection - the user's connection
			2) address - the user's address
		"""
		
		counter = 0
		cards=  []
		
		
		while counter < 3:
			num = random.randint(1, 15)
			cards.append(num)
			counter += 1
			
		
		#Send the house's public key to the user
		connection.send(self.private_key.publickey().exportKey().encode())
		
		#Receive the symmetric key from the user
		symmetric_key = self.decrypt(connection.recv(1024))

		
		#Create a user sessions holding their public key and cards
		session = Session(symmetric_key, connection, cards)
		
		#Create a dictionary entry using their address as the key
		self.sessions[address[1]] = session
		

		#While the player's still have cards, continue the loop
		while len(self.sessions[address[1]].cards) != 0:
			message = "Your cards are: "
			
			for card in self.sessions[address[1]].cards:
				message += "{} ".format(card)
			
			#Send the user's their cards and ask for them to pick a card
			message = "{}\nPlease select a card!".format(message)
			message = self.sessions[address[1]].encrypt(message)
			connection.send(message)
			
			
			#Receive the chosen card from the user and append to the server's list
			chosen_card = int(self.sessions[address[1]].decrypt(connection.recv(1024)))
			self.chosen_cards.append((address[1], chosen_card))
	
	
			#Remove the chosen card from that user's deck
			self.sessions[address[1]].cards.remove(chosen_card)

			#Wait for until both player's pick a card
			while len(self.chosen_cards) != 2:
				pass
				
	
			#If both player's cards have the same value, send a tie
			if self.chosen_cards[0][1] == self.chosen_cards[1][1]:
				connection.send(self.sessions[address[1]].encrypt("\nTied for the round!\n"))
				
				
			#If the first player has a higher value send a win message, else send a loss
			elif self.chosen_cards[0][1] > self.chosen_cards[1][1]:
				if address[1] == self.chosen_cards[0][0]:
					connection.send(self.sessions[address[1]].encrypt("\nYou have won the round!\n"))
					self.sessions[address[1]].wins += 1
				
				else:
					connection.send(self.sessions[address[1]].encrypt("\nYou have lost the round!\n"))
				
				
			#If the second player won send them a win message, else send a loss
			else:
				if address[1] == self.chosen_cards[1][0]:
					connection.send(self.sessions[address[1]].encrypt("\nYou have won the round!\n"))
					self.sessions[address[1]].wins += 1
					
				else:
					connection.send(self.sessions[address[1]].encrypt("\nYou have lost the round!\n"))
					
					
			time.sleep(1)
			
			
			#Delete the chosen cards the users have picked
			del self.chosen_cards[:]
			
			
def main():
	server = Server()
	server.start()
	server.accept()


if __name__ == '__main__':
	main()
