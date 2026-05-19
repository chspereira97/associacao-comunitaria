from app import db
from datetime import datetime

class Responsavel(db.Model):
    __tablename__ = 'responsaveis'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    telefone_principal = db.Column(db.String(20), nullable=False)
    telefone_secundario = db.Column(db.String(20))
    email = db.Column(db.String(100))
    cpf = db.Column(db.String(14), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Responsavel {self.nome}>'