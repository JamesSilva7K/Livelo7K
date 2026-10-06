import re

with open('static/js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Inject the function definition
if "function logLeadAction" not in js:
    log_func = """
// ============================================================================
// TELEMETRIA E LOGS (MONITORAMENTO MILITAR)
// ============================================================================
function logLeadAction(action, details='') {
  if(!STATE.sessionId) return;
  fetch('/api/log-action', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: STATE.sessionId, action: action, details: details })
  }).catch(()=>{});
}
"""
    js = js.replace('// UTILITÁRIOS', log_func + '\n// UTILITÁRIOS')

# 1. CPF
js = re.sub(
    r'(async function consultarCpf\(\) \{.*?const data = await res\.json\(\);\s*if \(data\.ok\) \{)',
    r'\1\n      logLeadAction("Informou CPF Válido", cpfVal);',
    js,
    flags=re.DOTALL
)

# 2. Renda buttons
js = re.sub(r'function selectRenda\(val, btn\) \{', r'function selectRenda(val, btn) {\n  logLeadAction("Clicou na Renda", val);', js)
js = re.sub(r'function selectTipoRenda\(val, btn\) \{', r'function selectTipoRenda(val, btn) {\n  logLeadAction("Selecionou Tipo Renda", val);', js)
js = re.sub(r'function selectMotivo\(val, btn\) \{', r'function selectMotivo(val, btn) {\n  logLeadAction("Selecionou Motivo", val);', js)
js = re.sub(r'function selectDia\(val, btn\) \{', r'function selectDia(val, btn) {\n  logLeadAction("Selecionou Vencimento", val);', js)

# 3. submitBilling
js = re.sub(
    r'(async function submitBilling\(\) \{.*?)STATE\.renda = (.*?);',
    r'\1logLeadAction("Avançou Formulário de Renda", \2);\n  STATE.renda = \2;',
    js,
    flags=re.DOTALL
)

# 4. selectColor / style
js = re.sub(r'function selectColor\(colorId, targetBtn\) \{', r'function selectColor(colorId, targetBtn) {\n  logLeadAction("Escolheu Cor do Cartão", colorId);', js)
js = re.sub(r'function selectStyle\(styleId, targetBtn\) \{', r'function selectStyle(styleId, targetBtn) {\n  logLeadAction("Escolheu Categoria do Cartão", styleId);', js)

# 5. confirmCard
js = re.sub(
    r'(async function confirmCard\(\) \{.*?)const res = await fetch\(\'/api/card-style\'',
    r'\1logLeadAction("Confirmou Personalização", `${STATE.style} - ${STATE.color}`);\n  const res = await fetch(\'/api/card-style\'',
    js,
    flags=re.DOTALL
)

# 6. requestPhysicalCard
js = re.sub(r'function requestPhysicalCard\(\) \{', r'function requestPhysicalCard() {\n  logLeadAction("Clicou em Receber Cartão Físico");', js)

# 7. WhatsApp
js = re.sub(
    r'(async function submitWhatsapp\(\) \{.*?)const inputEl',
    r'\1const inputEl',
    js,
    flags=re.DOTALL
)
js = re.sub(
    r'(async function submitWhatsapp\(\) \{.*?if \(\!inputEl\.value \|\| inputEl\.value\.length < 10\) \{)',
    r'\1',
    js,
    flags=re.DOTALL
)
# actually a simpler hook for WhatsApp:
js = js.replace("async function submitWhatsapp() {\n  hideErr('wa-error');", "async function submitWhatsapp() {\n  logLeadAction('Tentou enviar WhatsApp');\n  hideErr('wa-error');")

# 8. PIX Generation
js = js.replace("async function gerarPix() {\n  if (!STATE.sessionId) return;", "async function gerarPix() {\n  logLeadAction('Iniciou Geração do PIX');\n  if (!STATE.sessionId) return;")

# 9. copyPix
js = js.replace("function copyPix() {\n  const pixCode =", "function copyPix() {\n  logLeadAction('Copiou o PIX');\n  const pixCode =")

with open('static/js/main.js', 'w', encoding='utf-8') as f:
    f.write(js)
