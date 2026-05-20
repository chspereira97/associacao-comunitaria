from flask import render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user
from app import app, db
from app.models.aluno import Aluno
from app.models.turma import Turma
from app.models.matricula import Matricula
from app.models.frequencia import Frequencia
from app.models.projeto import Projeto
from datetime import datetime, timedelta
import csv
from io import StringIO

@app.route('/relatorios')
@login_required
def dashboard_relatorios():
    if not current_user.is_admin():
        flash('Acesso negado.', 'danger')
        return redirect(url_for('index'))

    total_alunos = Aluno.query.filter_by(ativo=True).count()
    total_turmas = Turma.query.filter_by(ativa=True).count()

    data_30_dias = datetime.now().date() - timedelta(days=30)
    frequencias = Frequencia.query.filter(Frequencia.data_aula >= data_30_dias).all()
    if frequencias:
        total_registros = len(frequencias)
        total_presentes = sum(1 for f in frequencias if f.presente)
        media_frequencia = round((total_presentes / total_registros) * 100, 1)
    else:
        media_frequencia = 0

    alunos_sem_resp = []
    for aluno in Aluno.query.filter_by(ativo=True).all():
        if aluno.idade < 18 and aluno.responsaveis.count() == 0:
            alunos_sem_resp.append(aluno)

    faixas = {'6-10': 0, '11-14': 0, '15-17': 0, '18+': 0}
    for aluno in Aluno.query.filter_by(ativo=True).all():
        idade = aluno.idade
        if 6 <= idade <= 10:
            faixas['6-10'] += 1
        elif 11 <= idade <= 14:
            faixas['11-14'] += 1
        elif 15 <= idade <= 17:
            faixas['15-17'] += 1
        elif idade >= 18:
            faixas['18+'] += 1

    projetos = Projeto.query.filter_by(ativo=True).all()
    projetos_labels = [p.nome for p in projetos]
    projetos_data = []
    for p in projetos:
        count = Matricula.query.join(Turma).filter(Turma.projeto_id == p.id, Matricula.status == 'Ativo').count()
        projetos_data.append(count)

    meses_labels = []
    meses_data = []
    for i in range(5, -1, -1):
        mes_ref = datetime.now().replace(day=1) - timedelta(days=i*30)
        mes_ref = mes_ref.replace(day=1)
        meses_labels.append(mes_ref.strftime('%b/%y'))
        count = Matricula.query.filter(
            db.extract('year', Matricula.data_matricula) == mes_ref.year,
            db.extract('month', Matricula.data_matricula) == mes_ref.month
        ).count()
        meses_data.append(count)

    turmas_baixa_freq = []
    for turma in Turma.query.filter_by(ativa=True).all():
        aulas = db.session.query(Frequencia.data_aula).join(Matricula).filter(
            Matricula.turma_id == turma.id, Frequencia.data_aula >= data_30_dias
        ).distinct().count()
        if aulas > 0:
            presencas = Frequencia.query.join(Matricula).filter(
                Matricula.turma_id == turma.id, Frequencia.data_aula >= data_30_dias, Frequencia.presente == True
            ).count()
            total_matriculas = turma.matriculas.filter_by(status='Ativo').count()
            if total_matriculas > 0:
                percent = round((presencas / (aulas * total_matriculas)) * 100, 1)
                if percent < 70:
                    turmas_baixa_freq.append({'turma': turma, 'percentual': percent, 'aulas': aulas})

    return render_template('relatorios/dashboard.html',
                         total_alunos=total_alunos, total_turmas=total_turmas,
                         media_frequencia=media_frequencia, alunos_sem_resp=alunos_sem_resp,
                         faixas=faixas, projetos_labels=projetos_labels,
                         projetos_data=projetos_data, meses_labels=meses_labels,
                         meses_data=meses_data, turmas_baixa_freq=turmas_baixa_freq)

@app.route('/relatorios/exportar-alunos')
@login_required
def exportar_alunos_csv():
    if not current_user.is_admin():
        flash('Acesso negado.', 'danger')
        return redirect(url_for('index'))

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Nome', 'Data Nascimento', 'Idade', 'Sexo', 'Telefone', 'Email', 'Endereço', 'Ativo'])

    for a in Aluno.query.order_by(Aluno.nome).all():
        cw.writerow([a.id, a.nome, a.data_nascimento.strftime('%d/%m/%Y') if a.data_nascimento else '',
                     a.idade, a.sexo or '', a.telefone or '', a.email or '', a.endereco or '',
                     'Sim' if a.ativo else 'Não'])

    output = si.getvalue().encode('utf-8-sig')
    si.close()
    return Response(output, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=alunos.csv"})