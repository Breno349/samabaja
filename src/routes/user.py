from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models.user import User, db
from werkzeug.utils import secure_filename
import os
import json

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users', methods=['POST'])
def create_user():
    
    data = request.json
    user = User(username=data['username'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

# ============ PAINEL DO USUÁRIO ============

@user_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """Exibe o painel do usuário com suas informações, horas e foto."""
    return render_template('user_dashboard.html')

@user_bp.route('/update-schedule', methods=['POST'])
@login_required
def update_schedule():
    """Atualiza o horário de trabalho do usuário."""
    try:
        schedule = {}
        days = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo']
        
        for day in days:
            inicio = request.form.get(f'{day}_inicio')
            fim = request.form.get(f'{day}_fim')
            
            if inicio and fim:
                schedule[day] = {'inicio': inicio, 'fim': fim}
        
        current_user.set_work_schedule(schedule)
        db.session.commit()
        flash('Horário atualizado com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao atualizar horário: {str(e)}', 'danger')
    
    return redirect(url_for('user.dashboard'))

@user_bp.route('/upload-profile-picture', methods=['POST'])
@login_required
def upload_profile_picture():
    """Faz upload da foto de perfil do usuário."""
    try:
        if 'profile_picture' not in request.files:
            flash('Nenhum arquivo selecionado.', 'danger')
            return redirect(url_for('user.dashboard'))
        
        file = request.files['profile_picture']
        
        if file.filename == '':
            flash('Nenhum arquivo selecionado.', 'danger')
            return redirect(url_for('user.dashboard'))
        
        # Verifica se o arquivo é uma imagem
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            flash('Apenas imagens são permitidas (PNG, JPG, JPEG, GIF).', 'danger')
            return redirect(url_for('user.dashboard'))
        
        # Cria o diretório de uploads se não existir
        upload_dir = 'src/static/uploads'
        os.makedirs(upload_dir, exist_ok=True)
        
        # Salva o arquivo com um nome seguro
        filename = secure_filename(f"{current_user.id}_{file.filename}")
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Atualiza o perfil do usuário
        current_user.profile_picture = f'uploads/{filename}'
        db.session.commit()
        
        flash('Foto de perfil atualizada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao fazer upload: {str(e)}', 'danger')
    
    return redirect(url_for('user.dashboard'))

@user_bp.route('/remove-profile-picture', methods=['POST'])
@login_required
def remove_profile_picture():
    """Remove a foto de perfil do usuário."""
    try:
        if current_user.profile_picture:
            # Remove o arquivo do servidor
            filepath = os.path.join('src/static', current_user.profile_picture)
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Atualiza o perfil do usuário
            current_user.profile_picture = None
            db.session.commit()
            
            flash('Foto de perfil removida com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao remover foto: {str(e)}', 'danger')
    
    return redirect(url_for('user.dashboard'))
