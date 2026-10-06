import re

def modernize_admin_ui():
    with open('templates/admin_dashboard.html', 'r', encoding='utf-8') as f:
        html = f.read()

    new_styles = """
    :root {
      --bg-base: #0b0f19; --bg-surface: #111827; --bg-surface-hover: #1f2937;
      --primary: #E5147A; --primary-hover: #be1265;
      --success: #10B981; --warning: #F59E0B; --danger: #EF4444;
      --text-main: #f9fafb; --text-muted: #9ca3af;
      --border: rgba(255, 255, 255, 0.08);
      --glass-bg: rgba(17, 24, 39, 0.7);
      --glass-border: rgba(255, 255, 255, 0.05);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
    body { background-color: var(--bg-base); color: var(--text-main); display: flex; height: 100vh; overflow: hidden; background-image: radial-gradient(circle at top right, rgba(229,20,122,0.05), transparent 400px); }
    
    /* Modern Glass Sidebar */
    .sidebar { width: 280px; background: var(--glass-bg); backdrop-filter: blur(12px); border-right: 1px solid var(--glass-border); display: flex; flex-direction: column; transition: 0.3s; z-index: 10; }
    .sidebar-header { padding: 32px 24px; font-weight: 800; font-size: 1.4rem; color: var(--text-main); border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 12px; letter-spacing: -0.5px; }
    .sidebar-header span { color: var(--primary); }
    .sidebar-nav { flex: 1; padding: 24px 0; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; }
    .nav-item { display: flex; align-items: center; gap: 16px; padding: 14px 24px; color: var(--text-muted); text-decoration: none; font-weight: 600; font-size: 0.95rem; transition: all 0.2s; cursor: pointer; border-left: 3px solid transparent; }
    .nav-item:hover { color: var(--text-main); background: rgba(255,255,255,0.02); }
    .nav-item.active { background: linear-gradient(90deg, rgba(229,20,122,0.1) 0%, transparent 100%); color: var(--primary); border-left: 3px solid var(--primary); }
    
    .main-wrapper { flex: 1; display: flex; flex-direction: column; overflow: hidden; position: relative; }
    
    /* Sleek Topbar */
    .header { height: 80px; padding: 0 40px; background: transparent; border-bottom: 1px solid var(--border); display: flex; align-items: center; justify-content: space-between; backdrop-filter: blur(10px); z-index: 5; }
    .header h1 { font-size: 1.25rem; font-weight: 700; letter-spacing: -0.5px; }
    .user-profile { display: flex; align-items: center; gap: 12px; font-weight: 600; font-size: 0.9rem; }
    .avatar { width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, var(--primary), #ff4d9f); display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; box-shadow: 0 4px 12px rgba(229,20,122,0.3); }
    
    .content-area { flex: 1; padding: 40px; overflow-y: auto; }
    .content-section { display: none; animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
    .content-section.active { display: block; }
    @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
    
    /* Neo-brutal / Premium Cards */
    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; margin-bottom: 40px; }
    .stat-card { background: linear-gradient(145deg, var(--bg-surface), #151e2f); border: 1px solid var(--glass-border); border-radius: 20px; padding: 28px; transition: all 0.3s; position: relative; overflow: hidden; }
    .stat-card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 4px; background: var(--primary); opacity: 0; transition: 0.3s; }
    .stat-card:hover { transform: translateY(-5px); box-shadow: 0 20px 40px -10px rgba(0,0,0,0.5); }
    .stat-card:hover::before { opacity: 1; }
    .stat-value { font-size: 2.5rem; font-weight: 800; color: var(--text-main); margin-top: 12px; letter-spacing: -1px; }
    .stat-label { font-size: 0.85rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; display: flex; align-items: center; gap: 8px; }
    
    /* Config Cards & Forms */
    .section-header { margin-bottom: 32px; }
    .section-header h2 { font-size: 1.8rem; font-weight: 800; margin-bottom: 8px; letter-spacing: -0.5px; }
    .section-header p { color: var(--text-muted); font-size: 1rem; }
    
    .config-card { background: var(--bg-surface); border: 1px solid var(--border); border-radius: 20px; padding: 32px; margin-bottom: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.2); }
    .field-group { margin-bottom: 24px; }
    .field-label { display: block; margin-bottom: 10px; font-size: 0.9rem; font-weight: 600; color: var(--text-main); }
    .field-input { width: 100%; background: #0b0f19; border: 1px solid var(--border); border-radius: 12px; padding: 14px 18px; color: var(--text-main); font-size: 0.95rem; transition: all 0.2s; box-shadow: inset 0 2px 4px rgba(0,0,0,0.2); }
    .field-input:focus { border-color: var(--primary); outline: none; box-shadow: 0 0 0 4px rgba(229,20,122,0.15), inset 0 2px 4px rgba(0,0,0,0.2); }
    
    /* Modern Tables */
    .table-container { background: var(--bg-surface); border: 1px solid var(--border); border-radius: 20px; overflow: hidden; margin-bottom: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
    table { width: 100%; border-collapse: collapse; }
    th { text-align: left; padding: 18px 24px; font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; font-weight: 700; border-bottom: 1px solid var(--border); background: rgba(0,0,0,0.2); letter-spacing: 0.5px; }
    td { padding: 18px 24px; font-size: 0.95rem; border-bottom: 1px solid var(--border); color: var(--text-main); vertical-align: middle; }
    tr:last-child td { border-bottom: none; }
    tr:hover { background: rgba(255,255,255,0.03); }
    
    .badge { padding: 6px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; display: inline-block; }
    .badge-paid { background: rgba(16,185,129,0.15); color: #34d399; }
    .badge-pending { background: rgba(245,158,11,0.15); color: #fbbf24; }
    
    .btn-primary { background: linear-gradient(135deg, var(--primary), #ff4d9f); color: white; border: none; border-radius: 12px; padding: 14px 28px; font-weight: 700; font-size: 0.95rem; cursor: pointer; transition: all 0.3s; box-shadow: 0 4px 15px rgba(229,20,122,0.3); display: inline-flex; align-items: center; justify-content: center; gap: 8px; }
    .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(229,20,122,0.4); }
"""

    html = re.sub(r':root \{.*?\}(?=\s*</style>)', new_styles, html, flags=re.DOTALL)
    
    # Change "Admin Supremo" to "Supreme<span>Admin</span>"
    html = html.replace('<div class="sidebar-header">Admin Supremo</div>', '<div class="sidebar-header">Supreme<span>Admin</span></div>')
    
    with open('templates/admin_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html)

modernize_admin_ui()
print("UI updated to modern SaaS design")
