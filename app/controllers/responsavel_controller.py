from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models.aluno import Aluno
from app.models.responsavel import Responsavel
from app.models.aluno_responsavel import aluno_responsavel
from app.utils.validators import validar_email, validar_telefone, validar_cpf

@app.route('/alunos/<int:aluno_id>/responsaveis')
def listar_responsaveis(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    responsaveis = aluno.responsaveis.all()
    return render_template('responsaveis/listar.html', aluno=aluno, responsaveis=responsaveis)

@app.route('/alunos/<int:aluno_id>/responsaveis/adicionar', methods=['GET', 'POST'])
def adicionar_responsavel(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    
    if request.method == 'POST':
        cpf_busca = request.form.get('cpf_busca', '').strip()
        parentesco = request.form.get('parentesco', '').strip()
        
        if cpf_busca:
            cpf_limpo = ''.join(filter(str.isdigit, cpf_busca))
            if len(cpf_limpo) != 11:
                flash('CPF deve ter 11 dígitos!', 'danger')
                return redirect(url_for('adicionar_responsavel', aluno_id=aluno_id))
            
            responsavel = Responsavel.query.filter_by(cpf=cpf_limpo).first()
            if responsavel:
                if aluno.responsaveis.filter_by(id=responsavel.id).first():
                    flash(f'⚠️ {responsavel.nome} já é responsável deste aluno!', 'warning')
                else:
                    db.session.execute(
                        aluno_responsavel.insert().values(
                            aluno_id=aluno_id, responsavel_id=responsavel.id, parentesco=parentesco
                        )
                    )
                    db.session.commit()
                    flash(f'✅ {responsavel.nome} vinculado com sucesso!', 'success')
                return redirect(url_for('listar_responsaveis', aluno_id=aluno_id))
            else:
                flash('Nenhum responsável encontrado com este CPF. Cadastre um novo:', 'info')
                return render_template('responsaveis/adicionar.html', aluno=aluno,
                                     cpf_preenchido=cpf_limpo, parentesco=parentesco, valores={})
        
        nome = request.form.get('nome', '').strip()
        telefone_principal = request.form.get('telefone_principal', '').strip()
        telefone_secundario = request.form.get('telefone_secundario', '').strip()
        email = request.form.get('email', '').strip().lower()
        cpf = request.form.get('cpf', '').strip()
        
        erros = []
        if not nome:
            erros.append("Nome é obrigatório!")
        elif len(nome) < 3:
            erros.append("Nome deve ter pelo menos 3 caracteres!")
        if not telefone_principal:
            erros.append("Telefone principal é obrigatório!")
        elif not validar_telefone(telefone_principal):
            erros.append("Telefone deve ter pelo menos 8 dígitos!")
        if telefone_secundario and not validar_telefone(telefone_secundario):
            erros.append("Telefone secundário inválido!")
        if email and not validar_email(email):
            erros.append("E-mail inválido!")
        if cpf and not validar_cpf(cpf):
            erros.append("CPF deve ter 11 dígitos!")
        
        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('responsaveis/adicionar.html', aluno=aluno, valores={
                'nome': nome, 'telefone_principal': telefone_principal,
                'telefone_secundario': telefone_secundario, 'email': email, 'cpf': cpf
            }, parentesco=parentesco)
        
        cpf_limpo = ''.join(filter(str.isdigit, cpf)) if cpf else None
        if cpf_limpo and Responsavel.query.filter_by(cpf=cpf_limpo).first():
            flash('Já existe um responsável com este CPF!', 'danger')
            return render_template('responsaveis/adicionar.html', aluno=aluno, valores={
                'nome': nome, 'telefone_principal': telefone_principal,
                'telefone_secundario': telefone_secundario, 'email': email, 'cpf': cpf
            }, parentesco=parentesco)
        
        responsavel = Responsavel(
            nome=nome, telefone_principal=telefone_principal,
            telefone_secundario=telefone_secundario if telefone_secundario else None,
            email=email if email else None, cpf=cpf_limpo
        )
        db.session.add(responsavel)
        db.session.flush()
        db.session.execute(
            aluno_responsavel.insert().values(
                aluno_id=aluno_id, responsavel_id=responsavel.id, parentesco=parentesco
            )
        )
        db.session.commit()
        flash(f'✅ {nome} cadastrado e vinculado!', 'success')
        return redirect(url_for('listar_responsaveis', aluno_id=aluno_id))
    
    return render_template('responsaveis/adicionar.html', aluno=aluno, valores={})

@app.route('/responsaveis/editar/<int:id>', methods=['GET', 'POST'])
def editar_responsavel(id):
    responsavel = Responsavel.query.get_or_404(id)
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        telefone_principal = request.form.get('telefone_principal', '').strip()
        telefone_secundario = request.form.get('telefone_secundario', '').strip()
        email = request.form.get('email', '').strip().lower()
        cpf = request.form.get('cpf', '').strip()
        
        erros = []
        if not nome:
            erros.append("Nome é obrigatório!")
        if not telefone_principal:
            erros.append("Telefone principal é obrigatório!")
        if email and not validar_email(email):
            erros.append("E-mail inválido!")
        
        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return redirect(url_for('editar_responsavel', id=id))
        
        responsavel.nome = nome
        responsavel.telefone_principal = telefone_principal
        responsavel.telefone_secundario = telefone_secundario if telefone_secundario else None
        responsavel.email = email if email else None
        if cpf:
            responsavel.cpf = ''.join(filter(str.isdigit, cpf))
        db.session.commit()
        flash(f'✅ Responsável {nome} atualizado!', 'success')
        return redirect(url_for('listar_responsaveis', aluno_id=responsavel.alunos[0].id if responsavel.alunos else None))
    
    return render_template('responsaveis/editar.html', responsavel=responsavel)

@app.route('/alunos/<int:aluno_id>/responsaveis/remover/<int:responsavel_id>')
def remover_vinculo(aluno_id, responsavel_id):
    responsavel = Responsavel.query.get_or_404(responsavel_id)
    db.session.execute(
        aluno_responsavel.delete().where(
            (aluno_responsavel.c.aluno_id == aluno_id) &
            (aluno_responsavel.c.responsavel_id == responsavel_id)
        )
    )
    db.session.commit()
    flash(f'🔗 Vínculo com {responsavel.nome} removido!', 'warning')
    return redirect(url_for('listar_responsaveis', aluno_id=aluno_id))