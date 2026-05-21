from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models.aluno import Aluno
from app.utils.validators import validar_email, validar_telefone, validar_data_nascimento
from datetime import datetime

@app.route('/alunos')
def listar_alunos():
    alunos = Aluno.query.order_by(Aluno.nome).all()
    now = datetime.now()
    return render_template('alunos/listar.html', alunos=alunos, now=now)

@app.route('/alunos/cadastrar', methods=['GET', 'POST'])
def cadastrar_aluno():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        dia = request.form.get('dia', '')
        mes = request.form.get('mes', '')
        ano = request.form.get('ano', '')
        sexo = request.form.get('sexo', '')
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip().lower()
        endereco = request.form.get('endereco', '').strip()
        observacoes = request.form.get('observacoes', '').strip()

        erros = []

        if not nome:
            erros.append("O nome do aluno é obrigatório!")
        elif len(nome) < 3:
            erros.append("O nome deve ter pelo menos 3 caracteres!")

        if not dia or not mes or not ano:
            erros.append("A data de nascimento completa é obrigatória!")
        else:
            try:
                valido, resultado = validar_data_nascimento(int(dia), int(mes), int(ano))
                if valido:
                    data_nascimento = resultado
                else:
                    erros.append(resultado)
            except ValueError:
                erros.append("Data de nascimento inválida!")

        if not endereco:
            erros.append("O endereço do aluno é obrigatório!")
        elif len(endereco) < 10:
            erros.append("O endereço deve ter pelo menos 10 caracteres!")

        if email and not validar_email(email):
            erros.append("E-mail inválido! Use o formato: nome@exemplo.com")

        if telefone and not validar_telefone(telefone):
            erros.append("Telefone deve ter pelo menos 8 dígitos!")

        if sexo and sexo not in ['M', 'F']:
            erros.append("Sexo deve ser 'M' (Masculino) ou 'F' (Feminino)!")

        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('alunos/cadastrar.html',
                                 valores={'nome': nome, 'sexo': sexo, 'telefone': telefone,
                                         'email': email, 'endereco': endereco,
                                         'observacoes': observacoes})

        aluno = Aluno(
            nome=nome,
            data_nascimento=data_nascimento,
            sexo=sexo if sexo else None,
            telefone=telefone if telefone else None,
            email=email if email else None,
            endereco=endereco,
            observacoes=observacoes if observacoes else None
        )
        db.session.add(aluno)
        db.session.commit()
        flash(f'✅ Aluno {nome} cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_alunos'))

    return render_template('alunos/cadastrar.html', valores={})

@app.route('/alunos/editar/<int:id>', methods=['GET', 'POST'])
def editar_aluno(id):
    aluno = Aluno.query.get_or_404(id)

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        dia = request.form.get('dia', '')
        mes = request.form.get('mes', '')
        ano = request.form.get('ano', '')
        sexo = request.form.get('sexo', '')
        telefone = request.form.get('telefone', '').strip()
        email = request.form.get('email', '').strip().lower()
        endereco = request.form.get('endereco', '').strip()
        observacoes = request.form.get('observacoes', '').strip()

        erros = []

        if not nome:
            erros.append("O nome do aluno é obrigatório!")
        elif len(nome) < 3:
            erros.append("O nome deve ter pelo menos 3 caracteres!")

        if not dia or not mes or not ano:
            erros.append("A data de nascimento completa é obrigatória!")
        else:
            try:
                valido, resultado = validar_data_nascimento(int(dia), int(mes), int(ano))
                if valido:
                    data_nascimento = resultado
                else:
                    erros.append(resultado)
            except ValueError:
                erros.append("Data de nascimento inválida!")

        if not endereco:
            erros.append("O endereço do aluno é obrigatório!")
        elif len(endereco) < 10:
            erros.append("O endereço deve ter pelo menos 10 caracteres!")

        if email and not validar_email(email):
            erros.append("E-mail inválido!")

        if telefone and not validar_telefone(telefone):
            erros.append("Telefone deve ter pelo menos 8 dígitos!")

        if sexo and sexo not in ['M', 'F']:
            erros.append("Sexo inválido!")

        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return redirect(url_for('editar_aluno', id=id))

        aluno.nome = nome
        aluno.data_nascimento = data_nascimento
        aluno.sexo = sexo if sexo else None
        aluno.telefone = telefone if telefone else None
        aluno.email = email if email else None
        aluno.endereco = endereco
        aluno.observacoes = observacoes if observacoes else None
        db.session.commit()
        flash(f'✅ Aluno {nome} atualizado com sucesso!', 'success')
        return redirect(url_for('listar_alunos'))

    return render_template('alunos/editar.html', aluno=aluno)

@app.route('/alunos/deletar/<int:id>')
def deletar_aluno(id):
    from app.models.matricula import Matricula
    from app.models.frequencia import Frequencia
    from app.models.aluno_responsavel import aluno_responsavel
    
    aluno = Aluno.query.get_or_404(id)
    nome = aluno.nome
    
    # 1. Remover todas as frequências vinculadas às matrículas deste aluno
    matriculas = aluno.matriculas.all()
    for matricula in matriculas:
        Frequencia.query.filter_by(matricula_id=matricula.id).delete()
    
    # 2. Remover todas as matrículas deste aluno
    Matricula.query.filter_by(aluno_id=id).delete()
    
    # 3. Remover todos os vínculos de responsáveis deste aluno
    db.session.execute(
        aluno_responsavel.delete().where(aluno_responsavel.c.aluno_id == id)
    )
    
    # 4. Agora podemos deletar o aluno com segurança
    db.session.delete(aluno)
    db.session.commit()
    
    flash(f'🗑️ Aluno {nome} removido com sucesso!', 'warning')
    return redirect(url_for('listar_alunos'))