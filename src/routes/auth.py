from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
# Import db and bcrypt from extensions
from src.extensions import db, bcrypt 
from src.models.user import User, UserRole, UserSector

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home")) # Redirect if already logged in
    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Basic validation (add more robust validation)
        if not username or not email or not password:
            flash("Preencha todos os campos.", "danger")
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Nome de usuário ou email já existe.", "warning")
            return redirect(url_for("auth.register"))

        # Use set_password method which uses bcrypt
        new_user = User(username=username, email=email, role=UserRole.PENDING, sector=UserSector.NONE, is_active=False)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()

        flash("Registro bem-sucedido! Aguarde a aprovação do administrador para fazer login.", "success")
        return redirect(url_for("auth.login")) # Redirect to login page

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home")) # Redirect if already logged in

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False # Add remember me option

        user = User.query.filter_by(username=username).first()

        # Use check_password method which uses bcrypt
        if not user or not user.check_password(password):
            flash("Usuário ou senha inválidos.", "danger")
            return redirect(url_for("auth.login"))

        # Check if user is active (approved by admin)
        if not user.is_active:
             flash("Sua conta ainda não foi aprovada por um administrador ou está inativa.", "warning")
             return redirect(url_for("auth.login"))

        # Log user in using Flask-Login
        login_user(user, remember=remember)
        flash("Login bem-sucedido!", "success")
        # Redirect to next page if available, otherwise home
        next_page = request.args.get("next")
        return redirect(next_page) if next_page else redirect(url_for("main.home"))

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required # Ensure user is logged in to log out
def logout():
    logout_user() # Log user out using Flask-Login
    flash("Logout bem-sucedido!", "info")
    return redirect(url_for("auth.login"))

