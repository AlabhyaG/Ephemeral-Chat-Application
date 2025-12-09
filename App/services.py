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


def verify_user_status(phone):
    """
    Verify if a user is still registered/online.
    Returns True if user is online, False otherwise.
    """
    if not phone:
        return False
    try:
        status = r.get(f"user:{phone}")
        return status == 'online'
    except Exception as e:
        print(f"Error verifying user status: {str(e)}")
        return False


def create_group_chatroom(creator_phone, member_phones, group_name=None):
    """
    Create a group chatroom with up to 5 members (including creator).
    Returns chat_id if successful, None otherwise.
    """
    if not creator_phone or not member_phones:
        return None
    
    # Combine creator and members, remove duplicates
    all_members = [creator_phone] + [m for m in member_phones if m != creator_phone]
    all_members = list(dict.fromkeys(all_members))  # Remove duplicates while preserving order
    
    # Check max 5 members
    if len(all_members) > 5:
        return None
    
    # Verify all members are online
    try:
        online_users = r.smembers('online_users')
        for member in all_members:
            if member not in online_users:
                return None
        
        # Create chatroom
        chat_id = str(uuid.uuid4())
        
        # Store chatroom type
        r.set(f"chatroom:{chat_id}:type", "group", ex=21600)  # 6 hours
        
        # Store members as a set
        for member in all_members:
            r.sadd(f"chatroom:{chat_id}:members", member)
        r.expire(f"chatroom:{chat_id}:members", 21600)
        
        # Store creator
        r.set(f"chatroom:{chat_id}:creator", creator_phone, ex=21600)
        
        # Store group name if provided
        if group_name:
            r.set(f"chatroom:{chat_id}:name", group_name, ex=21600)
        
        # Store status
        r.set(f"chatroom:{chat_id}:status", "active", ex=21600)
        
        # Store mapping for each member to this chatroom
        for member in all_members:
            r.sadd(f"user:{member}:chatrooms", chat_id)
        r.expire(f"user:{creator_phone}:chatrooms", 21600)
        
        return chat_id
    except Exception as e:
        print(f"Error creating group chatroom: {str(e)}")
        return None


def get_chatroom_info(chat_id):
    """
    Get information about a chatroom (type, members, name, etc.)
    """
    if not chat_id:
        return None
    
    try:
        status = r.get(f"chatroom:{chat_id}:status")
        if status != "active":
            return None
        
        chat_type = r.get(f"chatroom:{chat_id}:type") or "direct"
        
        info = {
            "chat_id": chat_id,
            "type": chat_type,
            "status": status
        }
        
        if chat_type == "group":
            members = list(r.smembers(f"chatroom:{chat_id}:members"))
            info["members"] = members
            info["creator"] = r.get(f"chatroom:{chat_id}:creator")
            group_name = r.get(f"chatroom:{chat_id}:name")
            if group_name:
                info["name"] = group_name
        else:
            # For direct chats, try to get members from chatrooms hash
            all_chatrooms = r.hgetall("chatrooms")
            for pair_key, cid in all_chatrooms.items():
                if cid == chat_id:
                    phones = pair_key.split(':')
                    info["members"] = phones
                    break
        
        return info
    except Exception as e:
        print(f"Error getting chatroom info: {str(e)}")
        return None


def get_active_chatrooms_enhanced(phone):
    """
    Enhanced version that returns both direct and group chatrooms.
    """
    if not phone:
        return []
    
    try:
        chatrooms = []
        
        # Get direct chatrooms (existing logic)
        all_chatrooms = r.hgetall("chatrooms")
        for pair_key, chat_id in all_chatrooms.items():
            if phone in pair_key:
                phones = pair_key.split(':')
                other_phone = phones[0] if phones[1] == phone else phones[1]
                status = r.get(f"chatroom:{chat_id}:status")
                if status == "active":
                    chatrooms.append({
                        "chat_id": chat_id,
                        "type": "direct",
                        "other_user": other_phone,
                        "pair": pair_key
                    })
        
        # Get group chatrooms
        user_chatrooms = r.smembers(f"user:{phone}:chatrooms")
        for chat_id in user_chatrooms:
            chat_type = r.get(f"chatroom:{chat_id}:type")
            if chat_type == "group":
                status = r.get(f"chatroom:{chat_id}:status")
                if status == "active":
                    members = list(r.smembers(f"chatroom:{chat_id}:members"))
                    group_name = r.get(f"chatroom:{chat_id}:name")
                    chatrooms.append({
                        "chat_id": chat_id,
                        "type": "group",
                        "members": members,
                        "name": group_name or f"Group ({len(members)} members)"
                    })
        
        return chatrooms
    except Exception as e:
        print(f"Error getting active chatrooms: {str(e)}")
        return []