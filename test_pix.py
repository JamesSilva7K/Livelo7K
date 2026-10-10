import app as flask_app
with flask_app.app.app_context():
    pix = flask_app.c7_create_pix(10.50, 'Joao', '12345678909', 'abcdef123')
    print(pix)
