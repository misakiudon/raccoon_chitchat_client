from flask import Flask, render_template, request, jsonify
from conversation_manager import ConversationManager
import re

app = Flask(__name__)

# Initialize OpenAI API key and ConversationManager
OPENAI_API_KEY = ""   # Replace with your actual OpenAI API key
conversation_manager = ConversationManager(api_key=OPENAI_API_KEY, user_name="User")

conversation_count = 20
offense_count = 0  # Track number of sensitive content occurrences

# Define sensitive content patterns (Add more patterns as needed)
sensitive_patterns = [r"abusive language", r"inappropriate sexual content"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    global conversation_count, offense_count

    if conversation_count > 0:
        conversation_count -= 1
    
    # Get user message
    user_message = request.json.get("message")

    # Check if the message contains sensitive content
    if detect_sensitive_content(user_message):
        if offense_count == 0:
            # First offense: Give a warning
            ai_response = conversation_manager.send_message_to_api("Warning: Sensitive content detected.")
            offense_count += 1
            response = {
                "response": "そんなことを言ってはいけません。会話を続けたい場合は、礼儀を守ってください。",
                "likeability": max(conversation_manager.Likeability - 10, 0),
                "mental": max(conversation_manager.Mental - 10, 0),
                "expression": "anger",
                "thinking": "이런 대화를 계속하면 안 될 것 같아.",
                "quests": conversation_manager.quests,
                "countdown": conversation_count
            }
        else:
            # Second offense: End the conversation
            ai_response = "申し訳ありませんが、もう会話はできません。さようなら。"
            offense_count += 1
            response = {
                "response": ai_response,
                "likeability": 0,
                "mental": 0,
                "expression": "sad",
                "thinking": "더 이상 대화를 할 수 없을 것 같아.",
                "quests": conversation_manager.quests,
                "countdown": conversation_count
            }
            # Disable further input by sending a final message
            conversation_count = 0
    else:
        # Regular conversation flow
        if conversation_count > 0:
            conversation_count = conversation_count - 1
        
        # Generate AI response
        ai_response = conversation_manager.send_message_to_api(user_message)

        response = {
            "response": ai_response,
            "likeability": conversation_manager.Likeability,
            "mental": conversation_manager.Mental,
            "expression": conversation_manager.expression,
            "thinking": conversation_manager.thinking,
            "quests": conversation_manager.quests,
            "countdown": conversation_count
        }

        print(response)

    return jsonify(response)

@app.route('/ask_something', methods=['POST'])
def ask_something():
    global conversation_count

    # Generate a random question or prompt from the AI
    ai_response = conversation_manager.send_message_to_api("Can you ask the user something to continue the conversation?")

    response = {
        "response": ai_response,
        "likeability": conversation_manager.Likeability,
        "mental": conversation_manager.Mental,
        "expression": conversation_manager.expression,
        "thinking": conversation_manager.thinking,
        "quests": conversation_manager.quests,
        "countdown": conversation_count
    }
    print(response)

    return jsonify(response)

def detect_sensitive_content(message: str) -> bool:
    """
    Check if the message contains any sensitive content.
    """
    for pattern in sensitive_patterns:
        if re.search(pattern, message):
            return True
    return False

if __name__ == '__main__':
    app.run(port=5002)
