# *******************************
# the code and ./src are deprecated
# *******************************

from flask import Flask, render_template, request, jsonify
import base64
from io import BytesIO
import src.module as module  # Assuming this is your AI manager module
import src.server as server  # Assuming this is your AI manager module
from pyngrok import ngrok

app = Flask(__name__)

# Initialize the AI Manager
ai_manager = module.RisuAIManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_name', methods=['POST'])
def set_name():
    name = request.form.get('name')
    ai_manager.set_user_name(name)
    ai_manager.initialize_chat()
    return jsonify({"message": f"Name set to {ai_manager.user_name}"})

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    
    # Handle quit/exit
    if user_input.lower() in ['quit', 'exit', '종료']:
        return jsonify({"message": "Chat ended."})

    # Process the user input with the AI Manager
    ai_manager.send_message_to_api(user_input)

    # AI response and stats
    response = {
        "likeability": ai_manager.Likeability,
        "mental": ai_manager.Mental,
        "thinking": ai_manager.thinking,
        "expression": ai_manager.expression,
        "want location": ai_manager.location,
        "dialogue": ai_manager.dialogue,
        "translated": ai_manager.translated_text
    }

    audio_data = ai_manager.text_to_speech(text=ai_manager.dialogue, model_id=0, speaker_id=0, language="JP", style=ai_manager.expression)
    
    if audio_data:
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        response["audio"] = audio_base64
    else:
        response["error"] = "Failed to convert text to speech."

    return jsonify(response)

if __name__ == "__main__":
    # Expose the app with Ngrok
    url = ngrok.connect(5002)
    print(f"Public URL: {url}")
    app.run(host="0.0.0.0", port=5002)
