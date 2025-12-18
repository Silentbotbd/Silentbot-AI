const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
function addMessage(message, sender) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender + '-message');
    const bubble = document.createElement('div');
    bubble.classList.add('message-bubble');
    bubble.innerText = message;
    messageElement.appendChild(bubble);
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
function handleUserInput() {
    const message = userInput.value;
    if (message.trim() === '') return;
    addMessage(message, 'user');
    userInput.value = '';
    setTimeout(() => {
        addMessage('This is a mocked AI response.', 'bot');
    }, 1000);
}
sendButton.addEventListener('click', handleUserInput);
userInput.addEventListener('keyup', (event) => {
    if (event.key === 'Enter') {
        handleUserInput();
    }
});
