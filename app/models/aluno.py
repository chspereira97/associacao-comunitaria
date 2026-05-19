from app import db
from datetime import datetime

class Aluno(db.Model):
    __tablename__ = 'alunos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    sexo = db.Column(db.String(1))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    endereco = db.Column(db.Text, nullable=False)
    observacoes = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Aluno {self.nome}>'