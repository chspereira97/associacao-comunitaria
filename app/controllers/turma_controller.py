from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models.projeto import Projeto
from app.models.turma import Turma
from app.models.usuario import Usuario
from app.models.frequencia import Frequencia
from app.models.matricula import Matricula

# ============================================
# ROTAS DE PROJETOS
# ============================================

@app.route('/projetos')
def listar_projetos():
    projetos = Projeto.query.order_by(Projeto.nome).all()
    return render_template('turmas/projetos.html', projetos=projetos)

@app.route('/projetos/cadastrar', methods=['GET', 'POST'])
def cadastrar_projeto():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        descricao = request.form.get('descricao', '').strip()
        
        if not nome:
            flash('Nome do projeto é obrigatório!', 'danger')
            return redirect(url_for('cadastrar_projeto'))
        if Projeto.query.filter_by(nome=nome).first():
            flash('Já existe um projeto com este nome!', 'danger')
            return redirect(url_for('cadastrar_projeto'))
        
        projeto = Projeto(nome=nome, descricao=descricao if descricao else None)
        db.session.add(projeto)
        db.session.commit()
        flash(f'✅ Projeto {nome} cadastrado!', 'success')
        return redirect(url_for('listar_projetos'))
    
    return render_template('turmas/cadastrar_projeto.html')

@app.route('/projetos/editar/<int:id>', methods=['GET', 'POST'])
def editar_projeto(id):
    projeto = Projeto.query.get_or_404(id)
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        descricao = request.form.get('descricao', '').strip()
        
        if not nome:
            flash('Nome do projeto é obrigatório!', 'danger')
            return redirect(url_for('editar_projeto', id=id))
        
        existente = Projeto.query.filter(Projeto.nome == nome, Projeto.id != id).first()
        if existente:
            flash('Já existe outro projeto com este nome!', 'danger')
            return redirect(url_for('editar_projeto', id=id))
        
        projeto.nome = nome
        projeto.descricao = descricao if descricao else None
        projeto.ativo = request.form.get('ativo') == 'on'
        db.session.commit()
        flash(f'✅ Projeto {nome} atualizado!', 'success')
        return redirect(url_for('listar_projetos'))
    
    return render_template('turmas/editar_projeto.html', projeto=projeto)

@app.route('/projetos/deletar/<int:id>')
def deletar_projeto(id):
    projeto = Projeto.query.get_or_404(id)
    nome = projeto.nome
    
    turmas_vinculadas = Turma.query.filter_by(projeto_id=id).count()
    if turmas_vinculadas > 0:
        flash(f'⚠️ Não é possível excluir "{nome}". Existem {turmas_vinculadas} turma(s) vinculada(s).', 'danger')
        return redirect(url_for('listar_projetos'))
    
    db.session.delete(projeto)
    db.session.commit()
    flash(f'🗑️ Projeto {nome} removido!', 'warning')
    return redirect(url_for('listar_projetos'))

# ============================================
# ROTAS DE TURMAS
# ============================================

@app.route('/turmas')
def listar_turmas():
    turmas = Turma.query.order_by(Turma.projeto_id, Turma.nome).all()
    return render_template('turmas/listar.html', turmas=turmas)

@app.route('/turmas/cadastrar', methods=['GET', 'POST'])
def cadastrar_turma():
    projetos = Projeto.query.filter_by(ativo=True).order_by(Projeto.nome).all()
    professores = Usuario.query.filter_by(perfil='professor', ativo=True).order_by(Usuario.nome).all()
    
    if request.method == 'POST':
        projeto_id = request.form.get('projeto_id', '')
        nome = request.form.get('nome', '').strip()
        horario = request.form.get('horario', '').strip()
        dia_semana = request.form.get('dia_semana', '').strip()
        professor_texto = request.form.get('professor', '').strip()
        capacidade_maxima = request.form.get('capacidade_maxima', '')
        professores_selecionados = request.form.getlist('professores')
        
        erros = []
        if not projeto_id:
            erros.append('Selecione um projeto!')
        if not nome:
            erros.append('Nome da turma é obrigatório!')
        if capacidade_maxima:
            try:
                capacidade_maxima = int(capacidade_maxima)
                if capacidade_maxima < 1:
                    erros.append('Capacidade deve ser pelo menos 1!')
            except ValueError:
                erros.append('Capacidade inválida!')
        else:
            capacidade_maxima = 20
        
        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('turmas/cadastrar.html', projetos=projetos, professores=professores,
                                 valores={'nome': nome, 'horario': horario, 'dia_semana': dia_semana,
                                         'professor': professor_texto, 'capacidade_maxima': capacidade_maxima})
        
        turma = Turma(projeto_id=int(projeto_id), nome=nome, horario=horario,
                      dia_semana=dia_semana, professor=professor_texto if professor_texto else None,
                      capacidade_maxima=capacidade_maxima)
        db.session.add(turma)
        db.session.flush()
        
        for prof_id in professores_selecionados:
            professor = Usuario.query.get(int(prof_id))
            if professor and not professor.is_admin() and professor not in turma.professores:
                turma.professores.append(professor)
        
        db.session.commit()
        flash(f'✅ Turma {nome} cadastrada!', 'success')
        return redirect(url_for('listar_turmas'))
    
    return render_template('turmas/cadastrar.html', projetos=projetos, professores=professores, valores={})

@app.route('/turmas/editar/<int:id>', methods=['GET', 'POST'])
def editar_turma(id):
    turma = Turma.query.get_or_404(id)
    projetos = Projeto.query.filter_by(ativo=True).order_by(Projeto.nome).all()
    professores = Usuario.query.filter_by(perfil='professor', ativo=True).order_by(Usuario.nome).all()
    
    if request.method == 'POST':
        turma.projeto_id = int(request.form.get('projeto_id'))
        turma.nome = request.form.get('nome', '').strip()
        turma.horario = request.form.get('horario', '').strip()
        turma.dia_semana = request.form.get('dia_semana', '').strip()
        turma.professor = request.form.get('professor', '').strip() or None
        capacidade = request.form.get('capacidade_maxima', '')
        if capacidade:
            try:
                turma.capacidade_maxima = int(capacidade)
            except ValueError:
                flash('Capacidade máxima inválida!', 'danger')
                return redirect(url_for('editar_turma', id=id))
        
        professores_selecionados = set(int(pid) for pid in request.form.getlist('professores'))
        professores_atuais = set(p.id for p in turma.professores)
        
        for prof_id in professores_atuais - professores_selecionados:
            professor = Usuario.query.get(prof_id)
            if professor:
                turma.professores.remove(professor)
        
        for prof_id in professores_selecionados - professores_atuais:
            professor = Usuario.query.get(prof_id)
            if professor and not professor.is_admin() and professor not in turma.professores:
                turma.professores.append(professor)
        
        db.session.commit()
        flash(f'✅ Turma {turma.nome} atualizada!', 'success')
        return redirect(url_for('listar_turmas'))
    
    professores_vinculados_ids = [p.id for p in turma.professores]
    return render_template('turmas/editar.html', turma=turma, projetos=projetos,
                         professores=professores, professores_vinculados_ids=professores_vinculados_ids)

@app.route('/turmas/deletar/<int:id>')
def deletar_turma(id):
    turma = Turma.query.get_or_404(id)
    nome = turma.nome
    
    matriculas = turma.matriculas.all()
    for matricula in matriculas:
        Frequencia.query.filter_by(matricula_id=matricula.id).delete()
    Matricula.query.filter_by(turma_id=id).delete()
    db.session.execute(db.text("DELETE FROM professor_turma WHERE turma_id = :turma_id"), {"turma_id": id})
    db.session.delete(turma)
    db.session.commit()
    
    flash(f'🗑️ Turma {nome} removida com sucesso!', 'warning')
    return redirect(url_for('listar_turmas'))