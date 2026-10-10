"""Testa se o PIX EMV fallback local gera um codigo valido."""
import re, unicodedata

def emv_field(tag: str, value: str) -> str:
    return f"{tag}{len(value):02d}{value}"

def gerar_pix_fallback(chave_pix, amount, payer_name, payment_id):
    amount_str = f"{amount:.2f}"
    
    raw_name = (payer_name or "CLIENTE LIVELO")[:25].upper()
    raw_name = ''.join(c for c in unicodedata.normalize('NFD', raw_name) if unicodedata.category(c) != 'Mn')
    raw_name = re.sub(r'[^A-Z0-9 ]', '', raw_name).strip() or "CLIENTE LIVELO"
    txid = re.sub(r'[^A-Za-z0-9]', '', payment_id)[:25].ljust(25, 'x')
    city = "SAO PAULO"

    gui_val  = "br.gov.bcb.pix"
    mchant_id = emv_field("26", emv_field("00", gui_val) + emv_field("01", chave_pix))
    addl_data = emv_field("62", emv_field("05", txid))

    pix_str = (
        "000201" +
        mchant_id +
        "52040000" +
        "5303986" +
        emv_field("54", amount_str) +
        "5802BR" +
        emv_field("59", raw_name) +
        emv_field("60", city) +
        addl_data +
        "6304"
    )

    poly = 0x1021
    crc = 0xFFFF
    for byte in pix_str.encode("utf-8"):
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
    crc_str = f"{crc & 0xFFFF:04X}"
    return pix_str + crc_str


# Testa com dados reais
code = gerar_pix_fallback(
    chave_pix="suporte@livelo.com.br",
    amount=29.90,
    payer_name="Joao da Silva Santos",
    payment_id="lvl_abc12345_deadbeef"
)
print("PIX Code gerado:")
print(code)
print(f"\nTamanho: {len(code)} chars")
print(f"Inicia com 000201: {code.startswith('000201')}")
print(f"Termina com CRC 4 hex: {len(code[-4:]) == 4}")

# Valida que os campos tem tamanhos corretos
import re
fields = re.findall(r'(\d{2})(\d{2})(.+?)(?=\d{2}\d{2}|6304[0-9A-F]{4}$)', code)
print(f"\nTotal de campos encontrados: {len(fields)}")

# Re-valida CRC
pix_body = code[:-4]
crc_given = code[-4:]
poly = 0x1021
crc = 0xFFFF
for byte in pix_body.encode("utf-8"):
    crc ^= (byte << 8)
    for _ in range(8):
        crc = (crc << 1) ^ poly if crc & 0x8000 else crc << 1
computed = f"{crc & 0xFFFF:04X}"
print(f"CRC computado: {computed} | CRC no codigo: {crc_given} | Match: {computed == crc_given}")
print("\n✅ PIX VALIDO!" if computed == crc_given else "\n❌ CRC INVALIDO!")
