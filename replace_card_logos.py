import os

filepaths = [
    r'd:\Paginas ADS\Livelo\templates\index.html',
    r'd:\Paginas ADS\Livelo\mod_livelo2.py',
    r'd:\Paginas ADS\Livelo\mod_livelo.py',
    r'd:\Paginas ADS\Livelo\mod_frete.py',
]

replacement = '<img src="/static/images/logo-branco.png" style="height:20px; max-width:80px; object-fit:contain; flex-shrink:0; display:block" alt="Livelo">'
replacement2 = '<img src="/static/images/logo-branco.png" style="height:20px; max-width:80px; object-fit:contain" alt="Livelo">'

target1 = '<svg viewBox="0 0 80 22" fill="none" width="64" height="18" style="flex-shrink:0;display:block"><path d="M6 2L2 11l4 9" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><text x="14" y="16" font-family="Inter,sans-serif" font-weight="700" font-size="14" fill="white">livelo</text></svg>'
target2 = '<svg viewBox="0 0 80 22" fill="none" width="64" height="18"><path d="M6 2L2 11l4 9" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><text x="14" y="16" font-family="Inter,sans-serif" font-weight="700" font-size="14" fill="white">livelo</text></svg>'
target3 = '<svg viewBox="0 0 80 22" fill="none" width="62" height="18"><path d="M6 2L2 11l4 9" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/><text x="14" y="16" font-family="Inter,sans-serif" font-weight="700" font-size="14" fill="white">livelo</text></svg>'


for path in filepaths:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        content = content.replace(target1, replacement)
        content = content.replace(target2, replacement2)
        content = content.replace(target3, replacement2)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Replaced logos in {path}")
