#Message Client (Python version 2.7)
#Arguments: port #,

import sys, socket, threading, select

host = 'localhost'
port = int(sys.argv[1])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = (host,port)
pulse = True

sock.connect(address)

#Protocol: send prompts from server in same format as command line prompts

def login(arg): #arg must be string
	arg = arg.split(" ")
	switcher = {
		"PROMPT" : prompt,
	}
	command = arg[0]
	try:	
		argument = arg[1]
		return switcher[command](argument)
	except:
		return switcher[command]()

def keyboardSwitch(arg):
	switcher = {
		"login" : login,
		"sendmsg" : recvmsg,
		"logout": logout
	}
	command = arg[0]
	try:
		content = arg[1]
		return switcher[command](content)
	except:
		return switcher[command]()

def prompt():
	user = raw_input("Enter username: ")
	code = raw_input("Enter password: ")
	sock.send(user + " " + code)

def recvmsg(user):
	print("\n"+user)

def logout():
	global pulse 
	pulse = False
	
def messagercv():
	return

class keyThread (threading.Thread):
	def __init__(self, arg):
		threading.Thread.__init__(self)
		self.arg = arg
	def run(self):
		while(pulse):
			if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
				readIn = sys.stdin.readline()[0:-1]
				sock.send(readIn)
		#print("exiting keyThread")

class serverThread (threading.Thread):
	def __init__(self, arg):
		threading.Thread.__init__(self)
		self.arg = arg
		sock.setblocking(0)
	def run(self):
		while(pulse):
			sockBuffer = ""
			try:
				data = sock.recv(2048)
				sockBuffer = sockBuffer + data
				toDo = sockBuffer.split("\z")
				for msg in toDo:
					serverCommand = msg.split(" ",1)
					try: #handles empty string
						keyboardSwitch(serverCommand)
					except:
						continue
			except:
				continue
		sock.close()
		#print("exiting serverThread")

serverConnect = serverThread("clientSocket")
serverConnect.start()
keyboardConnect = keyThread("clientKeyboard")
keyboardConnect.start()