import os
import re

files_to_fix = [
    r'd:\Paginas ADS\Livelo\templates\index.html',
    r'd:\Paginas ADS\Livelo\mod_livelo.py',
    r'd:\Paginas ADS\Livelo\mod_livelo2.py',
    r'd:\Paginas ADS\Livelo\mod_frete.py'
]

# Standardize Logo to exact same size and wrapper everywhere
logo_pattern_div = r'<div style="text-align:center;margin-bottom:2[08]px;">\s*<img class="sys-logo" src="\{\{ sys_config\.get\(\'system_logo\', \'/static/images/logo\.png\'\) \}\}" alt="Logo" style="height:(?:48|64)px; max-width:100%; object-fit:contain; display:inline-block;">\s*</div>'

# Or generic regex to match any sys-logo div wrapper
generic_logo_pattern = r'<div[^>]*>\s*<img class="sys-logo"[^>]*>\s*</div>'

standard_logo = r'''<div class="global-logo-wrapper" style="text-align:center; margin-top: 30px; margin-bottom: 30px;">
      <img class="sys-logo" src="{{ sys_config.get('system_logo', '/static/images/logo.png') }}" alt="Logo" style="height: 60px; max-width: 100%; object-fit: contain; display: inline-block;">
    </div>'''

for path in files_to_fix:
    if not os.path.exists(path):
        continue
        
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Replace all logo instances
    new_content = re.sub(generic_logo_pattern, standard_logo, content)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Fixed logos in {path}")
