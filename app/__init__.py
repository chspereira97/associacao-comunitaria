from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'instance', 'sistema.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chave-secreta-temporaria'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from app.models import Aluno, Responsavel, aluno_responsavel, Projeto, Turma, Matricula, Frequencia, Usuario, professor_turma

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

from app import routes