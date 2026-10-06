import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

new_notify_card = """
        texto += f"📊 <b>ETAPAS DO FUNIL:</b>\\n"
        texto += f"📋 Motivo do Crédito: {lead['motivo_credito'] or '...'}\\n"
        texto += f"💼 Tipo de Renda: {lead['tipo_renda'] or '...'}\\n"
        texto += f"💰 Renda Informada: R$ {lead['renda'] or '...'}\\n"
        texto += f"📅 Dia Vencimento: {lead['dia_vencimento'] or '...'}\\n"
        texto += f"🎯 Limite Aprovado: R$ {lead['limite_aprovado'] or '...'}\\n"
"""

content = re.sub(
    r'texto \+= f"📊 <b>ETAPAS DO FUNIL:</b>\\n"\n\s*texto \+= f"💰 Renda Informada: R\$ \{lead\[\'renda\'\] or \'\.\.\.\'\}\\n"\n\s*texto \+= f"🎯 Limite Aprovado: R\$ \{lead\[\'limite_aprovado\'\] or \'\.\.\.\'\}\\n"',
    new_notify_card.strip('\n'),
    content,
    flags=re.DOTALL
)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Updated app.py with full lead fields in card!")
