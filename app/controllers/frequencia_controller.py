from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models.turma import Turma
from app.models.matricula import Matricula
from app.models.frequencia import Frequencia
from datetime import date, datetime, timedelta

@app.route('/turmas/<int:turma_id>/frequencia', methods=['GET', 'POST'])
@app.route('/turmas/<int:turma_id>/frequencia/<string:data_str>', methods=['GET', 'POST'])
def registrar_frequencia(turma_id, data_str=None):
    turma = Turma.query.get_or_404(turma_id)
    
    if data_str:
        try:
            data_aula = datetime.strptime(data_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Data inválida!', 'danger')
            return redirect(url_for('registrar_frequencia', turma_id=turma_id))
    else:
        data_aula = date.today()
    
    matriculas = turma.matriculas.filter_by(status='Ativo').order_by(Matricula.aluno_id).all()
    
    if request.method == 'POST':
        for matricula in matriculas:
            presente_str = request.form.get(f'presente_{matricula.id}')
            presente = presente_str == 'on'
            justificativa = request.form.get(f'justificativa_{matricula.id}', '').strip()
            
            freq_existente = Frequencia.query.filter_by(
                matricula_id=matricula.id, data_aula=data_aula
            ).first()
            
            if freq_existente:
                freq_existente.presente = presente
                freq_existente.justificativa = justificativa if not presente and justificativa else None
            else:
                if not presente and not justificativa:
                    justificativa = "Não justificada"
                freq = Frequencia(
                    matricula_id=matricula.id, data_aula=data_aula,
                    presente=presente,
                    justificativa=justificativa if not presente else None
                )
                db.session.add(freq)
        
        db.session.commit()
        flash(f'✅ Frequência de {data_aula.strftime("%d/%m/%Y")} salva!', 'success')
        return redirect(url_for('historico_frequencia', turma_id=turma_id))
    
    frequencias_existentes = {}
    for matricula in matriculas:
        freq = Frequencia.query.filter_by(matricula_id=matricula.id, data_aula=data_aula).first()
        if freq:
            frequencias_existentes[matricula.id] = freq
    
    return render_template('frequencias/registrar.html',
                         turma=turma, matriculas=matriculas,
                         data_aula=data_aula,
                         frequencias_existentes=frequencias_existentes)

@app.route('/turmas/<int:turma_id>/frequencia/historico')
def historico_frequencia(turma_id):
    turma = Turma.query.get_or_404(turma_id)
    
    datas_aulas = db.session.query(Frequencia.data_aula)\
        .join(Matricula)\
        .filter(Matricula.turma_id == turma_id)\
        .distinct()\
        .order_by(Frequencia.data_aula.desc())\
        .all()
    
    datas = [d[0] for d in datas_aulas]
    
    historico = []
    for data_aula in datas:
        total_matriculas = turma.matriculas.filter_by(status='Ativo').count()
        presentes = db.session.query(Frequencia)\
            .join(Matricula)\
            .filter(Matricula.turma_id == turma_id)\
            .filter(Frequencia.data_aula == data_aula)\
            .filter(Frequencia.presente == True)\
            .count()
        
        historico.append({
            'data': data_aula,
            'presentes': presentes,
            'ausentes': total_matriculas - presentes,
            'total': total_matriculas
        })
    
    return render_template('frequencias/historico.html', turma=turma, historico=historico)

@app.route('/frequencia/editar/<int:frequencia_id>', methods=['GET', 'POST'])
def editar_frequencia(frequencia_id):
    frequencia = Frequencia.query.get_or_404(frequencia_id)
    
    if request.method == 'POST':
        frequencia.presente = request.form.get('presente') == 'on'
        if not frequencia.presente:
            justificativa = request.form.get('justificativa', '').strip()
            frequencia.justificativa = justificativa if justificativa else "Não justificada"
        else:
            frequencia.justificativa = None
        db.session.commit()
        flash('✅ Frequência atualizada!', 'success')
        return redirect(url_for('historico_frequencia', turma_id=frequencia.matricula.turma_id))
    
    return render_template('frequencias/editar.html', frequencia=frequencia)