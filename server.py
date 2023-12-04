#Message Server (Python version 3.10.8)
#Arguments: port #, block duration, timeout length

import sys, socket, threading, time

offlinemsgs = dict()	#key = username, msgs recieved since last online
onlinelist = dict()		#key = online username, ClientConnection object
lockedoutlist = dict()	#key = username, value = ClientConnection object
credlog = dict()		#key = valid username, value = valid associated password
lockLog = dict()		#key = username, value = number of consecutive failed login attempts
onlineHistory = dict() 	#key = username, value = time last seen
blockedUsers = dict() 	#key = blocked person, value = list of people blocking them

credfile = open("credentials.txt")

# populate credlog
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
			# update onlineHistory for whoelsesice
			if self.user in onlineHistory:
				onlineHistory[self.user] = time.time()
			timeDelta = time.time() - self.lastActive
			timeLimit = float(sys.argv[3])
			if(timeDelta > timeLimit):
				self.sock.send("sendmsg timeout due to inactivity\z".encode())
				print(self.user +" timed out")
				self.clientSwitch(["logout"])
				break
			try:
				clientCommand = self.sock.recv(2048).decode().split(" ",1)
				self.lastActive = time.time()
				try:
					self.clientSwitch(clientCommand)
				except:
					print(clientCommand)
					self.sock.send("sendmsg Invalid Command\z".encode())
			except:
				continue
		print("Exiting thread for "+self.user)
		return

	# Direct incomming client messages to appropriate functions
	def clientSwitch(self,arg):
		command = arg[0]
		switcher ={
			"logout" : self.logout,
			"message" : self.message,
			"broadcast" : self.broadcast,
			"whoelse" : self.whoelse,
			"whoelsesince" : self.whoelsesince,
			"block" : self.block,
			"unblock" : self.unblock,
			"startprivate" : self.startprivate,
			"privateinfo" : self.privateinfo
		}
		try:
			content = arg[1]
			return switcher[command](content)
		except:
			return switcher[command]()

	def privateinfo(self,addy):
		temp = addy.split(" ")
		onlinelist[self.user] = onlinelist[self.user],(temp[0],int(temp[1]))

	def startprivate(self, user):
		if(self.user in blockedUsers and destuser in blockedUsers[self.user]):
				self.sock.send("sendmsg You can't start private messaging because the recipient has blocked you".encode())
		elif user == self.user:
			self.sock.send("sendmsg cannot start private message with self\z".encode())
		elif user in onlinelist:
			self.sock.send(("startprivate "+str(onlinelist[user][1][0])+" "+str(onlinelist[user][1][1])+"\z").encode())
			onlinelist[user][0].sock.send("privaterequest".encode())	
		elif user in credlog:
			self.sock.send(("sendmsg "+user+" not online").encode())
		else:
			self.sock.send(("sendmsg "+user+" not a valid user").encode())
			
	def unblock(self,unblockeduser):
		if unblockeduser in credlog:
			if unblockeduser == self.user:
				self.sock.send("sendmsg can't unblock yourself\z".encode())
			elif unblockeduser in blockedUsers and self.user in blockedUsers[unblockeduser]:
				blockedUsers[unblockeduser].remove(self.user)
			else:
				self.sock.send("sendmsg "+unblockeduser+" already unblocked\z".encode())
			print("blocked users:")
			print(blockedUsers)
		else:
			self.sock.send(("sendmsg "+unblockeduser+" doesn't exist\z").encode())

	def block(self,blockeduser):
		if blockeduser in credlog:
			if blockeduser == self.user:
				self.sock.send("sendmsg can't block yourself\z".encode())
			elif blockeduser in blockedUsers and self.user in blockedUsers[blockeduser]:
				self.sock.send(("sendmsg "+blockeduser+" already blocked\z").encode())
			else:
				if blockeduser in blockedUsers:
					blockedUsers[blockeduser].append(self.user)
				else:
					blockedUsers[blockeduser] = [self.user]
			print("blocked users:")
			print(blockedUsers)
		else:
			self.sock.send(("sendmsg "+unblockeduser+" doesn't exist\z").encode())

	def whoelsesince(self,timelen):
		since = time.time() - float(timelen)
		for person in onlineHistory:
			if onlineHistory[person] > since and person != self.user:
				self.sock.send(("sendmsg "+person+"\z").encode())

	def whoelse(self):
		for person in onlinelist:
			if person != self.user:
				self.sock.send(("sendmsg "+person+"\z").encode())

	def broadcast(self,info):
		for recipient in onlinelist:
			if recipient != self.user:
				if(self.user in blockedUsers and recipient in blockedUsers[self.user]):
					self.sock.send("sendmsg Your message wasn't delivered to some recipients".encode())
				else:
					self.message(recipient+" "+info+"\z")

	def message(self,info):
		destuser = info.split(" ")[0]
		try:
			msg = self.user + ": " + info.split(" ",1)[1]
			if(self.user in blockedUsers and destuser in blockedUsers[self.user]):
				self.sock.send("sendmsg Your message couldn't be delivered because the recipient has blocked you".encode())
			else:
				if(destuser in credlog and destuser != self.user):
					if(destuser in onlinelist):
						onlinelist[destuser][0].sock.send(("sendmsg "+ msg+"\z").encode())
					else:
						if(destuser in offlinemsgs):
							offlinemsgs[destuser] = offlinemsgs[destuser] +"\n"+msg
						else:
							offlinemsgs[destuser] = msg
				else:
					print("send error")
					self.sock.send(("sendmsg Invalid user: "+destuser+"\z").encode())
					return
		except:
			self.sock.send("sendmsg Invalid command format, try: message <user> <messgae>\z".encode())

	def logout(self):
		if self.user in onlinelist:
			del onlinelist[self.user]
			for person in onlinelist:
				if(person not in blockedUsers):
					onlinelist[person][0].sock.send(("sendmsg "+self.user+" is no longer online\z").encode())
				elif (self.user not in blockedUsers[person]):
					onlinelist[person][0].sock.send(("sendmsg "+self.user+" is no longer online\z").encode())
		self.pulse = False
		self.sock.send("logout".encode())
		print("User logged out, bye "+self.user)
		return

	def authorize(self):
		
		LOCK_DURATION = sys.argv[2]

		self.sock.send("login userprompt\z".encode())
		logininfo = self.sock.recv(2048).decode()
		if len(logininfo.split(" ")) == 1:
			clientuser = logininfo
			print("recieved " + clientuser)
			self.user = clientuser
			if clientuser in credlog.keys():
				if(clientuser in onlinelist.keys()):
					self.sock.send("sendmsg Account already online from a different address\z".encode())
					time.sleep(0.001)
					self.authorize()
				else:
					while 1:
						if(lockLog[clientuser] == 3 or clientuser in lockedoutlist.keys()):
							self.sock.send(("sendmsg locked out for "+str(LOCK_DURATION)+" seconds due to three consecutive failed attempts\z").encode())
							print(self.user +" locked out")
							if(clientuser not in lockedoutlist.keys()):
								self.sock.send("logout".encode())
								lockedoutlist[clientuser] = self
								time.sleep(float(LOCK_DURATION))
								del lockedoutlist[clientuser]
								lockLog[clientuser] = 0
								self.pulse = False
								print("locked out over for: " + clientuser)
							else:
								self.clientSwitch(["logout"])
							return
						self.sock.send("login passprompt".encode())
						passinfo = self.sock.recv(2048).decode()
						if len(passinfo.split(" ")) == 1:
							print("recieved "+ passinfo)
							if (passinfo == credlog[clientuser]):
								self.sock.send("sendmsg Login successful, Welcome!\z".encode())
								for user in onlinelist:
									print(onlinelist[user])
									if(user not in blockedUsers):
										onlinelist[user][0].sock.send(("sendmsg "+clientuser+" is now online\z").encode())
									elif (self.user not in blockedUsers[user]):
										onlinelist[user][0].sock.send(("sendmsg "+clientuser+" is now online\z").encode())
								onlinelist[clientuser] = self
								self.sock.send("success\z".encode())
								onlineHistory[clientuser] = time.time()
								if(self.user in offlinemsgs):
									self.sock.send(("sendmsg "+ offlinemsgs[self.user]+"\z").encode())
									del offlinemsgs[self.user]
								self.lastActive = time.time()
								print(self.user+' logged in')
								return 
							else:
								self.sock.send("sendmsg  Invalid password. Please try again\z".encode())
								lockLog[clientuser] = lockLog[clientuser] + 1
								time.sleep(0.001)
						else:
							self.sock.send("sendmsg Invalid password. Please try again\z".encode())
							lockLog[clientuser] = lockLog[clientuser] + 1
							time.sleep(0.001)
			else:	
				self.sock.send("sendmsg Invalid Username. Please try again\z".encode())
				time.sleep(0.001)
				self.authorize()
		else:
			self.sock.send("sendmsg Invalid Username. Please try again\z".encode())
			time.sleep(0.001)
			self.authorize()

# build welcome socket
port = int(sys.argv[1])
address = ('localhost', port)
welcomeSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
welcomeSocket.bind(address)

# create new socket connection and thread when requested by client
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