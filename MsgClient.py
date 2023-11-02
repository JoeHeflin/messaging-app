#Message Client (Python version 2.7)
#Arguments: port #,

import sys, socket, threading,select

host = 'localhost'
port = int(sys.argv[1])
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
address = (host,port)
pulse = True

sock.connect(address)

#Protocol: send prompts from server in same format as command line prompts

def login(arg): #arg must be string
	#print(arg)
	arg = arg.split(" ")
	switcher = {
		"PROMPT" : prompt,
		"LOCKOUT" : userlockedout, #login <BLOCKED<> <BLOCKED_TIMER>
	}
	command = arg[0]

	try:	
		argument = arg[1]
		return switcher[command](argument)
	except:
		return switcher[command]()

def keyboardSwitch(arg):
	#print("Keyborad switch : "+arg)
	switcher = {
		"login" : login,
		"sendmsg" : recvmsg,
		# whoelse: whoelse(content)
		# whoelsesince: whoelsesince(content)
		# block: block(content)
		# unblock: unblock(content)
		"timeout": timeout,
		"logout": logout
	}
	#print("?????")
	command = arg[0]

	# print(command)
	# print(arg[1:])
	try:
		#print(command + " SPACE " + content)
		content = arg[1]
	#print("?????")
		#print("try "+ command + " " + content)
		return switcher[command](content)
	except:
		return switcher[command]()
	
def timeout():
	print("\nSession timeout due to inactivity")
	logout()

def prompt():
	user = raw_input("Enter username: ")
	code = raw_input("Enter password: ")
	sock.send(user + " " + code)
def userlockedout(timelocked):
	print("Too many consecutive failed login attempts for this username, wait " + timelocked + " seconds to try again" )
	global pulse
	pulse = False
def recvmsg(user):
	print("\n"+user)
def logout():
	global pulse 
	pulse = False

def messagercv():
	return
# def online():
# def tryagain():

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
			try:
				serverCommand = sock.recv(2048).split(" ",1)
				#print(serverCommand)
				keyboardSwitch(serverCommand)
			except:
				continue
		sock.close()
		#print("exiting serverThread")

serverConnect = serverThread("clientSocket")
serverConnect.start()
keyboardConnect = keyThread("clientKeyboard")
keyboardConnect.start()