from app import db
from datetime import datetime

professor_turma = db.Table(
    'professor_turma',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuarios.id'), primary_key=True),
    db.Column('turma_id', db.Integer, db.ForeignKey('turmas.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)