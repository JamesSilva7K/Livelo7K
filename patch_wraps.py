from pathlib import Path

app_file = Path("app.py")
content = app_file.read_text("utf-8")

if "from functools import wraps" not in content:
    content = content.replace("import os", "import os\nfrom functools import wraps")
    app_file.write_text(content, "utf-8")
    print("Added functools.wraps")
