import re

def update_main_js():
    with open('static/js/main.js', 'r', encoding='utf-8') as f:
        js = f.read()

    # 1. Add logLeadAction function
    log_func = """
// ============================================================================
// TELEMETRIA E LOGS
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
    if "logLeadAction" not in js:
        js = js.replace('// UTILITÁRIOS', log_func + '\n// UTILITÁRIOS')

    # Inject logs into key functions
    # 1. CPF Consulting
    js = js.replace('const data = await res.json();\n    \n    if (data.ok) {', 'const data = await res.json();\n    \n    if (data.ok) {\n      logLeadAction("Digitou CPF", cpfVal);')
    
    # 2. Renda options (there are buttons that set Renda)
    js = js.replace('function selectRenda(val, btn) {', 'function selectRenda(val, btn) {\n  logLeadAction("Selecionou Renda", val);')
    js = js.replace('function selectTipoRenda(val, btn) {', 'function selectTipoRenda(val, btn) {\n  logLeadAction("Selecionou Tipo Renda", val);')
    js = js.replace('function selectMotivo(val, btn) {', 'function selectMotivo(val, btn) {\n  logLeadAction("Selecionou Motivo", val);')
    js = js.replace('function selectDia(val, btn) {', 'function selectDia(val, btn) {\n  logLeadAction("Selecionou Dia Vencimento", val);')

    # 3. Form submit Renda
    js = js.replace('async function submitRenda() {', 'async function submitRenda() {\n  logLeadAction("Enviou Questionário de Renda");')

    # 4. Card color selection
    js = js.replace('function selectColor(colorId, targetBtn) {', 'function selectColor(colorId, targetBtn) {\n  logLeadAction("Mudou cor do Cartão", colorId);')
    js = js.replace('function selectStyle(styleId, targetBtn) {', 'function selectStyle(styleId, targetBtn) {\n  logLeadAction("Mudou estilo do Cartão", styleId);')
    
    # 5. Confirm card
    js = js.replace('async function confirmCard() {', 'async function confirmCard() {\n  logLeadAction("Confirmou Cartão", `${STATE.style} - ${STATE.color}`);')

    # 6. View summary (Entregar cartao virtual)
    js = js.replace('function requestPhysicalCard() {', 'function requestPhysicalCard() {\n  logLeadAction("Clicou em Receber Cartão Físico");')

    # 7. WhatsApp submit
    js = js.replace('async function submitWhatsapp() {', 'async function submitWhatsapp() {\n  logLeadAction("Enviou WhatsApp", inputWa.value);')

    # 8. PIX Generation
    js = js.replace('async function fetchPix() {', 'async function fetchPix() {\n  logLeadAction("Chegou na Tela de Pagamento PIX");')
    js = js.replace('function copyPix() {', 'function copyPix() {\n  logLeadAction("Copiou Código PIX");')

    with open('static/js/main.js', 'w', encoding='utf-8') as f:
        f.write(js)

update_main_js()
print("main.js updated with telemetry")
