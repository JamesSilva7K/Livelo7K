import re

def fix_html(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # The dynamic img tag pointing to logo.png
        img_tag = '<img class="sys-logo" src="{{ sys_config.get(\'system_logo\', \'/static/images/logo.png\') }}" alt="Logo" style="height:36px; max-width:100%; object-fit:contain; display:inline-block;">'

        # Regex to find the Livelo SVG
        pattern = re.compile(r'<svg\s+viewBox="0 0 148 40"[\s\S]*?</svg>', re.IGNORECASE)
        
        new_content = pattern.sub(img_tag, content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {filepath}")
    except FileNotFoundError:
        pass

fix_html(r'd:\Paginas ADS\Livelo\templates\index.html')
fix_html(r'd:\Paginas ADS\Livelo\templates\admin_dashboard.html')
fix_html(r'd:\Paginas ADS\Livelo\templates\tg_webapp.html')
