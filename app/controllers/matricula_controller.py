from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models.aluno import Aluno
from app.models.turma import Turma
from app.models.matricula import Matricula
from datetime import datetime

@app.route('/turmas/<int:turma_id>/matriculas')
def listar_matriculas(turma_id):
    turma = Turma.query.get_or_404(turma_id)
    matriculas = turma.matriculas.all()
    vagas_ocupadas = turma.matriculas.filter_by(status='Ativo').count()
    vagas_disponiveis = turma.capacidade_maxima - vagas_ocupadas
    return render_template('matriculas/listar.html', 
                         turma=turma, matriculas=matriculas,
                         vagas_ocupadas=vagas_ocupadas,
                         vagas_disponiveis=vagas_disponiveis)

@app.route('/turmas/<int:turma_id>/matricular', methods=['GET', 'POST'])
def matricular_aluno(turma_id):
    turma = Turma.query.get_or_404(turma_id)
    
    if request.method == 'POST':
        aluno_id = request.form.get('aluno_id', '')
        status = request.form.get('status', 'Ativo')
        observacoes = request.form.get('observacoes', '').strip()
        
        if not aluno_id:
            flash('Selecione um aluno!', 'danger')
            return redirect(url_for('matricular_aluno', turma_id=turma_id))
        
        aluno = Aluno.query.get_or_404(int(aluno_id))
        
        existente = Matricula.query.filter_by(aluno_id=aluno.id, turma_id=turma.id).first()
        if existente:
            flash(f'⚠️ {aluno.nome} já está matriculado nesta turma!', 'warning')
            return redirect(url_for('matricular_aluno', turma_id=turma_id))
        
        vagas_ocupadas = turma.matriculas.filter_by(status='Ativo').count()
        if vagas_ocupadas >= turma.capacidade_maxima:
            flash('❌ Turma lotada! Não há vagas disponíveis.', 'danger')
            return redirect(url_for('matricular_aluno', turma_id=turma_id))
        
        matricula = Matricula(
            aluno_id=aluno.id, turma_id=turma.id, status=status,
            observacoes=observacoes if observacoes else None
        )
        db.session.add(matricula)
        db.session.commit()
        flash(f'✅ {aluno.nome} matriculado com sucesso!', 'success')
        return redirect(url_for('listar_matriculas', turma_id=turma_id))
    
    alunos_matriculados_ids = [m.aluno_id for m in turma.matriculas.all()]
    alunos_disponiveis = Aluno.query.filter(~Aluno.id.in_(alunos_matriculados_ids)).order_by(Aluno.nome).all()
    return render_template('matriculas/matricular.html', turma=turma, alunos=alunos_disponiveis, valores={})

@app.route('/matriculas/editar/<int:id>', methods=['GET', 'POST'])
def editar_matricula(id):
    matricula = Matricula.query.get_or_404(id)
    
    if request.method == 'POST':
        matricula.status = request.form.get('status', 'Ativo')
        matricula.observacoes = request.form.get('observacoes', '').strip() or None
        db.session.commit()
        flash('✅ Matrícula atualizada!', 'success')
        return redirect(url_for('listar_matriculas', turma_id=matricula.turma_id))
    
    return render_template('matriculas/editar.html', matricula=matricula)

@app.route('/matriculas/deletar/<int:id>')
def deletar_matricula(id):
    matricula = Matricula.query.get_or_404(id)
    turma_id = matricula.turma_id
    
    if matricula.aluno is not None:
        aluno_nome = matricula.aluno.nome
    else:
        aluno_nome = "Aluno (não encontrado)"
    
    db.session.delete(matricula)
    db.session.commit()
    flash(f'🗑️ Matrícula de {aluno_nome} removida!', 'warning')
    return redirect(url_for('listar_matriculas', turma_id=turma_id))