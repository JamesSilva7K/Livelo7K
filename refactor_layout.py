import re

with open(r'd:\Paginas ADS\Livelo\templates\index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remove all logos:
# <div style="text-align:center;margin-bottom:28px">
# <img alt="Logo" class="sys-logo" src="{{ sys_config.get('system_logo', '/static/images/logo.png') }}" style="height:96px; max-width:100%; object-fit:contain; display:inline-block;"/>
# </div>
# or similar.
logo_pattern = r'<div\s+style="text-align:center;margin-bottom:\d+px">\s*<img\s+alt="Logo"[^>]+>\s*</div>'
html = re.sub(logo_pattern, '', html, flags=re.IGNORECASE)

# Some might not have a div, just img? The code usually has:
logo_pattern_2 = r'<img\s+alt="Logo"[^>]+>'
html = re.sub(logo_pattern_2, '', html, flags=re.IGNORECASE)

# 2. Remove all footers
footer_pattern = r'<footer\s+class="funnel-footer">.*?</footer>'
html = re.sub(footer_pattern, '', html, flags=re.DOTALL | re.IGNORECASE)

# 3. Create global layout
# Find <body> tag
body_start = html.find('<body>') + len('<body>')

global_header = """
<div id="app" style="display: flex; flex-direction: column; min-height: 100vh; background: var(--bg-color);">
  <header style="text-align:center; padding: 40px 0 20px 0;">
    <img alt="Logo" class="sys-logo" src="{{ sys_config.get('system_logo', '/static/images/logo.png') }}" style="height:48px; max-width:100%; object-fit:contain; display:inline-block;"/>
  </header>
  <main style="flex: 1; display: flex; flex-direction: column; align-items: center; padding: 0 20px;">
"""

global_footer = """
  </main>
  <footer class="funnel-footer" style="padding: 30px 20px; text-align: center; color: var(--text-muted); font-size: 0.85rem; width: 100%;">
    <p>{{ sys_config.get('system_name', 'Livelo') }} | CNPJ: {{ sys_config.get('system_cnpj', '12.888.241/0001-06') }}</p>
    <p>{{ sys_config.get('system_address', 'Alameda Xingu, 512 · Alphaville, Barueri, SP') }}</p>
    <p>© 2026 · Todos os direitos reservados</p>
  </footer>
</div>
"""

# Wait, the user wants the logo height to be 96px or consistent? He said "aumente o tamanho da logo em todas as etapas" earlier, but now he wants it "mesma altura e posicionadas no mesmo lugar". I will make the logo height 96px in the global header.

global_header = global_header.replace('height:48px', 'height:96px')

# Inject global header
html = html[:body_start] + global_header + html[body_start:]

# Inject global footer before </body>
body_end = html.find('</body>')
if body_end != -1:
    html = html[:body_end] + global_footer + html[body_end:]

with open(r'd:\Paginas ADS\Livelo\templates\index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Layout refactored!")
