# messaging-app
This is a simple python command line messaging app, originally created as a project for Computer Networks course at the University of New South Wales.


### Setting up the Virtual Environment
* For Windows:
   * Install
   ```
   pip install virtualenv
   python -m venv auto-scraping-env
   ```
   * Activate
   ```
   auto-scraping-env\Scripts\activate
   ```
* For Unix or MacOS:
   * Install
   ```
   pip install virtualenv
   python -m venv auto-scraping-env
   ```
   * Activate
   ```
   source auto-scraping-env/bin/activate
   ```

## Install required dependencies
After setting up your virtual environment, download the dependencies with 
```
pip3 install -r requirements.txt
```

## server.py
To start server
```
python MsgServer.py <port number> <block duration> <timeout>
```
All arguments are required
- Port number: port number for the server to listen/prompt clients over.
- Block duration: how long to block users after too many failed login attempts in seconds.
- Timeout: seconds of inactivity before closing client connection.

For example
```
python MsgServer.py 8080 30 50
```

## client.py
address, port #
To start client session
```
python MsgClient.py <ip address> <port number>
```
All arguments are required
- IP address: ipv4 address of active server script.
- Port number: port number for the server to listen/prompt clients over.

For example
```
python MsgClient.py 127.0.0.1 8080
```
Note: 127.0.0.1 is the address of the local host (the device running the script)


## credentials.txt
Each line contains a space separted username and password pair for the server to accept as a valid user. \
Example:  
For a username = "user" and password = "pass" enter
``` 
user pass
```

## Using the app

### Logging in
A server session with a matching address and port must be running before starting a client session. As a client, enter a valid username and password located in credentials.txt when prompted. After 3 consecutive failed attempts, the user is blocked for a period of time defined by the server (see MsgServer.py). The client session will automatically close after a period of activity defined by the server.
### Commands
Space separated in the below order.
Messages can contain spaces.
| command | arguments| description |
|------|-----|-----|
|message|\<user> <message>|send <message> to <user> through the server|
|broadcast|\<message>|send <message> to all "online" users|
|whoelse|NA|get list of all other users currently online|
|whoelsesince|\<time>|get list of all users logged in at any time in the past <time> seconds|
|block|\<user>|prevent client from recieving messages from <user>|
|unblock|\<user>|allow client to recieve messages from <user>|
|logout|NA|end client session, client considered offline|


### Private sessions
Send messages directly to user without relaying through server
| command | arguments| description |
|---------|-----|-----|
|startprivate|\<user>|requests private messaging session with <user>|
|private|\<user> <message>|send <user> <message> directly without going through server after startpivate request has been sent|
|stopprivate|NA|end p2p messaging session|
### Offline messaging
If messages are sent while a user isn't logged in, messages queue to be relayed asynchronously upon login


