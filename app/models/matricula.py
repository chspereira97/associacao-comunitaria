from app import db
from datetime import datetime

class Matricula(db.Model):
    __tablename__ = 'matriculas'
    
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey('turmas.id'), nullable=False)
    data_matricula = db.Column(db.Date, default=datetime.now().date())
    status = db.Column(db.String(20), default='Ativo')
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    aluno = db.relationship('Aluno', backref=db.backref('matriculas', lazy='dynamic'))
    turma = db.relationship('Turma', backref=db.backref('matriculas', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Matricula {self.aluno.nome} - {self.turma.nome}>'