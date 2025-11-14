📡 Real-Time Peer-to-Peer Chat System
Flask · WebSockets · Redis · Event-Driven Backend

A clean and lightweight backend-only real-time chat application, built using Flask, Flask-SocketIO, and Redis.

Users can come online, send chat requests, accept them, and instantly start chatting inside a temporary chatroom that auto-expires after 6 hours.
This project highlights simplicity, real-time communication, and event-driven backend logic without needing a heavy frontend.

🚀 Features
🔹 Real-Time Messaging

Live chatting using WebSockets

Event-driven architecture (connect, message, disconnect)

True peer-to-peer chat rooms

🔹 Online Presence (Redis)

Users register using their phone number

Automatically marked “online” in Redis

Auto-expire if inactive

🔹 Request + Accept System

User A sends a request to User B

User B gets “incoming request”

If accepted → backend creates a chatroom ID

🔹 6-Hour Auto Expiry

Chatrooms + messages are temporary

Redis TTL cleans old rooms automatically

If users reconnect within 6 hours → chat history restored

🔹 5-Minute Dropped Connection Logic

If one person drops → room stays alive

If both offline > 5 minutes → expire room

🛠 Tech Stack
Purpose	Technology
Web Framework	Flask
WebSockets	Flask-SocketIO
In-Memory Store	Redis
Real-Time Worker	Eventlet
Architecture	Application Factory + Services Layer
Deployment	Render / Railway / Docker-ready
