import re

with open(r'd:\Paginas ADS\Livelo\app.py', 'r', encoding='utf-8') as f:
    code = f.read()

import_snippet = """
import qrcode
import io
import base64

def generate_qr_b64(data: str) -> str:
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception as e:
        # Fallback se a lib falhar por algum motivo
        return f"https://quickchart.io/qr?text={data}&size=300"
"""

if "def generate_qr_b64" not in code:
    # Achar um bom lugar para inserir (logo aps os imports)
    match = re.search(r'import uuid\n', code)
    if match:
        code = code[:match.end()] + import_snippet + code[match.end():]
    else:
        code = import_snippet + code

# Substituir as chamadas do QuickChart pela nossa função nativa
code = re.sub(
    r'f"https://quickchart\.io/qr\?text=\{_req\.utils\.quote\(pix_code\)\}&size=300"',
    'generate_qr_b64(pix_code)',
    code
)

with open(r'd:\Paginas ADS\Livelo\app.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("QR Code nativo implementado com sucesso!")
