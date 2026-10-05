import re

html_code = """<div class="screen" id="screen-cep">
<div class="step-container" style="justify-content:center;min-height:90vh;max-width:480px;margin:0 auto">

<div class="step-card funnel-card" style="padding: 32px 24px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.04); background: #FFF;">
<h2 class="step-title" style="font-size:1.4rem; font-weight:800; margin-bottom:6px; color:#1A1A1A; text-align:center;">Endereço de Entrega</h2>
<p class="step-sub" style="font-size:0.85rem; color:#666; margin-bottom:24px; text-align:center;">Onde você deseja receber seu cartão</p>

<div class="input-group" style="margin-bottom:16px;">
<label class="input-label" style="font-size:0.75rem; color:#333; font-weight:600; margin-bottom:6px; display:block;">CEP</label>
<input type="text" id="input-cep" class="input-field" placeholder="00000-000" maxlength="9" oninput="mascaraCepInteligente(this)" style="width:100%; border:1px solid #E5E5E5; border-radius:10px; padding:14px; font-size:0.95rem; outline:none; transition: border-color 0.2s;">
</div>

<div class="input-group" style="margin-bottom:16px;">
<label class="input-label" style="font-size:0.75rem; color:#333; font-weight:600; margin-bottom:6px; display:block;">Endereço</label>
<input type="text" id="input-rua" class="input-field" placeholder="" style="width:100%; border:1px solid #E5E5E5; border-radius:10px; padding:14px; font-size:0.95rem; outline:none;">
</div>

<div style="display:flex; gap:12px; margin-bottom:16px;">
<div class="input-group" style="flex:1;">
<label class="input-label" style="font-size:0.75rem; color:#333; font-weight:600; margin-bottom:6px; display:block;">Número</label>
<input type="text" id="input-numero" class="input-field" placeholder="" style="width:100%; border:1px solid #E5E5E5; border-radius:10px; padding:14px; font-size:0.95rem; outline:none;">
</div>
<div class="input-group" style="flex:1;">
<label class="input-label" style="font-size:0.75rem; color:#333; font-weight:600; margin-bottom:6px; display:block;">Complemento</label>
<input type="text" id="input-complemento" class="input-field" placeholder="" style="width:100%; border:1px solid #E5E5E5; border-radius:10px; padding:14px; font-size:0.95rem; outline:none;">
</div>
</div>

<div class="input-group" style="margin-bottom:16px;">
<label class="input-label" style="font-size:0.75rem; color:#333; font-weight:600; margin-bottom:6px; display:block;">Bairro</label>
<input type="text" id="input-bairro" class="input-field" placeholder="" style="width:100%; border:1px solid #E5E5E5; border-radius:10px; padding:14px; font-size:0.95rem; outline:none;">
</div>

<div style="display:flex; gap:12px; margin-bottom:24px;">
<div class="input-group" style="flex:1;">
<label class="input-label" style="font-size:0.75rem; color:#333; font-weight:600; margin-bottom:6px; display:block;">Cidade</label>
<input type="text" id="input-cidade" class="input-field" placeholder="" style="width:100%; border:1px solid #E5E5E5; border-radius:10px; padding:14px; font-size:0.95rem; outline:none;">
</div>
<div class="input-group" style="flex:1;">
<label class="input-label" style="font-size:0.75rem; color:#333; font-weight:600; margin-bottom:6px; display:block;">Estado</label>
<select id="input-estado" class="input-field" style="width:100%; border:1px solid #E5E5E5; border-radius:10px; padding:14px; font-size:0.95rem; outline:none; background:#FFF; appearance:none; cursor:pointer;">
<option value="" disabled selected>Selecione</option>
<option value="AC">AC</option><option value="AL">AL</option><option value="AP">AP</option>
<option value="AM">AM</option><option value="BA">BA</option><option value="CE">CE</option>
<option value="DF">DF</option><option value="ES">ES</option><option value="GO">GO</option>
<option value="MA">MA</option><option value="MT">MT</option><option value="MS">MS</option>
<option value="MG">MG</option><option value="PA">PA</option><option value="PB">PB</option>
<option value="PR">PR</option><option value="PE">PE</option><option value="PI">PI</option>
<option value="RJ">RJ</option><option value="RN">RN</option><option value="RS">RS</option>
<option value="RO">RO</option><option value="RR">RR</option><option value="SC">SC</option>
<option value="SP">SP</option><option value="SE">SE</option><option value="TO">TO</option>
</select>
</div>
</div>

<button class="btn-primary" id="btn-cep-continuar" onclick="submitCep()" style="width:100%; padding:16px; font-size:1rem; font-weight:700; border-radius:24px; display:flex; justify-content:center; align-items:center; gap:8px;">
Continuar 
<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
</button>

<style>
.input-field:focus { border-color: #E5147A !important; box-shadow: 0 0 0 3px rgba(229,20,122,0.1) !important; }
</style>

</div>

</div>
</div>"""

with open(r'd:\Paginas ADS\Livelo\templates\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Substituir o screen-cep atual
content = re.sub(
    r'<div class="screen" id="screen-cep">.*?<!-- ═══════ SHIPPING SUCCESS \(Img 5\) ═══════ -->',
    html_code + '\n\n<!-- ═══════ SHIPPING SUCCESS (Img 5) ═══════ -->',
    content,
    flags=re.DOTALL
)

with open(r'd:\Paginas ADS\Livelo\templates\index.html', 'w', encoding='utf-8') as f:
    f.write(content)


js_code = """
async function mascaraCepInteligente(input) {
  let v = input.value.replace(/\D/g, '');
  if (v.length > 5) v = v.replace(/^(\d{5})(\d)/, '$1-$2');
  input.value = v;
  
  if (v.length === 9) { // 00000-000
    try {
      const res = await fetch(`https://viacep.com.br/ws/${v.replace('-','')}/json/`);
      const data = await res.json();
      if (!data.erro) {
        document.getElementById('input-rua').value = data.logradouro || '';
        document.getElementById('input-bairro').value = data.bairro || '';
        document.getElementById('input-cidade').value = data.localidade || '';
        document.getElementById('input-estado').value = data.uf || '';
        document.getElementById('input-numero').focus();
      }
    } catch(e) {}
  }
}
"""

with open(r'd:\Paginas ADS\Livelo\static\js\main.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# Adicionar a mascara inteligente e atualizar submitCep
if "mascaraCepInteligente" not in js_content:
    js_content += js_code

js_content = js_content.replace(
    "$id('input-cidade-uf').value",
    "$id('input-cidade').value + '/' + $id('input-estado').value"
)

with open(r'd:\Paginas ADS\Livelo\static\js\main.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("Endereço screen updated to match exactly!")
