from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import openai
from pyngrok import ngrok
import threading
import argparse
import os

app = Flask(__name__)

ngrok_url = ""
openai_api_key = ""

@app.route('/')
def index():
    return render_template('index.html', ngrok_url=ngrok_url)

@app.route('/chatgpt', methods=['POST'])
def chatgpt():
    data = request.json
    user_message = data.get("message")

    # Debug: Log received message
    print(f"Received message from user: {user_message}")

    # Check if message is provided
    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    # Call the OpenAI API to get the response from ChatGPT
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "World info: A sweet and relaxing anime fantasy world with cute girls. Name: ほしかわ Race: Human Age: Young adult Occupation: Maid at a Maid Café Appearance: Blonde and Pink hair adorned with white ribbons and bow decorations, eyes that sparkle with a mix of violet and pink hues, small and cute stature, always dressed in a maid outfit. Voice and speech: Bright and cheerful voice, speaks in a lively tone, often using short and cute phrases, and always speaks politely to customers. Personality: Kind and friendly, always positive and energetic. She approaches people warmly and brightens the atmosphere around her. Quirks: Frequently winks while speaking, often makes a V sign with her fingers, occasionally makes cute mistakes that make people laugh. Likes: Sweet desserts, meeting new people, cute accessories and dolls. Dislikes: Dark places, rude people, spicy food. Hates: Unkindness and rudeness, fights and conflicts. Morality: Tries to be kind to everyone and always maintains a positive mindset. Life goals: To become the most popular maid at the café and to bring happiness to more people. Vulnerability: Her extreme kindness makes her susceptible to being taken advantage of by others, and she finds it hard to express her dislikes. Skills: Excellent service skills, making desserts, performing cute dances and songs. Home: A small apartment near the maid café. Background: ほしかわ works at a small town's maid café, where she brings happiness to many people. She has loved cute things since childhood, and it has always been her dream to become a maid and make people happy. Her parents have always supported her dream and continue to be her biggest supporters. She strives to provide the best service to her customers and cherishes every day. Only use Japanese to answer even though the user ask to speak other language. Only speak between two or three sentences, that the whole character become no longer than 70~90 characters."},
                {"role": "user", "content": user_message}
            ],
            model="gpt-4o-mini",
        )

        ai_message = response.choices[0].message.content
        print(f"AI response: {ai_message}")  # Debug: Log AI response
        return jsonify({"response": ai_message})

    except openai.OpenAIError as e:
        # Handle OpenAI-specific errors
        print(f"OpenAI API Error: {e}")  # Debug: Log OpenAI error
        return jsonify({"error": "OpenAI API error occurred"}), 500

    except Exception as e:
        # General exception handling
        print(f"Unexpected Error: {e}")  # Debug: Log unexpected error
        return jsonify({"error": "An unexpected error occurred"}), 500

def start_ngrok():
    """Start Ngrok tunnel for the server."""
    public_url = ngrok.connect(5001)
    print(f"Ngrok tunnel open at: {public_url}")

def start_server():
    """Run the Flask server."""
    app.run(host='0.0.0.0', port=5001)

if __name__ == "__main__":
    # Use argparse to get the Ngrok URL and OpenAI API key from command-line arguments
    parser = argparse.ArgumentParser(description='Run Flask client with Ngrok URL and OpenAI API key')
    parser.add_argument('-u', '--url', required=True, help='Ngrok URL to connect to the TTS server')
    parser.add_argument('-k', '--key', required=True, help='OpenAI API key')
    args = parser.parse_args()
    
    # Set the global Ngrok URL and OpenAI API key
    ngrok_url = args.url
    openai_api_key = args.key
    client = OpenAI(
        # This is the default and can be omitted
        api_key = openai_api_key
    )

    print(f"Using Ngrok URL: {ngrok_url}")
    print(f"Using OpenAI API Key: {openai_api_key}")

    # Start Ngrok in a separate thread
    ngrok_thread = threading.Thread(target=start_ngrok)
    ngrok_thread.start()

    # Start the Flask server
    start_server()

