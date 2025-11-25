// YEAR
document.getElementById('year').textContent = new Date().getFullYear();

// Chat selectors
const chatIcon = document.getElementById('chatbot-icon');
const overlay = document.getElementById('chat-overlay');
const closeChat = document.getElementById('close-chat');
const sendBtn = document.getElementById('send-btn');
const chatInput = document.getElementById('chat-input');
const chatBody = document.getElementById('chat-body');

// Open / Close Chat
function openChat(){
  overlay.style.display = 'flex';
  overlay.setAttribute('aria-hidden','false');
  chatInput.focus();
}
function closeChatPanel(){
  overlay.style.display = 'none';
  overlay.setAttribute('aria-hidden','true');
  chatIcon.focus();
}

chatIcon.addEventListener('click', openChat);
closeChat.addEventListener('click', closeChatPanel);
overlay.addEventListener('click', (e)=>{ if(e.target === overlay) closeChatPanel(); });

// Create Message
function appendMessage(text, role='bot'){
  const el = document.createElement('div');
  el.className = 'msg ' + (role === 'bot' ? 'bot' : 'user');
  el.innerHTML = text.replace(/</g,'&lt;').replace(/>/g,'&gt;');
  chatBody.appendChild(el);
  chatBody.scrollTop = chatBody.scrollHeight;
}

// Bot reply logic
function simulateBotReply(query){
  const lower = query.toLowerCase();

  if(lower.includes('atomic habits')){
    return 'If you like <strong>Atomic Habits</strong>, try:<ul><li>The Power of Habit</li><li>Tiny Habits</li><li>Make Time</li></ul>';
  }
  if(lower.includes('romance')){
    return 'Top romance picks:<ul><li>Pride and Prejudice</li><li>The Time Traveler\'s Wife</li><li>The Night Circus</li></ul>';
  }
  if(lower.includes('suggest') || lower.includes('recommend')){
    return 'Readers also enjoyed:<ul><li>Sapiens</li><li>The Alchemist</li><li>The Goldfinch</li></ul>';
  }

  return 'Here are a few suggestions:<ul><li>Educated</li><li>Norwegian Wood</li><li>The Great Gatsby</li></ul>';
}

// Send message handler
function handleSend(){
  const text = chatInput.value.trim();
  if(!text) return;

  appendMessage(text, 'user');

  chatInput.value = '';

  // Typing indicator
  const typing = document.createElement('div');
  typing.className = 'msg bot';
  typing.textContent = '🤖 BookBot is typing...';
  chatBody.appendChild(typing);

  chatBody.scrollTop = chatBody.scrollHeight;

  setTimeout(()=>{
    typing.remove();
    const reply = simulateBotReply(text);

    const botMsg = document.createElement('div');
    botMsg.className = 'msg bot';
    botMsg.innerHTML = reply;

    chatBody.appendChild(botMsg);
    chatBody.scrollTop = chatBody.scrollHeight;

  }, 800 + Math.random()*700);
}

sendBtn.addEventListener('click', handleSend);
chatInput.addEventListener('keydown', (e)=>{ if(e.key === 'Enter') handleSend(); });

// Close on Escape
document.addEventListener('keydown', (e)=>{
  if(e.key === 'Escape' && overlay.style.display === 'flex') closeChatPanel();
});
