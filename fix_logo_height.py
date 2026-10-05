import os
import re

files_to_fix = [
    r'd:\Paginas ADS\Livelo\templates\index.html',
    r'd:\Paginas ADS\Livelo\mod_livelo.py',
    r'd:\Paginas ADS\Livelo\mod_livelo2.py',
    r'd:\Paginas ADS\Livelo\mod_frete.py'
]

# We want to replace style="height:XXpx;" with style="height:64px;" for any img with class="sys-logo"
for path in files_to_fix:
    if not os.path.exists(path):
        continue
        
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Regex to match the img tag and its style attribute
    # Since we know the exact string pattern inside the style attribute from previous BS4 output:
    # style="height:96px; max-width:100%; object-fit:contain; display:inline-block;"
    # We replace any height:\d+px; with height:64px;
    
    # Let's do a robust sub function
    def repl(m):
        full_tag = m.group(0)
        # replace the height value inside the tag
        new_tag = re.sub(r'height:\d+px;', 'height:96px;', full_tag)
        return new_tag

    new_content = re.sub(r'<img[^>]*class="sys-logo"[^>]*>', repl, content)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Standardized logo height in {path}")
