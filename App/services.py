import redis
import uuid
from .extension import r



def registerUser(data):
    phone = data.get('phone')
    if not phone:
        return False
    try:
        # Mark user as online
        r.set(f"user:{phone}", "online", ex=600)
        r.sadd("online_users", phone)
        r.set(f"last_seen:{phone}", "active_now", ex=600)
        return True
    except Exception as e:
        print(f"Error while registering the user: {str(e)}")
        return False


def checkUserOnline(data):
    phone = data.get('phone2')
    if not phone:
        return False
    try:
        status = r.get(f"user:{phone}")
        return status == 'online'
    except Exception as e:
        print(f"Error checking user online status: {str(e)}")
        return False


def sendRequest(data):
    phone1 = data.get('phone1')
    phone2 = data.get('phone2')
    if not phone1 or not phone2:
        return False
    try:
        online_users = r.smembers('online_users')
        print(online_users)
        if phone1 in online_users and phone2 in online_users:
            r.sadd(f"{phone1}:sent_requests", phone2)
            r.sadd(f"{phone2}:incoming_requests", phone1)
            r.expire(f"{phone1}:sent_requests", 6000)
            r.expire(f"{phone2}:incoming_requests", 6000)
            return True
        return False
    except Exception as e:
        print(f"Error while sending request: {str(e)}")
        return False


def checkIncomingRequest(phone):
    try:
        incoming = list(r.smembers(f"{phone}:incoming_requests"))
        sent = list(r.smembers(f"{phone}:sent_requests"))
        print(incoming)
        print(sent)
        return incoming if incoming else []
    except Exception as e:
        print(f"Error checking incoming requests: {str(e)}")
        return []


def respondToRequest(data):
    phone1 = data.get('phone1')
    phone2 = data.get('phone2')
    action = data.get('action')
    if not phone1 or not phone2:
        return False

    try:
        if action == 'accept':
            # remove from request lists
            r.srem(f"{phone2}:incoming_requests", phone1)
            r.srem(f"{phone1}:sent_requests", phone2)

            # create chatroom
            chat_id = createChatroom(phone1, phone2)
            return {"accepted": True, "chat_id": chat_id}
        elif action == 'decline':
            r.srem(f"{phone2}:incoming_requests", phone1)
            r.srem(f"{phone1}:sent_requests", phone2)
            return {"accepted": False}
        else:
            return False
    except Exception as e:
        print(f"Error in respondToRequest: {str(e)}")
        return False


def createChatroom(phone1, phone2):
    try:
        chat_id = str(uuid.uuid4())
        # store mapping both ways
        r.hset("chatrooms", f"{phone1}:{phone2}", chat_id)
        r.hset("chatrooms", f"{phone2}:{phone1}", chat_id)
        r.set(f"chatroom:{chat_id}:status", "active", ex=21600)  # 6 hours
        return chat_id
    except Exception as e:
        print(f"Error creating chatroom: {str(e)}")
        return None


def getActiveChatrooms(phone):
    """
    Get all active chatrooms for a user.
    Returns list of chatrooms with chat_id and other user's phone.
    """
    if not phone:
        return []
    
    try:
        chatrooms = []
        all_chatrooms = r.hgetall("chatrooms")
        
        for pair_key, chat_id in all_chatrooms.items():
            if phone in pair_key:
                # Extract the other user's phone from the pair
                phones = pair_key.split(':')
                other_phone = phones[0] if phones[1] == phone else phones[1]
                
                # Check if chatroom is still active
                status = r.get(f"chatroom:{chat_id}:status")
                if status == "active":
                    chatrooms.append({
                        "chat_id": chat_id,
                        "other_user": other_phone,
                        "pair": pair_key
                    })
        
        return chatrooms
    except Exception as e:
        print(f"Error getting active chatrooms: {str(e)}")
        return []


def reconnectUser(data):
    """
    Called when a user reconnects within timeout.
    Refresh TTLs and return any active chatroom info.
    """
    phone = data.get('phone')
    if not phone:
        return False

    try:
        # re-mark as online
        r.set(f"user:{phone}", "online", ex=600)
        r.sadd("online_users", phone)
        r.set(f"last_seen:{phone}", "active_now", ex=600)

        # find any active chatrooms
        chatrooms = []
        for k, v in r.hgetall("chatrooms").items():
            if phone in k:
                chatrooms.append({"pair": k, "chat_id": v})

        return {"status": "reconnected", "chatrooms": chatrooms}
    except Exception as e:
        print(f"Error reconnecting user: {str(e)}")
        return False
