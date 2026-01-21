# Real-Time Chat Application (Flask + WebSockets + Redis)

A lightweight real-time chat backend built using Flask, Flask-SocketIO, and Redis. Supports user registration, online presence tracking, chat requests, and real-time messaging.

---

## 🚀 Features

* User registration
* Online user tracking via Redis
* Send/receive chat requests
* Temporary chatroom creation
* Real-time messaging using WebSockets
* Simple HTML/JS pages for testing

---

## 🧰 Tech Stack

* **Flask** (Python)
* **Flask-SocketIO**
* **Redis**
* **HTML + JavaScript**

---

## 📁 Project Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── routes.py
│   ├── socket_events.py
│   ├── services/
│   └── templates/
├── run.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation Steps

### 1️⃣ Clone the repository

```bash
git clone https://github.com/yourusername/realtime-chat.git
cd realtime-chat
```

### 2️⃣ Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🗄️ Redis Setup

### macOS

```bash
brew install redis
brew services start redis
```

### Linux

```bash
sudo apt install redis-server
sudo systemctl start redis
```

### Windows

Install **Memurai** or the official Redis MSI.

### Test Redis

```bash
redis-cli ping
# PONG
```

---

## ▶️ Running the App

Start the backend:

```bash
python run.py
```

App will be available at:

```
http://127.0.0.1:5000/
```

---

## 🔌 REST API Endpoints

### **Register User**

```
POST /register_user
```

### **Send Chat Request**

```
POST /send_request
```

### **Respond to Chat Request**

```
POST /respond_request
```

### **Open Chatroom**

```
GET /chatroom?room_id={id}
```

---

## 🔄 WebSocket Events

### Join Room

```javascript
socket.emit("join_room", {
  room: "room123",
  phone: "9876543210"
});
```

### Send Message

```javascript
socket.emit("send_message", {
  room: "room123",
  sender: "9876543210",
  message: "Hello!"
});
```

### Receive Message

```javascript
socket.on("receive_message", (data) => {
  console.log(data);
});
```

---

