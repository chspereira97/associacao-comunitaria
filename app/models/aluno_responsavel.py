from app import db
from datetime import datetime

aluno_responsavel = db.Table(
    'aluno_responsavel',
    db.Column('aluno_id', db.Integer, db.ForeignKey('alunos.id'), primary_key=True),
    db.Column('responsavel_id', db.Integer, db.ForeignKey('responsaveis.id'), primary_key=True),
    db.Column('parentesco', db.String(50), nullable=False),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)