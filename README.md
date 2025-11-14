📡 Real-Time Chat Application (Flask + WebSockets + Redis)

A lightweight, real-time chat application built using:

Flask – Backend REST API

Flask-SocketIO – WebSocket support for live messaging

Redis – User presence, caching & message queue for SocketIO

HTML/JS – Simple frontend chatroom

Application Factory Pattern – Clean & scalable architecture

This project demonstrates how to integrate traditional REST APIs with real-time WebSocket communication using Flask-SocketIO — ideal for learning modern backend design.

🚀 Features
🔐 User System

Register users using a simple API

Online/offline status management via Redis

👥 Real-Time Communication

Send chat requests between users

Accept requests → creates chatroom

Join chatroom and exchange live messages

Messages are delivered instantly using WebSockets

🧠 Architecture

Clean separation: routes/, socket/, services/

Socket events handled in dedicated module

Application Factory Pattern for extensibility

Redis used as transport layer for WebSocket events
