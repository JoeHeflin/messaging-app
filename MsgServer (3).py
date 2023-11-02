#Message Server (Python version 2.7)
#Arguments: port #, BLOCK_DURATION, timeout

import sys, socket, threading, time

offlinemsgs = dict()
onlinelist = dict()
lockedoutlist = dict()
credlog = dict()
lockLog = dict()
onlineHistory = dict()
blockedUsers = dict() #key = blocked person, value = list of people blocking them

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
			if self.user in onlineHistory:
				onlineHistory[self.user] = time.time()
			timeDelta = time.time() - self.lastActive
			timeLimit = float(sys.argv[3])
			if(timeDelta > timeLimit):
				self.sock.send("sendmsg timeout due to inactivity\z")
				print(self.user +" timed out")
				self.clientSwitch(["logout"])
				break
			try:
				clientCommand = self.sock.recv(2048).split(" ",1)
				self.lastActive = time.time()
				try:
					self.clientSwitch(clientCommand)
				except:
					print(clientCommand)
					self.sock.send("sendmsg Invalid Command\z")
			except:
				continue
		print("Exiting thread for "+self.user)
		return
		
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
				self.sock.send("sendmsg You can't start private messaging because the recipient has blocked you")
		elif user == self.user:
			self.sock.send("sendmsg cannot start private message with self\z")
		elif user in onlinelist:
			self.sock.send("startprivate "+str(onlinelist[user][1][0])+" "+str(onlinelist[user][1][1])+"\z")
			onlinelist[user][0].sock.send("privaterequest")	
		elif user in credlog:
			self.sock.send("sendmsg "+user+" not online")
		else:
			self.sock.send("sendmsg "+user+" not a valid user")
			
	def unblock(self,unblockeduser):
		if unblockeduser in credlog:
			if unblockeduser == self.user:
				self.sock.send("sendmsg can't unblock yourself\z")
			elif unblockeduser in blockedUsers and self.user in blockedUsers[unblockeduser]:
				blockedUsers[unblockeduser].remove(self.user)
			else:
				self.sock.send("sendmsg "+unblockeduser+" already unblocked\z")
			print("blocked users:")
			print(blockedUsers)
		else:
			self.sock.send("sendmsg "+unblockeduser+" doesn't exist\z")

	def block(self,blockeduser):
		if blockeduser in credlog:
			if blockeduser == self.user:
				self.sock.send("sendmsg can't block yourself\z")
			elif blockeduser in blockedUsers and self.user in blockedUsers[blockeduser]:
				self.sock.send("sendmsg "+blockeduser+" already blocked\z")
			else:
				if blockeduser in blockedUsers:
					blockedUsers[blockeduser].append(self.user)
				else:
					blockedUsers[blockeduser] = [self.user]
			print("blocked users:")
			print(blockedUsers)
		else:
			self.sock.send("sendmsg "+unblockeduser+" doesn't exist\z")

	def whoelsesince(self,timelen):
		since = time.time() - float(timelen)
		for person in onlineHistory:
			if onlineHistory[person] > since and person != self.user:
				self.sock.send("sendmsg "+person+"\z")

	def whoelse(self):
		for person in onlinelist:
			if person != self.user:
				self.sock.send("sendmsg "+person+"\z")

	def broadcast(self,info):
		for recipient in onlinelist:
			if recipient != self.user:
				if(self.user in blockedUsers and recipient in blockedUsers[self.user]):
					self.sock.send("sendmsg Your message wasn't delivered to some recipients")
				else:
					self.message(recipient+" "+info+"\z")

	def message(self,info):
		destuser = info.split(" ")[0]
		try:
			msg = self.user + ": " + info.split(" ",1)[1]
			if(self.user in blockedUsers and destuser in blockedUsers[self.user]):
				self.sock.send("sendmsg Your message couldn't be delivered because the recipient has blocked you")
			else:
				if(destuser in credlog and destuser != self.user):
					if(destuser in onlinelist):
						onlinelist[destuser][0].sock.send("sendmsg "+ msg+"\z")
					else:
						if(destuser in offlinemsgs):
							offlinemsgs[destuser] = offlinemsgs[destuser] +"\n"+msg
						else:
							offlinemsgs[destuser] = msg
				else:
					print("send error")
					self.sock.send("sendmsg Invalid user: "+destuser+"\z")
					return
		except:
			self.sock.send("sendmsg Invalid command format, try: message <user> <messgae>\z")

	def logout(self):
		# print("logout")
		if self.user in onlinelist:
			del onlinelist[self.user]
			for person in onlinelist:
				# print(person)
				if(person not in blockedUsers):
					# print("2")
					# print(blockedUsers)
					# print(person)
					onlinelist[person][0].sock.send("sendmsg "+self.user+" is no longer online\z")
					# print("3")
				elif (self.user not in blockedUsers[person]):
					onlinelist[person][0].sock.send("sendmsg "+self.user+" is no longer online\z")
				# 	print("4")
				# print("5")
		# print("1")
		self.pulse = False
		self.sock.send("logout")
		print("User logged out, bye "+self.user)
		return

	def authorize(self):
		
		LOCK_DURATION = sys.argv[2]

		self.sock.send("login userprompt\z")
		logininfo = self.sock.recv(2048)
		# try:
		if len(logininfo.split(" ")) == 1:
			clientuser = logininfo
			print("recieved " + clientuser)
			self.user = clientuser
			if clientuser in credlog.keys():
				if(clientuser in onlinelist.keys()):
					self.sock.send("sendmsg Account already online from a different address\z")
					time.sleep(0.001)
					self.authorize()
				else:
					while 1:
						if(lockLog[clientuser] == 3 or clientuser in lockedoutlist.keys()):
							self.sock.send("sendmsg locked out for "+str(LOCK_DURATION)+" seconds due to three consecutive failed attempts\z")
							print(self.user +" locked out")
							if(clientuser not in lockedoutlist.keys()):
								self.sock.send("logout")
								lockedoutlist[clientuser] = self
								time.sleep(float(LOCK_DURATION))
								del lockedoutlist[clientuser]
								lockLog[clientuser] = 0
								self.pulse = False
								print("locked out over for: " + clientuser)
							else:
								self.clientSwitch(["logout"])
							return
						self.sock.send("login passprompt")
						passinfo = self.sock.recv(2048)
						if len(passinfo.split(" ")) == 1:
							print("recieved "+ passinfo)
							if (passinfo == credlog[clientuser]):
								self.sock.send("sendmsg Login successful, Welcome!\z")
								for user in onlinelist:
									print(onlinelist[user])
									if(user not in blockedUsers):
										onlinelist[user][0].sock.send("sendmsg "+clientuser+" is now online\z")
									elif (self.user not in blockedUsers[user]):
										onlinelist[user][0].sock.send("sendmsg "+clientuser+" is now online\z")
								onlinelist[clientuser] = self
								self.sock.send("success\z")
								onlineHistory[clientuser] = time.time()
								if(self.user in offlinemsgs):
									self.sock.send("sendmsg "+ offlinemsgs[self.user]+"\z")
									del offlinemsgs[self.user]
								self.lastActive = time.time()
								print(self.user+' logged in')
								return 
							else:
								self.sock.send("sendmsg Wrong password, please try again\z")
								lockLog[clientuser] = lockLog[clientuser] + 1
								time.sleep(0.001)
						else:
							self.sock.send("sendmsg Invalid password, please try again\z")
							lockLog[clientuser] = lockLog[clientuser] + 1
							time.sleep(0.001)
			else:	
				self.sock.send("sendmsg Invalid Username, please try again\z")
				time.sleep(0.001)
				self.authorize()
		else:
			self.sock.send("sendmsg Invalid Username, please try again\z")
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