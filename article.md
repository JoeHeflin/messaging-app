# Reflecting on Building a Simple Python Messaging App for a Computer Networks Course

While taking a Computer Networks course at the University of New South Wales, I built a rudimentary yet robust command-line messaging app using Python. This project aimed to exercise crucial skills in Python programming, threading, and networking principles.

The core components of the messaging app revolved around two main scripts: `server.py` and `client.py`. The server script operated as the backbone of the application, responsible for handling incoming connections, managing user sessions, and relaying messages between clients. To initiate the server, specific command-line arguments were required, including port number, block duration, and timeout settings. These parameters dictated the server's behavior, regulating failed login attempts, and managing session durations.

The client script, on the other hand, facilitated user interaction with the messaging app. It allowed users to establish connections to the server, login using credentials stored in `credentials.txt`, and execute various commands to send messages, query user status, block/unblock users, initiate private sessions, and more.

A few of the more intriguing features I implemented include initiating private p2p messaging sessions and offline message queuing. These commands added depth to the app, enabling bypassing the server to send messages and queuing and asynchronous delivery of messages to users upon login, even if they were offline during the message's initial transmission. The p2p messaging feature provided a glimpse into how distributed filesharing services function which was especially cool as a student who relied heavily on such tools to find cheap alternatives to textbooks.

Throughout the project, the utilization of Python's socket library for networking and threading for handling multiple client connections concurrently was paramount. Threading enabled smooth communication between multiple clients without blocking the overall functionality of the app, showcasing the power and versatility of Python in managing concurrent tasks.

This project served as an excellent hands-on experience in understanding the intricacies of computer networking, threading, and their practical applications in software development. It highlighted the significance of clear communication protocols, error handling, and user authentication in building functional network-based applications.

The journey of building this messaging app solidified my comprehension of these fundamental networking concepts and fortified my Python programming skills, providing a concrete foundation for tackling more complex networking challenges in the future.
