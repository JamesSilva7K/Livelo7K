import os
import re

files = [
    r'd:\Paginas ADS\Livelo\templates\index.html',
    r'd:\Paginas ADS\Livelo\mod_livelo.py',
    r'd:\Paginas ADS\Livelo\mod_livelo2.py',
    r'd:\Paginas ADS\Livelo\mod_frete.py'
]

replacement = r'''<div class="funnel-logo" style="text-align:center;margin-bottom:20px;">
      <img class="sys-logo" src="{{ sys_config.get('system_logo', '/static/images/logo.png') }}" alt="Logo" style="height:48px; max-width:100%; object-fit:contain; display:inline-block;">
    </div>'''

for file_path in files:
    if not os.path.exists(file_path):
        continue
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the text logo. It looks like:
    # <div class="funnel-logo">
    #   <span style="color:#E5147A;font-size:1.4rem;line-height:1">&#9670;</span>
    #   <span style="font-family:Inter,sans-serif;font-weight:800;font-size:1.35rem;color:#1A1A1A;letter-spacing:-0.02em"> livelo</span>
    # </div>
    new_content = re.sub(
        r'<div class="funnel-logo">.*?</div>',
        replacement,
        content,
        flags=re.DOTALL
    )
    
    # Also look for any other places with Livelo text
    new_content = re.sub(
        r'<div style="text-align:center;margin-bottom:28px">\s*<span style="color:#E5147A;font-size:2rem;line-height:1">&#9670;</span>\s*<span style="font-family:Inter,sans-serif;font-weight:800;font-size:2rem;color:#1A1A1A;letter-spacing:-0.03em"> livelo</span>\s*</div>',
        r'''<div style="text-align:center;margin-bottom:28px">
      <img class="sys-logo" src="{{ sys_config.get('system_logo', '/static/images/logo.png') }}" alt="Logo" style="height:64px; max-width:100%; object-fit:contain; display:inline-block;">
    </div>''',
        new_content,
        flags=re.DOTALL
    )

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Replaced funnel-logo in {file_path}")
