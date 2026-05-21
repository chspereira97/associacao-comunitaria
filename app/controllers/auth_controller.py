from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from app.models.usuario import Usuario
from app.models.turma import Turma
from app.models.professor_turma import professor_turma

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        
        usuario = Usuario.query.filter_by(email=email, ativo=True).first()
        
        if usuario and usuario.verificar_senha(senha):
            login_user(usuario, remember=True)
            flash(f'Bem-vindo(a), {usuario.nome}!', 'success')
            if usuario.is_admin():
                return redirect(url_for('index'))
            else:
                return redirect(url_for('professor_turmas'))
        else:
            flash('E-mail ou senha inválidos.', 'danger')
    
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin():
        flash('Acesso negado.', 'danger')
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route('/professor/turmas')
@login_required
def professor_turmas():
    if current_user.is_admin():
        return redirect(url_for('index'))
    
    turmas = Turma.query.join(professor_turma).filter(
        professor_turma.c.usuario_id == current_user.id,
        Turma.ativa == True
    ).order_by(Turma.nome).all()
    
    return render_template('professor/turmas.html', turmas=turmas)

@app.route('/admin/usuarios')
@login_required
def listar_usuarios():
    if not current_user.is_admin():
        flash('Acesso negado.', 'danger')
        return redirect(url_for('index'))
    
    usuarios = Usuario.query.order_by(Usuario.nome).all()
    return render_template('admin/usuarios/listar.html', usuarios=usuarios)

@app.route('/admin/usuarios/cadastrar', methods=['GET', 'POST'])
@login_required
def cadastrar_usuario():
    if not current_user.is_admin():
        flash('Acesso negado.', 'danger')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        perfil = request.form.get('perfil', 'professor')
        
        erros = []
        if not nome:
            erros.append('Nome é obrigatório.')
        if not email:
            erros.append('E-mail é obrigatório.')
        if not senha or len(senha) < 4:
            erros.append('Senha deve ter pelo menos 4 caracteres.')
        if Usuario.query.filter_by(email=email).first():
            erros.append('Este e-mail já está cadastrado.')
        
        if erros:
            for e in erros:
                flash(e, 'danger')
            return render_template('admin/usuarios/cadastrar.html', valores={'nome': nome, 'email': email, 'perfil': perfil})
        
        usuario = Usuario(nome=nome, email=email, perfil=perfil)
        usuario.set_senha(senha)
        db.session.add(usuario)
        db.session.commit()
        flash(f'Usuário {nome} cadastrado!', 'success')
        return redirect(url_for('listar_usuarios'))
    
    return render_template('admin/usuarios/cadastrar.html', valores={})

@app.route('/admin/usuarios/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id):
    if not current_user.is_admin():
        flash('Acesso negado.', 'danger')
        return redirect(url_for('index'))
    
    usuario = Usuario.query.get_or_404(id)
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        perfil = request.form.get('perfil', 'professor')
        ativo = request.form.get('ativo') == 'on'
        
        existente = Usuario.query.filter(Usuario.email == email, Usuario.id != id).first()
        if existente:
            flash('Este e-mail já está cadastrado para outro usuário.', 'danger')
            return render_template('admin/usuarios/editar.html', usuario=usuario)
        
        usuario.nome = nome
        usuario.email = email
        usuario.perfil = perfil
        usuario.ativo = ativo
        
        senha = request.form.get('senha')
        if senha:
            if len(senha) >= 4:
                usuario.set_senha(senha)
            else:
                flash('Senha deve ter pelo menos 4 caracteres.', 'warning')
        
        db.session.commit()
        flash(f'Usuário {nome} atualizado!', 'success')
        return redirect(url_for('listar_usuarios'))
    
    return render_template('admin/usuarios/editar.html', usuario=usuario)

@app.route('/admin/usuarios/deletar/<int:id>')
@login_required
def deletar_usuario(id):
    if not current_user.is_admin():
        flash('Acesso negado.', 'danger')
        return redirect(url_for('index'))
    
    if id == current_user.id:
        flash('Você não pode deletar seu próprio usuário!', 'danger')
        return redirect(url_for('listar_usuarios'))
    
    usuario = Usuario.query.get_or_404(id)
    nome = usuario.nome
    db.session.delete(usuario)
    db.session.commit()
    flash(f'🗑️ Usuário {nome} removido com sucesso!', 'warning')
    return redirect(url_for('listar_usuarios'))