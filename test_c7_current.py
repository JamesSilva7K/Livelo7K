from app import app, c7_create_pix
import traceback

try:
    with app.app_context():
        print("Testing c7_create_pix with User-Agent header...")
        res = c7_create_pix(29.90, "João Silva", "60454669933", "test_pay_123")
        print("Result:", res)
except Exception as e:
    print("Exception:", e)
    traceback.print_exc()
