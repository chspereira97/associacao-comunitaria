from app.models.aluno import Aluno
from app.models.responsavel import Responsavel
from app.models.aluno_responsavel import aluno_responsavel
from app.models.projeto import Projeto
from app.models.turma import Turma
from app.models.matricula import Matricula
from app.models.frequencia import Frequencia
from app.models.usuario import Usuario
from app.models.professor_turma import professor_turma

__all__ = [
    'Aluno',
    'Responsavel',
    'aluno_responsavel',
    'Projeto',
    'Turma',
    'Matricula',
    'Frequencia',
    'Usuario',
    'professor_turma'
]