// GreenGrid AI Floating Chatbot Logic
document.addEventListener('DOMContentLoaded', function() {
  const toggleBtn = document.getElementById('chatbotToggleBtn');
  const closeBtn = document.getElementById('chatbotCloseBtn');
  const panel = document.getElementById('chatbotPanel');
  const form = document.getElementById('chatbotForm');
  const input = document.getElementById('chatbotInput');
  const messagesContainer = document.getElementById('chatbotMessages');
  const chipBtns = document.querySelectorAll('.chip-btn');

  if (!toggleBtn || !panel || !form) return;

  // Toggle Panel
  toggleBtn.addEventListener('click', function() {
    panel.classList.toggle('active');
    if (panel.classList.contains('active')) {
      input.focus();
    }
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', () => panel.classList.remove('active'));
  }

  function appendMessage(text, isUser = false) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-msg ${isUser ? 'user-msg' : 'bot-msg'}`;
    
    // Parse bold markdown **text** into <strong>
    let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formattedText = formattedText.replace(/\n/g, '<br>');
    
    msgDiv.innerHTML = formattedText;
    messagesContainer.appendChild(msgDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }

  async function sendMessage(queryText) {
    const userQuery = queryText || input.value.trim();
    if (!userQuery) return;

    appendMessage(userQuery, true);
    if (!queryText) input.value = '';

    // Show typing indicator
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-msg bot-msg';
    typingDiv.style.fontStyle = 'italic';
    typingDiv.style.color = 'var(--text-muted)';
    typingDiv.textContent = 'GridBot AI is thinking...';
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userQuery })
      });

      const data = await res.json();
      messagesContainer.removeChild(typingDiv);

      if (data.response) {
        appendMessage(data.response, false);
      } else {
        appendMessage("Sorry, I am having trouble connecting to the Grid AI network.", false);
      }
    } catch (err) {
      console.error(err);
      if (typingDiv.parentNode) messagesContainer.removeChild(typingDiv);
      appendMessage("For support & assistance, please call Admin Srujana at: **+91 98765 43210**", false);
    }
  }

  form.addEventListener('submit', function(e) {
    e.preventDefault();
    sendMessage();
  });

  chipBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const query = this.dataset.query;
      sendMessage(query);
    });
  });
});
