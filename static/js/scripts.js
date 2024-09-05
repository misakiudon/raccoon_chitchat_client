document.getElementById('send-button').addEventListener('click', sendMessage);

// Function to send message to ChatGPT API and then to TTS server
async function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    if (userInput.trim() === '') return; // Prevent sending empty messages

    appendMessage('あなた', userInput); // Display user input in the chat
    document.getElementById('user-input').value = ''; // Clear input field

    try {
        // Step 1: Send the user's message to ChatGPT API
        const chatgptResponse = await fetch('/chatgpt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userInput })
        });
        
        const chatgptData = await chatgptResponse.json();
        if (chatgptData.error) {
            throw new Error(chatgptData.error); // Handle errors from ChatGPT API
        }

        const aiResponse = chatgptData.response; // ChatGPT's response text
        appendMessage('ほしかわ', aiResponse); // Display ChatGPT's response

        // Step 2: Send ChatGPT's response to the TTS server using the dynamic Ngrok URL
        const ttsResponse = await fetch(`${NGROK_URL}/tts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: aiResponse })
        });

        if (!ttsResponse.ok) {
            throw new Error('Failed to get response from TTS server.');
        }

        const audioBlob = await ttsResponse.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audioElement = document.getElementById('audio');
        audioElement.src = audioUrl;
        audioElement.style.display = 'block';
        audioElement.play();

        // appendMessage('Bot', 'Playing synthesized speech...'); // Notify user of audio playback

    } catch (error) {
        console.error('Error:', error);
        appendMessage('Error', error.message); // Display error message
    }
}

// Function to append messages to the conversation display
function appendMessage(sender, message) {
    const conversation = document.getElementById('conversation');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
    conversation.appendChild(messageElement);
    conversation.scrollTop = conversation.scrollHeight;
}
