from flask import render_template
from app import app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teste')
def teste():
    return 'Se você está vendo isso, o Flask funciona!'