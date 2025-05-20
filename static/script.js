const socket = io();

socket.on('connect', () => {
    console.log('Connected to server');
});

socket.on('bot_reply', (data) => {
    addMessage('Bot', data.message);
});

function sendMessage() {
    const input = document.getElementById("message-input");
    const message = input.value.trim();
    if (message) {
        addMessage('You', message);
        socket.emit('user_message', { message: message });
        input.value = '';
    }
}

function addMessage(sender, text) {
    const chatBox = document.getElementById("chat-box");
    const p = document.createElement("p");
    p.innerHTML = `<strong>${sender}:</strong> ${text}`;
    chatBox.appendChild(p);
    chatBox.scrollTop = chatBox.scrollHeight;
}



