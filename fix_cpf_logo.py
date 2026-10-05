import re

app_path = r'd:\Paginas ADS\Livelo\templates\index.html'
with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# We look for the cpf screen wrapper
target = r'<div id="screen-cpf" class="screen">\s*<div class="step-container">\s*<div class="step-card">'

replacement = r'''<div id="screen-cpf" class="screen">
  <div class="step-container">
    <div style="text-align:center;margin-bottom:28px">
      <img class="sys-logo" src="{{ sys_config.get('system_logo', '/static/images/logo.png') }}" alt="Logo" style="height:48px; max-width:100%; object-fit:contain; display:inline-block;">
    </div>
    <div class="step-card">'''

new_content = re.sub(target, replacement, content, count=1)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Inserted logo above CPF screen")
