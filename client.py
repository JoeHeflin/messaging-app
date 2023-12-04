#Message Client (Python version 3.10.8)
#Arguments: address, port #

import sys, socket, threading, select, time

privateLog = dict()

host = sys.argv[1]
port = int(sys.argv[2])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = (host,port)
pulse = True
username = ""

sock.connect(address)

def login(arg): 
	arg = arg.split(" ")
	switcher = {
		"userprompt" : userprompt,
		"passprompt" : passprompt
	}
	command = arg[0]
	try:	
		argument = arg[1]
		return switcher[command](argument)
	except:
		return switcher[command]()

# Direct incomming server messages and cli commands to appropriate functions
def keyboardSwitch(arg):
	switcher = {
		"login" : login,
		"sendmsg" : recvmsg,
		"logout": logout,
		"startprivate" : startprivate,
		"success" : success,
		"private" : sendprivate,
		"privaterequest" : privaterequest,
		"private" : sendprivate,
		"stopprivate" : stopprivate
	}
	command = arg[0]
	try:
		content = arg[1]
		return switcher[command](content)
	except:
		return switcher[command]()

def stopprivate(user):
	privateLog[user].stop = True

def privaterequest():
	print("private connection requested")
	try:
		privateSocket.settimeout(5)
		privateSocket.listen(1)
	except:
		print("timedout")
	peerSocket, peerAddress = privateSocket.accept()
	newP2P = privateThread(peerSocket)
	newP2P.start()

def success():
	time.sleep(0.2)
	addy, port = privateAddress
	sock.send(("privateinfo "+ addy + " " + str(port)).encode())

def sendprivate(usermsg):
	user,msg = usermsg.split(" ",1)
	if user in privateLog:
		privateLog[user].sock.send(username+"(private): "+msg+"\z".encode())
	else:
		print("User not in private session. Use command \"startprivate <user>\" to start a private conversation")

def startprivate(portandaddress):
	print("trying to start private connection")
	temp = portandaddress.split(" ")
	julia = (temp[0],int(temp[1]))
	time.sleep(0.002)
	daniel = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	daniel.connect(julia)
	newP2P = privateThread(daniel)
	newP2P.start()

def userprompt():
	global username
	username = input("Enter username: ")
	sock.send(username.encode())

def passprompt():
	password = input("Enter password: ")
	sock.send(password.encode())

def recvmsg(user):
	print("\n"+user)

def logout():
	global pulse 
	pulse = False
	
def messagercv():
	return

# thread for keyboard inputs
class keyThread (threading.Thread):
	def __init__(self, arg):
		threading.Thread.__init__(self)
		self.arg = arg
	def run(self):
		while(pulse):
			if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
				readIn = sys.stdin.readline()[0:-1]
				if readIn.split(" ")[0] == "private":
					try:
						keyboardSwitch(readIn.split(" ",1))
					except:
						print("Wrong format, try: private <user> <msg>")
				elif readIn.split(" ")[0] == "stopprivate":
					try:
						keyboardSwitch(readIn.split(" ",1))
					except:
						print("Wrong format, try: stopprivate <user>")
				else:
					sock.send(readIn.encode())

# thread to listen on server connection
class serverThread (threading.Thread):
	def __init__(self, arg):
		threading.Thread.__init__(self)
		self.arg = arg
		sock.setblocking(0)
	def run(self):
		while(pulse):
			sockBuffer = ""
			try:
				data = sock.recv(2048).decode()
			except:
				data = ""
			if data == "":
				continue
			else: #handles empty string
				sockBuffer = sockBuffer + data
				toDo = sockBuffer.split("\z")
				for msg in toDo:
					if msg == "":
						continue
					else:
						serverCommand = msg.split(" ",1)
						keyboardSwitch(serverCommand)
		sock.close()

# Thread for listening to private connection
class privateThread (threading.Thread):
	def __init__(self, socket):
		threading.Thread.__init__(self)
		self.sock = socket
		self.alive = True
		self.stop = False
		self.sock.setblocking(0)
		self.peername = ""

	def run(self):
		self.sock.send("username "+username+"\z".encode())
		while self.alive:
			if not pulse or self.stop:
				print("kill other thread")
				self.sock.send("kill yourself".encode())
				self.alive = False
			else:
				sockBuffer = ""
				try:
					data = self.sock.recv(2048).decode()
				except:
					data = ""
				if data == "":
					continue
				else: #handles empty string
					sockBuffer = sockBuffer + data
					toDo = sockBuffer.split("\z")
					for msg in toDo:
						if msg == "":
							continue
						elif msg == "kill yourself":
							self.alive = False
						elif msg.split(" ")[0] == "username":
							self.peername = msg.split(" ")[1]
							privateLog[self.peername] = self
						else:
							print(msg)
		try:
			del privateLog[self.peername]
		except:
			print("Key error: ")
			print(privateLog)
		self.sock.close()
		
# Start client threads	
serverConnect = serverThread("clientSocket")
serverConnect.start()
keyboardConnect = keyThread("clientKeyboard")
keyboardConnect.start()

# Build socket to listen for private connection but wait to be prompted to listen (line 58)
temp = (host,0)
privateSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
privateSocket.bind(temp)
privateAddress = privateSocket.getsockname()