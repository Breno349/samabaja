from flask import Blueprint, render_template, request, flash, redirect, url_for
# Import db from extensions
from src.extensions import db
from src.models.user import User, UserSector, UserRole # Added UserRole
from src.models.ordem_servico import OrdemServico, OrdemStatus
from datetime import datetime
from flask_login import login_required, current_user

ordem_bp = Blueprint("ordem", __name__)

@ordem_bp.route("/")
@login_required
def listar_ordens():
    if current_user.role == UserRole.GESTAO:
        ordens = OrdemServico.query.order_by(OrdemServico.data_criacao.desc()).all()
    else:
        ordens = OrdemServico.query.filter_by(setor_responsavel=current_user.sector).order_by(OrdemServico.data_criacao.desc()).all()
        
    return render_template("ordens_lista.html", ordens=ordens)

@ordem_bp.route("/nova", methods=["GET", "POST"])
@login_required
def nova_ordem():
    if request.method == "POST":
        criador_id = current_user.id
        setor_str = request.form.get("setor_responsavel")
        try:
            # Use .value for comparison if needed, or directly use Enum member
            setor = UserSector[setor_str] # Assuming form sends the Enum name (e.g., "POWERTRAIN")
        except KeyError:
            flash("Setor inválido selecionado.", "danger")
            setores = [s.name for s in UserSector if s != UserSector.NONE and s != UserSector.GESTAO]
            return render_template("ordem_form.html", setores=setores, form_data=request.form)

        titulo = request.form.get("titulo")
        if not titulo:
            flash("O título da ordem de serviço é obrigatório.", "danger")
            setores = [s.name for s in UserSector if s != UserSector.NONE and s != UserSector.GESTAO]
            return render_template("ordem_form.html", setores=setores, form_data=request.form)
            
        data_prevista = None
        data_prevista_str = request.form.get("data_prevista_conclusao")
        if data_prevista_str:
            try:
                data_prevista = datetime.strptime(data_prevista_str, "%Y-%m-%d").date()
            except ValueError:
                 flash("Formato de data inválido para Data Prevista.", "danger")
                 setores = [s.name for s in UserSector if s != UserSector.NONE and s != UserSector.GESTAO]
                 return render_template("ordem_form.html", setores=setores, form_data=request.form)

        nova = OrdemServico(
            titulo=titulo,
            descricao_resumida=request.form.get("descricao_resumida"),
            descricao_detalhada=request.form.get("descricao_detalhada"),
            setor_responsavel=setor,
            criador_id=criador_id,
            data_prevista_conclusao=data_prevista,
            materiais_necessarios=request.form.get("materiais_necessarios"),
            materiais_indiretos=request.form.get("materiais_indiretos"),
            equipamentos_ferramentas=request.form.get("equipamentos_ferramentas"),
            epis=request.form.get("epis"),
            anexos_link=request.form.get("anexos_link"),
            observacoes=request.form.get("observacoes")
        )
        db.session.add(nova)
        db.session.commit()
        flash("Nova ordem de serviço criada com sucesso!", "success")
        return redirect(url_for("ordem.listar_ordens"))

    setores = [s.name for s in UserSector if s != UserSector.NONE and s != UserSector.GESTAO]
    return render_template("ordem_form.html", setores=setores)

@ordem_bp.route("/<int:ordem_id>")
@login_required
def ver_ordem(ordem_id):
    ordem = OrdemServico.query.get_or_404(ordem_id)
    if current_user.role != UserRole.GESTAO and current_user.sector != ordem.setor_responsavel:
        flash("Você não tem permissão para ver detalhes desta ordem de serviço.", "danger")
        return redirect(url_for("ordem.listar_ordens"))
        
    return render_template("ordem_detalhe.html", ordem=ordem)

# Add routes for editing and updating status later, with permission checks

