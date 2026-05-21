from flask import Flask, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from datetime import timedelta
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, '..', 'instance', 'sistema.db'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'chave-padrao-insegura')

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Faça login para acessar esta página.'
login_manager.login_message_category = 'warning'

app.jinja_env.globals['timedelta'] = timedelta

@app.before_request
def require_login():
    public_endpoints = ['login', 'static']
    if not current_user.is_authenticated:
        if request.endpoint not in public_endpoints:
            return redirect(url_for('login'))

from app.models import Aluno, Responsavel, aluno_responsavel, Projeto, Turma, Matricula, Frequencia, Usuario, professor_turma

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

from app import routes
from app.controllers import aluno_controller, responsavel_controller, turma_controller, matricula_controller, frequencia_controller, auth_controller, relatorio_controller