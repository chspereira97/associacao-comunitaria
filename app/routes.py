from app import app

@app.route('/')
def index():
    return '<h1>🏠 Associação Comunitária</h1><p>Sistema no ar!</p>'