from app import db
from datetime import datetime, date

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
    
    # Relacionamento N:N com Responsavel
    from app.models.aluno_responsavel import aluno_responsavel
    from app.models.responsavel import Responsavel
    responsaveis = db.relationship(
        'Responsavel',
        secondary=aluno_responsavel,
        backref=db.backref('alunos', lazy='dynamic'),
        lazy='dynamic'
    )
    
    @property
    def idade(self):
        """Calcula a idade atual do aluno"""
        hoje = date.today()
        idade = hoje.year - self.data_nascimento.year
        if (hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day):
            idade -= 1
        return idade
    
    def __repr__(self):
        return f'<Aluno {self.nome}>'