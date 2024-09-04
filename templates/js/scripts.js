document.getElementById('send-button').addEventListener('click', sendMessage);

function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    if (userInput.trim() === '') return;

    appendMessage('User', userInput);
    document.getElementById('user-input').value = '';

    fetch('http://your_ngrok_url.ngrok.io/tts', { // Replace with your actual ngrok URL
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: userInput })
    })
    .then(response => response.blob())
    .then(blob => {
        const audioUrl = URL.createObjectURL(blob);
        const audioElement = document.getElementById('audio');
        audioElement.src = audioUrl;
        audioElement.style.display = 'block';
        audioElement.play();

        appendMessage('Bot', 'Playing synthesized voice...');
    })
    .catch(error => console.error('Error:', error));
}

function appendMessage(sender, message) {
    const conversation = document.getElementById('conversation');
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
    conversation.appendChild(messageElement);
    conversation.scrollTop = conversation.scrollHeight;
}
