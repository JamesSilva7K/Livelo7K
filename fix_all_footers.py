from bs4 import BeautifulSoup
import os

files_to_fix = [
    r'd:\Paginas ADS\Livelo\templates\index.html',
    r'd:\Paginas ADS\Livelo\mod_livelo.py',
    r'd:\Paginas ADS\Livelo\mod_livelo2.py',
    r'd:\Paginas ADS\Livelo\mod_frete.py'
]

footer_html = """
<footer class="funnel-footer">
  <p>{{ sys_config.get('system_name', 'Livelo') }} | CNPJ: {{ sys_config.get('system_cnpj', '12.888.241/0001-06') }}</p>
  <p>{{ sys_config.get('system_address', 'Alameda Xingu, 512 &middot; Alphaville, Barueri, SP') }}</p>
  <p>&copy; 2025 &middot; Todos os direitos reservados</p>
</footer>
"""

for path in files_to_fix:
    if not os.path.exists(path):
        continue
        
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove existing footers
    for footer in soup.find_all('footer'):
        footer.decompose()
        
    # Find all screens
    screens = soup.find_all('div', class_=lambda c: c and ('screen' in c or 'splash-screen' in c))
    
    for screen in screens:
        # First child div is the container
        container = screen.find('div', recursive=False)
        if container:
            # Append footer
            footer_soup = BeautifulSoup(footer_html, 'html.parser')
            container.append(footer_soup)
            
    # Write back
    with open(path, 'w', encoding='utf-8') as f:
        # Avoid bs4 HTML escaping replacing {{ }} using formatter=None
        # Wait, bs4 formatter=None might mess up self-closing tags. 
        # html5lib is safer or standard output. 
        f.write(str(soup))
        
    print(f"Fixed footers in {path}")
