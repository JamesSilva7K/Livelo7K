import os

files_to_check = [
    r'd:\Paginas ADS\Livelo\templates\index.html',
    r'd:\Paginas ADS\Livelo\templates\admin_dashboard.html',
    r'd:\Paginas ADS\Livelo\templates\tg_webapp.html'
]

for filepath in files_to_check:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Increase height from 64px to 96px
        new_content = content.replace('style="height:64px; max-width:100%; object-fit:contain; display:inline-block;"', 
                                      'style="height:96px; max-width:100%; object-fit:contain; display:inline-block;"')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Resized logos to 96px in {filepath}")
    except Exception as e:
        print(f"Error {filepath}: {e}")
