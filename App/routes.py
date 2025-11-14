from flask import Blueprint, render_template, request, jsonify
from .services import *
from .socket import emit_to_user

routes_bp = Blueprint('routes', __name__)


@routes_bp.route('/', methods=['GET'])
def home_page_api():
    try:
        return render_template('homePage.html')
    except Exception as e:
        print(f"error from home page api : {str(e)}")
        return jsonify({"success": False, "error": f"Error loading page: {str(e)}"}), 500



@routes_bp.route('/register_user', methods=['POST'])
def register_user_api():
    try:
        data = request.get_json()
        status = registerUser(data)
        return jsonify({"success": True, "message": status}), 200
    except Exception as e:
        print(f"error while register user : {str(e)}")
        return jsonify({"success": False, "error": f"Error registering user: {str(e)}"}), 500



@routes_bp.route('/send_request', methods=['POST'])
def send_request_api():
    try:
        data = request.get_json()
        status = checkUserOnline(data)
        if status:
            sending_status = sendRequest(data)
            if sending_status:
                return jsonify({"success": True, "message": "Request sent successfully"}), 200
            else:
                return jsonify({"success": False, "message": "Unable to send request"}), 500
        else:
            return jsonify({"success": False, "message": "User not found"}), 404
    except Exception as e:
        print(f"error while sending request : {str(e)}")
        return jsonify({"success": False, "error": f"Error sending request: {str(e)}"}), 500



@routes_bp.route('/incoming_request', methods=['GET'])
def incoming_request_api():
    try:
        phone = request.args.get('phone')
        incoming_request = checkIncomingRequest(phone)
        if incoming_request:
            return jsonify({"success": True, "incoming_request": incoming_request}), 200
        else:
            return jsonify({"success": True, "incoming_request": []}), 200
    except Exception as e:
        print(f"error from incoming request: {str(e)}")
        return jsonify({"success": False, "error": f"Error fetching incoming requests: {str(e)}"}), 500



@routes_bp.route('/respond_request', methods=['POST'])
def respond_request_api():
    """
    Called when user accepts or declines an incoming request.
    Expected JSON: { "phone1": ..., "phone2": ..., "action": "accept" / "decline" }
    """
    try:
        data = request.get_json()
        phone1 = data.get('phone1')  # User who sent the request
        phone2 = data.get('phone2')  # User who is responding
        response_status = respondToRequest(data)
        
        # If request was accepted, notify both users via WebSocket
        if response_status and isinstance(response_status, dict) and response_status.get('accepted'):
            chat_id = response_status.get('chat_id')
            if chat_id:
                # Notify the user who sent the request (phone1)
                emit_to_user(phone1, 'request_accepted', {
                    'chat_id': chat_id,
                    'from_user': phone2,
                    'to_user': phone1
                })
                # Notify the user who accepted (phone2) - they already know from the response
                emit_to_user(phone2, 'request_accepted', {
                    'chat_id': chat_id,
                    'from_user': phone1,
                    'to_user': phone2
                })
        
        return jsonify({"success": True, "message": response_status}), 200
    except Exception as e:
        print(f"error responding to request: {str(e)}")
        return jsonify({"success": False, "error": f"Error processing response: {str(e)}"}), 500





@routes_bp.route('/chatroom/<room_id>', methods=['GET'])
def render_chatroom(room_id):
    try:
        return render_template('chatroom.html', room_id=room_id)
    except Exception as e:
        print(f"error rendering chatroom: {str(e)}")
        return jsonify({"success": False, "error": f"Unable to render chatroom: {str(e)}"}), 500


@routes_bp.route('/reconnect', methods=['POST'])
def reconnect_user_api():
    """
    When a user refreshes or rejoins within 6 hours,
    restore their chatroom and existing messages if still valid.
    """
    try:
        data = request.get_json()
        reconnect_status = reconnectUser(data)
        return jsonify({"success": True, "data": reconnect_status}), 200
    except Exception as e:
        print(f"error during reconnect: {str(e)}")
        return jsonify({"success": False, "error": f"Error reconnecting user: {str(e)}"}), 500


@routes_bp.route('/active_chatrooms', methods=['GET'])
def get_active_chatrooms_api():
    """
    Get all active chatrooms for a user.
    """
    try:
        phone = request.args.get('phone')
        if not phone:
            return jsonify({"success": False, "error": "Phone number required"}), 400
        
        chatrooms = getActiveChatrooms(phone)
        return jsonify({"success": True, "chatrooms": chatrooms}), 200
    except Exception as e:
        print(f"error getting active chatrooms: {str(e)}")
        return jsonify({"success": False, "error": f"Error fetching chatrooms: {str(e)}"}), 500


# # ---------------------------
# # CLEANUP EXPIRED CHATROOMS (optional utility route)
# # ---------------------------
# @routes_bp.route('/cleanup', methods=['POST'])
# def cleanup_expired_chats():
#     """
#     This can be triggered manually or via a scheduler
#     to clear expired chatrooms/messages from Redis.
#     """
#     try:
#         cleanup_status = cleanupExpiredChats()
#         return jsonify({"success": True, "message": cleanup_status}), 200
#     except Exception as e:
#         print(f"error cleaning expired chats: {str(e)}")
#         return jsonify({"success": False, "error": f"Error during cleanup: {str(e)}"}), 500
