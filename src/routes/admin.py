from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
# Import db from extensions
from src.extensions import db
from src.models.user import User, UserRole, UserSector
from functools import wraps

admin_bp = Blueprint("admin", __name__)

# Decorator to check for GESTAO role
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.GESTAO:
            flash("Acesso restrito a administradores.", "danger")
            return redirect(url_for("main.home"))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route("/dashboard")
@login_required
@admin_required
def dashboard():
    # Admin dashboard - maybe show pending users, stats, etc.
    pending_users = User.query.filter_by(is_active=False, role=UserRole.PENDING).count()
    return render_template("admin/dashboard.html", pending_users=pending_users)

@admin_bp.route("/users")
@login_required
@admin_required
def manage_users():
    users = User.query.order_by(User.id).all()
    return render_template("admin/manage_users.html", users=users, roles=UserRole, sectors=UserSector)

@admin_bp.route("/users/<int:user_id>/approve", methods=["POST"])
@login_required
@admin_required
def approve_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == UserRole.PENDING:
        user.activate_user() # Sets is_active=True and assigns default role if needed
        db.session.commit()
        flash(f"Usuário {user.username} aprovado e ativado.", "success")
    else:
        flash(f"Usuário {user.username} já estava aprovado.", "info")
    return redirect(url_for("admin.manage_users"))

@admin_bp.route("/users/<int:user_id>/update_role_sector", methods=["POST"])
@login_required
@admin_required
def update_role_sector(user_id):
    user = User.query.get_or_404(user_id)
    new_role_str = request.form.get("role")
    new_sector_str = request.form.get("sector")

    try:
        new_role = UserRole[new_role_str]
        new_sector = UserSector[new_sector_str]

        user.role = new_role
        user.sector = new_sector
        # Ensure user is active if assigning a role other than PENDING
        if new_role != UserRole.PENDING:
            user.is_active = True
            
        db.session.commit()
        flash(f"Cargo e setor do usuário {user.username} atualizados.", "success")
    except KeyError:
        flash("Cargo ou setor inválido selecionado.", "danger")

    return redirect(url_for("admin.manage_users"))

@admin_bp.route("/users/<int:user_id>/toggle_active", methods=["POST"])
@login_required
@admin_required
def toggle_active(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("Você não pode desativar sua própria conta.", "danger")
        return redirect(url_for("admin.manage_users"))
        
    user.is_active = not user.is_active
    db.session.commit()
    status = "ativado" if user.is_active else "desativado"
    flash(f"Usuário {user.username} foi {status}.", "success")
    return redirect(url_for("admin.manage_users"))

