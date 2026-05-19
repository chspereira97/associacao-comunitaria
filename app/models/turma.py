from app import db
from datetime import datetime

class Turma(db.Model):
    __tablename__ = 'turmas'
    
    id = db.Column(db.Integer, primary_key=True)
    projeto_id = db.Column(db.Integer, db.ForeignKey('projetos.id'), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    horario = db.Column(db.String(100))
    dia_semana = db.Column(db.String(100))
    professor = db.Column(db.String(100))
    capacidade_maxima = db.Column(db.Integer, default=20)
    ativa = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    projeto = db.relationship('Projeto', backref=db.backref('turmas', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Turma {self.nome}>'