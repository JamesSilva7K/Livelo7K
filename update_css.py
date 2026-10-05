import os

css_path = r"d:\Paginas ADS\Livelo\static\css\main.css"

with open(css_path, "r", encoding="utf-8") as f:
    css = f.read()

# Add styles for CEP and Cards
new_css = """
/* ANIMATIONS AND CARD UPGRADES */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.input-field {
  width: 100%;
  padding: 14px 16px;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  font-size: 1rem;
  color: var(--text);
  background: white;
  transition: all 0.2s;
  box-sizing: border-box;
}
.input-field:focus {
  border-color: var(--pink);
  outline: none;
  box-shadow: 0 0 0 4px rgba(229,20,122,0.1);
}
.input-label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 6px;
}

/* More realistic cards */
.credit-card {
  box-shadow: 0 20px 40px -10px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.4);
  overflow: hidden;
  position: relative;
}
.credit-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 10;
  border-radius: 18px;
}

/* Fix Advanced Card Preview Overflow */
.card-scene {
    perspective: 1500px;
    padding: 20px;
    display: flex;
    justify-content: center;
}
.advanced-card-preview {
    transform-style: preserve-3d;
    box-shadow: 0 30px 60px -15px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.4);
    position: relative;
}
"""

if "/* ANIMATIONS AND CARD UPGRADES */" not in css:
    css = css + "\n" + new_css

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css)

print("CSS updated successfully")
