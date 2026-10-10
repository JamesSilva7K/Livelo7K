from app import app, c7_create_pix
import time

with app.test_request_context():
    res = c7_create_pix(29.90, "Joao Silva", "14887154674", "TEST_" + str(int(time.time())))
    print("PIX GENERATED:", res)
