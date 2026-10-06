import re
import os

app_path = "app.py"

with open(app_path, "r", encoding="utf-8") as f:
    app_code = f.read()

# Modify calc_limite in app.py to use dynamic percentages
old_calc = """    # Multiplicadores Avançados
    if "CLT" in tipo_renda or "Formal" in tipo_renda:
        base_limite *= 1.15
    elif "Autônomo" in tipo_renda or "Empresário" in tipo_renda:
        base_limite *= 1.25

    if "Negócio" in motivo or "Empresa" in motivo:
        base_limite *= 1.20
    elif "Imóvel" in motivo or "Casa" in motivo or "Carro" in motivo:
        base_limite *= 1.10"""

new_calc = """    # Multiplicadores Avançados (Dinâmicos)
    try:
        from flask import g
        db_conn = g.db if 'db' in g else get_db()
        sys_cfg = get_sys_config(db_conn)
        perc_clt = float(sys_cfg.get('perc_clt', '1.15'))
        perc_autonomo = float(sys_cfg.get('perc_autonomo', '1.25'))
        perc_negocio = float(sys_cfg.get('perc_negocio', '1.20'))
        perc_imovel = float(sys_cfg.get('perc_imovel', '1.10'))
    except Exception:
        perc_clt, perc_autonomo, perc_negocio, perc_imovel = 1.15, 1.25, 1.20, 1.10

    if "CLT" in tipo_renda or "Formal" in tipo_renda:
        base_limite *= perc_clt
    elif "Autônomo" in tipo_renda or "Empresário" in tipo_renda:
        base_limite *= perc_autonomo

    if "Negócio" in motivo or "Empresa" in motivo:
        base_limite *= perc_negocio
    elif "Imóvel" in motivo or "Casa" in motivo or "Carro" in motivo:
        base_limite *= perc_imovel"""

app_code = app_code.replace(old_calc, new_calc)

with open(app_path, "w", encoding="utf-8") as f:
    f.write(app_code)

print("Percentages simulation patched!")
