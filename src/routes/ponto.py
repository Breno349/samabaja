from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime, time
from flask_login import login_required, current_user
from src.extensions import db
from src.models.user import User, UserRole
from src.models.ponto import TimeEntry, EntryType
from src.models.ordem_servico import OrdemServico, OrdemStatus
import json

ponto_bp = Blueprint("ponto", __name__)

# --- Funções auxiliares ---
def is_within_work_hours(user, check_time=None):
    """Verifica se o usuário está dentro do horário de trabalho definido."""
    if user.role == UserRole.GESTAO:
        return True
    if check_time is None:
        check_time = datetime.now()
    today_schedule = user.get_today_schedule()
    if not today_schedule:
        return True
    try:
        inicio = datetime.strptime(today_schedule.get('inicio', '00:00'), '%H:%M').time()
        fim = datetime.strptime(today_schedule.get('fim', '23:59'), '%H:%M').time()
        current_time = check_time.time()
        return inicio <= current_time <= fim
    except Exception as e:
        print(f"Erro ao validar horário: {e}")
        return True

def get_user_status(user):
    """Retorna o status atual do usuário (trabalhando, fora do horário, etc)."""
    today_schedule = user.get_today_schedule()
    if not today_schedule:
        return {'status': 'sem_horario', 'message': 'Sem horário definido'}
    
    last_entry = TimeEntry.query.filter_by(
        user_id=user.id,
        entry_type=EntryType.ENTRADA
    ).order_by(TimeEntry.start_time.desc()).first()
    
    if last_entry and last_entry.end_time is None:
        return {'status': 'trabalhando', 'message': 'Trabalhando', 'entry_id': last_entry.id}
    else:
        return {'status': 'nao_bateu', 'message': 'Não bateu ponto'}

# --- Rotas ---
@ponto_bp.route("/", methods=["GET", "POST"])
@login_required
def registrar_ponto():
    now_utc = datetime.utcnow()
    now = datetime.now()
    user_id = current_user.id

    if request.method == "POST":
        action = request.form.get("action")
        last_entry = TimeEntry.query.filter_by(
            user_id=user_id,
            entry_type=EntryType.ENTRADA
        ).order_by(TimeEntry.start_time.desc()).first()
        is_clocked_in = last_entry and last_entry.end_time is None

        if action == "clock_in":
            if not is_within_work_hours(current_user, now):
                flash("Você está fora do horário de trabalho definido!", "warning")
            elif is_clocked_in:
                flash("Você já registrou a entrada.", "warning")
            else:
                new_entry = TimeEntry(
                    user_id=user_id,
                    start_time=now_utc,
                    entry_type=EntryType.ENTRADA
                )
                db.session.add(new_entry)
                db.session.commit()
                flash("Ponto de entrada registrado com sucesso!", "success")

        elif action == "clock_out":
            if not is_clocked_in:
                flash("Você não registrou a entrada.", "warning")
            else:
                last_entry.end_time = now_utc
                duration_seconds = (last_entry.end_time - last_entry.start_time).total_seconds()
                duration_minutes = int(duration_seconds // 60)
                current_user.total_hours_worked += duration_minutes

                today_schedule = current_user.get_today_schedule()
                if today_schedule:
                    try:
                        inicio = datetime.strptime(today_schedule.get('inicio', '00:00'), '%H:%M').time()
                        fim = datetime.strptime(today_schedule.get('fim', '23:59'), '%H:%M').time()
                        start_minutes = inicio.hour * 60 + inicio.minute
                        end_minutes = fim.hour * 60 + fim.minute
                        expected_minutes = end_minutes - start_minutes
                        current_user.bank_of_hours = expected_minutes - duration_minutes
                    except:
                        pass

                db.session.commit()
                flash(f"Ponto de saída registrado com sucesso! ({last_entry.format_duration()})", "success")

        elif action == "register_occurrence":
            description = request.form.get("occurrence_description")
            if not description:
                flash("Descrição da ocorrência é obrigatória.", "danger")
            else:
                occurrence = TimeEntry(
                    user_id=user_id,
                    start_time=now_utc,
                    end_time=now_utc,
                    description=description,
                    entry_type=EntryType.OCORRENCIA,
                    registered_by_id=user_id
                )
                db.session.add(occurrence)
                db.session.commit()
                flash("Ocorrência registrada com sucesso!", "success")
        
        return redirect(url_for("ponto.registrar_ponto"))

    time_entries = TimeEntry.query.filter_by(user_id=user_id).order_by(TimeEntry.start_time.desc()).limit(10).all()
    last_entry = TimeEntry.query.filter_by(
        user_id=user_id,
        entry_type=EntryType.ENTRADA
    ).order_by(TimeEntry.start_time.desc()).first()
    is_clocked_in = last_entry and last_entry.end_time is None

    if current_user.role == UserRole.GESTAO:
        open_orders = OrdemServico.query.filter(
            OrdemServico.status != OrdemStatus.CONCLUIDA,
            OrdemServico.status != OrdemStatus.CANCELADA
        ).order_by(OrdemServico.data_criacao.desc()).limit(5).all()
    else:
        open_orders = OrdemServico.query.filter(
            OrdemServico.setor_responsavel == current_user.sector,
            OrdemServico.status != OrdemStatus.CONCLUIDA,
            OrdemServico.status != OrdemStatus.CANCELADA
        ).order_by(OrdemServico.data_criacao.desc()).limit(5).all()

    today_schedule = current_user.get_today_schedule()
    current_time_display = now.strftime("%H:%M:%S")
    all_occurrences = TimeEntry.query.filter_by(
        entry_type=EntryType.OCORRENCIA
    ).order_by(TimeEntry.start_time.desc()).limit(20).all()

    return render_template(
        "ponto.html",
        current_time=current_time_display,
        time_entries=time_entries,
        is_clocked_in=is_clocked_in,
        open_orders=open_orders,
        today_schedule=today_schedule,
        total_hours_worked=current_user.format_hours(current_user.total_hours_worked),
        all_occurrences=all_occurrences
    )

@ponto_bp.route("/set-schedule", methods=["GET", "POST"])
@login_required
def set_schedule():
    """Permite que o usuário defina seu horário de trabalho."""
    if request.method == "POST":
        schedule_data = {}
        days = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo']
        for day in days:
            inicio = request.form.get(f'{day}_inicio')
            fim = request.form.get(f'{day}_fim')
            if inicio and fim:
                schedule_data[day] = {'inicio': inicio, 'fim': fim}
        current_user.set_work_schedule(schedule_data)
        db.session.commit()
        flash("Horário de trabalho atualizado com sucesso!", "success")
        return redirect(url_for("ponto.registrar_ponto"))

    current_schedule = current_user.get_work_schedule()
    days_pt = {
        'segunda': 'Segunda-feira',
        'terca': 'Terça-feira',
        'quarta': 'Quarta-feira',
        'quinta': 'Quinta-feira',
        'sexta': 'Sexta-feira',
        'sabado': 'Sábado',
        'domingo': 'Domingo'
    }
    return render_template("set_schedule.html", current_schedule=current_schedule, days_pt=days_pt)

@ponto_bp.route("/historico")
@login_required
def historico_horas():
    """Exibe o histórico de horas de todos os usuários (apenas Admin)."""
    if current_user.role != UserRole.GESTAO:
        flash("Você não tem permissão para acessar esta página.", "danger")
        return redirect(url_for("main.home"))

    users = User.query.filter_by(is_active=True).all()
    users_data = []
    for user in users:
        status = get_user_status(user)
        today_schedule = user.get_today_schedule()
        users_data.append({
            'user': user,
            'status': status,
            'today_schedule': today_schedule,
            'total_hours': user.format_hours(user.total_hours_worked),
            'weekly_hours': user.format_hours(user.get_weekly_hours()),
            'bank_of_hours': user.format_hours(user.bank_of_hours)
        })

    users_data.sort(key=lambda x: (x['status']['status'] != 'trabalhando', x['user'].username))
    all_occurrences = TimeEntry.query.filter_by(entry_type=EntryType.OCORRENCIA).order_by(TimeEntry.start_time.desc()).all()
    
    return render_template("ponto_historico.html", users_data=users_data, all_occurrences=all_occurrences, admin_view=True)

@ponto_bp.route("/historico-publico")
def historico_publico():
    """Exibe o histórico de horas de todos os usuários (público)."""
    users = User.query.filter_by(is_active=True).all()
    users_data = []
    for user in users:
        status = get_user_status(user)
        today_schedule = user.get_today_schedule()
        users_data.append({
            'user': user,
            'status': status,
            'today_schedule': today_schedule,
            'total_hours': user.format_hours(user.total_hours_worked),
            'weekly_hours': user.format_hours(user.get_weekly_hours()),
            'bank_of_hours': user.format_hours(user.bank_of_hours)
        })

    users_data.sort(key=lambda x: (x['status']['status'] != 'trabalhando', x['user'].username))
    all_occurrences = TimeEntry.query.filter_by(entry_type=EntryType.OCORRENCIA).order_by(TimeEntry.start_time.desc()).all()

    return render_template("ponto_historico.html", users_data=users_data, all_occurrences=all_occurrences, admin_view=False)

@ponto_bp.route("/api/status")
def api_status():
    """API para obter o status atual de todos os usuários (para auto-atualização)."""
    users = User.query.filter_by(is_active=True).all()
    users_status = []
    for user in users:
        status = get_user_status(user)
        today_schedule = user.get_today_schedule()
        users_status.append({
            'user_id': user.id,
            'username': user.username,
            'status': status['status'],
            'message': status['message'],
            'today_schedule': today_schedule,
            'total_hours': user.format_hours(user.total_hours_worked),
            'weekly_hours': user.format_hours(user.get_weekly_hours()),
            'bank_of_hours': user.format_hours(user.bank_of_hours)
        })
    return jsonify(users_status)

@ponto_bp.route("/api/occurrences")
def api_occurrences():
    """API para obter as ocorrências recentes (para auto-atualização)."""
    occurrences = TimeEntry.query.filter_by(entry_type=EntryType.OCORRENCIA).order_by(TimeEntry.start_time.desc()).limit(50).all()
    occurrences_data = []
    for occ in occurrences:
        occurrences_data.append({
            'id': occ.id,
            'user_id': occ.user_id,
            'username': occ.user.username,
            'description': occ.description,
            'start_time': occ.start_time.isoformat(),
            'registered_by': occ.registered_by.username if occ.registered_by else 'Desconhecido'
        })
    return jsonify(occurrences_data)
