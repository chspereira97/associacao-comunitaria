from app import db
from datetime import datetime, date

class Frequencia(db.Model):
    __tablename__ = 'frequencias'
    
    id = db.Column(db.Integer, primary_key=True)
    matricula_id = db.Column(db.Integer, db.ForeignKey('matriculas.id'), nullable=False)
    data_aula = db.Column(db.Date, nullable=False, default=date.today)
    presente = db.Column(db.Boolean, default=False)
    justificativa = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    matricula = db.relationship('Matricula', backref=db.backref('frequencias', lazy='dynamic'))
    
    def __repr__(self):
        status = 'Presente' if self.presente else 'Ausente'
        return f'<Frequencia {self.matricula.aluno.nome} - {self.data_aula} - {status}>'