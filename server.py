import socket
import threading
import random
import time

class Session:
	def __init__(self, key, cards):
		self.key = key
		self.cards = cards
		self.wins = 0

class Server:
	def __init__(self):
		self.socket = None
		self.sessions = {}
		self.session_keys = []
		self.chosen_cards = []
		

	def start(self):
		self.socket = socket.socket()
		self.socket.bind(("localhost", 5000))
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


	def accept(self):
		self.socket.listen(5)
		while True:
			connection, address = self.socket.accept()
			self.session_keys.append(address[1])
			threading.Thread(target=self.play, args=(connection,address,)).start()
			

	def play(self, connection, address):
		counter = 0
		cards=  []
		
		while counter < 3:
			num = random.randint(1, 15)
			cards.append(num)
			counter += 1
			
		session = Session("", cards)
			
		self.sessions[address[1]] = session
		
		
		while len(self.sessions[address[1]].cards) != 0:
			message = ""
			
			for card in self.sessions[address[1]].cards:
				message += "{} ".format(card)
				
			connection.send("{}\nPlease select a card!".format(message).encode())
			

			chosen_card = int(connection.recv(1024).decode())

			self.chosen_cards.append((address[1], chosen_card))
	
			self.sessions[address[1]].cards.remove(chosen_card)

			while len(self.chosen_cards) != 2:
				pass
				
	
			time.sleep(1)

			if self.chosen_cards[0][1] == self.chosen_cards[1][1]:
				connection.send("Tied for the round!".encode())
					
			elif self.chosen_cards[0][1] > self.chosen_cards[1][1]:
				if address[1] == self.chosen_cards[0][0]:
					connection.send("You have won the round! ".encode())
					self.sessions[address[1]].wins += 1
				else:
					connection.send("You have lost the round!".encode())
					
			else:
				if address[1] == self.chosen_cards[1][0]:
					connection.send("You have won the round!".encode())
					self.sessions[address[1]].wins += 1
					
				else:
					connection.send("You have lost the round!".encode())
					
			time.sleep(1)
			
			
			#self.chosen_cards.clear()
			
			del self.chosen_cards[:]
			
		first_player = self.session_keys[0]
		second_player = self.session_keys[1]
		
		if self.sessions[first_player].wins == self.sessions[second_player].wins:
			connection.send("Tied!".encode())
		
		elif self.sessions[first_player].wins > self.sessions[second_player].wins:
			if first_player == address[1]:
				connection.send("Winner!".encode())
			
			else:
				connection.send("Loser!".encode())
				
		elif self.sessions[second_player].wins > self.sessions[first_player].wins:
			if second_player == address[1]:
				connection.send("Winner!".encode())
			
			else:
				connection.send("Loser!".encode())
			

def main():
	server = Server()
	server.start()
	server.accept()


if __name__ == '__main__':
	main()
