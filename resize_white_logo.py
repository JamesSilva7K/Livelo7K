import os

filepaths = [
    r'd:\Paginas ADS\Livelo\templates\index.html',
    r'd:\Paginas ADS\Livelo\mod_livelo2.py',
    r'd:\Paginas ADS\Livelo\mod_livelo.py',
    r'd:\Paginas ADS\Livelo\mod_frete.py',
]

# Increase logo size
target_img = '<img src="/static/images/logo-branco.png" style="height:20px; max-width:80px;'
replacement_img = '<img src="/static/images/logo-branco.png" style="height:32px; max-width:140px;'

# Replace wifi icon with contactless icon
target_svg = '<svg viewBox="0 0 24 24" fill="none" width="18" height="18"><path d="M12 4C7.58 4 4 7.58 4 12s3.58 8 8 8" stroke="rgba(255,255,255,0.7)" stroke-width="1.8" stroke-linecap="round"/><path d="M12 7.5C9.01 7.5 6.5 10.01 6.5 13s2.51 5.5 5.5 5.5" stroke="rgba(255,255,255,0.7)" stroke-width="1.8" stroke-linecap="round"/><path d="M12 11C10.34 11 9 12.34 9 14s1.34 3 3 3" stroke="rgba(255,255,255,0.7)" stroke-width="1.8" stroke-linecap="round"/></svg>'

contactless_svg = '<svg viewBox="0 0 24 24" fill="none" width="24" height="24" style="transform: rotate(90deg);"><path d="M12 4C7.58 4 4 7.58 4 12s3.58 8 8 8" stroke="rgba(255,255,255,0.9)" stroke-width="2.5" stroke-linecap="round"/><path d="M12 7.5C9.01 7.5 6.5 10.01 6.5 13s2.51 5.5 5.5 5.5" stroke="rgba(255,255,255,0.9)" stroke-width="2.5" stroke-linecap="round"/><path d="M12 11C10.34 11 9 12.34 9 14s1.34 3 3 3" stroke="rgba(255,255,255,0.9)" stroke-width="2.5" stroke-linecap="round"/></svg>'

for path in filepaths:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        content = content.replace(target_img, replacement_img)
        content = content.replace(target_svg, contactless_svg)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated sizes and SVG in {path}")
