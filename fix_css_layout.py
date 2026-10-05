import re

path = r'd:\Paginas ADS\Livelo\static\css\main.css'
with open(path, 'r', encoding='utf-8') as f:
    css = f.read()

# Fix step-container
css = re.sub(r'\.step-container\s*\{[^}]+\}', r'.step-container { display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 520px; margin: 0 auto; padding: 40px 20px 32px; min-height: 100vh; }', css)

# Fix funnel-page
if '.funnel-page' in css:
    css = re.sub(r'\.funnel-page\s*\{[^}]+\}', r'.funnel-page { display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 480px; margin: 0 auto; padding: 40px 20px 32px; min-height: 100vh; }', css)
else:
    css += "\n.funnel-page { display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 480px; margin: 0 auto; padding: 40px 20px 32px; min-height: 100vh; }"

# Fix welcome-container
if '.welcome-container' in css:
    css = re.sub(r'\.welcome-container\s*\{[^}]+\}', r'.welcome-container { display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 480px; margin: 0 auto; padding: 40px 20px 32px; min-height: 100vh; }', css)
else:
    css += "\n.welcome-container { display: flex; flex-direction: column; align-items: center; width: 100%; max-width: 480px; margin: 0 auto; padding: 40px 20px 32px; min-height: 100vh; }"

# Fix footer jumping
css = re.sub(r'\.funnel-footer\s*\{[^}]+\}', r'.funnel-footer { margin-top: auto; padding: 24px 20px 22px; text-align: center; font-size: 0.72rem; color: #9CA3AF; line-height: 1.9; width: 100%; flex-shrink: 0; }', css)

with open(path, 'w', encoding='utf-8') as f:
    f.write(css)

print("CSS updated for fixed footer!")
