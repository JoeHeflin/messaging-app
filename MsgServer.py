#Message Server (Python version 2.7)
#Arguments: port #, BLOCK_DURATION, timeout

import sys, socket, threading, time

offlinemsgs = dict()
onlinelist = dict()
lockedoutlist = dict()
credlog = dict()
lockLog = dict()

credfile = open("credentials.txt")

for line in credfile:
	creds = line.split(" ")
	credlog[creds[0]] = creds[1].strip()
	lockLog[creds[0]] = 0



class ClientConnection(threading.Thread):
	def __init__(self,clientSocket,clientAddress):
		threading.Thread.__init__(self)
		self.sock = clientSocket
		self.address = clientAddress
		self.user = ""
		self.pulse = True
		self.blockedlist = []
		self.lastActive = time.time()


	def run(self):

		self.authorize()
		self.sock.setblocking(0)
		while(self.pulse):
			timeDelta = time.time() - self.lastActive
			timeLimit = float(sys.argv[3])
			if(timeDelta > timeLimit):
				self.sock.send("timeout")
				print(self.user +" timed out")
				self.clientSwitch(["logout"])
				break
			try:
				clientCommand = self.sock.recv(2048).split(" ",1)
				self.lastActive = time.time()
				try:
					self.clientSwitch(clientCommand)
				except:
					self.sock.send("sendmsg Invalid Command")
			except:
				continue
		print("Exiting thread for "+self.user)
		return
		
	def clientSwitch(self,arg):
		command = arg[0]
		switcher ={
			"logout" : self.logout,
			"message" : self.message,
			"broadcast" : self.broadcast
		}
		try:
			content = arg[1]
			return switcher[command](content)
		except:
			return switcher[command]()

	def broadcast(self,info):
		for recipient in onlinelist:
			if recipient != self.user:
				self.message(recipient+" "+info)
				
	def message(self,info):
		destuser = info.split(" ")[0]
		try:
			msg = self.user + ": " + info.split(" ",1)[1]
			if(destuser in credlog and destuser != self.user):
				if(destuser in onlinelist):
					onlinelist[destuser].sock.send("sendmsg "+ msg)
				else:
					if(destuser in offlinemsgs):
						offlinemsgs[destuser] = offlinemsgs[destuser] +"\n"+msg
					else:
						offlinemsgs[destuser] = msg
			else:
				print("send error")
				self.sock.send("sendmsg Invalid user: "+destuser)
				return
		except:
			self.sock.send("sendmsg Invalid command format, try: message <user> <messgae>")

	def logout(self):
		self.sock.send("logout")
		del onlinelist[self.user]
		for person in onlinelist:
			onlinelist[person].sock.send("sendmsg "+self.user+" is no longer online")
		self.pulse = False
		print("User logged out, bye "+self.user)
		return

	def authorize(self):
		
		LOCK_DURATION = sys.argv[2]

		self.sock.send("login PROMPT")
		logininfo = self.sock.recv(2048)
		try:
			clientuser, clientpass = logininfo.split(" ")
			print("recieved " + clientuser + " " + clientpass)
			self.user = clientuser
			if(clientuser in onlinelist.keys()):
				self.sock.send("sendmsg Account already online from a different address")
				time.sleep(0.001)
				self.authorize()
			elif(clientuser in credlog.keys()):
				if(lockLog[clientuser] == 2 or clientuser in lockedoutlist.keys()):
					self.sock.send("login LOCKOUT " + LOCK_DURATION)
					if(clientuser not in lockedoutlist.keys()):
						print("client blocked")
						lockedoutlist[clientuser] = self
						time.sleep(float(LOCK_DURATION))
						del lockedoutlist[clientuser]
						lockLog[clientuser] = 0
						self.pulse = False
						print("locked out over for: " + clientuser)
					return
				elif (clientpass == credlog[clientuser]):
					self.sock.send("sendmsg Login successful, Welcome!")
					for user in onlinelist:
						onlinelist[user].sock.send("sendmsg "+clientuser+" is now online")
					onlinelist[clientuser] = self
					if(self.user in offlinemsgs):
						self.sock.send("sendmsg "+ offlinemsgs[self.user])
						del offlinemsgs[self.user]
					self.lastActive = time.time()
					print(self.user+' logged in')
					return 
				else:
					self.sock.send("sendmsg Wrong username or password, please try again")
					lockLog[clientuser] = lockLog[clientuser] + 1
					time.sleep(0.001)
					self.authorize()
			else:	
				self.sock.send("sendmsg Invalid Username")
				time.sleep(0.001)
				self.authorize()
		except:
			self.sock.send("sendmsg Invalid Username")
			time.sleep(0.001)
			self.authorize()

port = int(sys.argv[1])
address = ('localhost', port)

welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

welcomeSocket.bind(address)

while(1):
	print("Waiting for New Client Connection")
	welcomeSocket.listen(1)
	clientSocket, clientAddress = welcomeSocket.accept()
	newClient = ClientConnection(clientSocket,clientAddress)
	newClient.start()

	print("Starting New Thread")
print('close')
newClient.sock.close()
welcomeSocket.close()