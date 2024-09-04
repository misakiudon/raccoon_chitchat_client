from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message")
    
    # This is where the conversation logic with your GPT-like model would go.
    # Here, we're simulating a response.
    response = generate_response(user_input)
    
    return jsonify({"response": response})

def generate_response(user_input):
    # Simulate a response from a GPT-like model.
    # In a real scenario, you'd call your model here.
    return f"Simulated response to: {user_input}"

if __name__ == "__main__":
    app.run(debug=True)
