from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
# Import db from extensions
from src.extensions import db
from src.models.user import UserRole
from src.models.document import Document # Import Document model
import markdown # Import markdown library

docs_bp = Blueprint("docs", __name__)

# Helper function to check edit permissions (example: creator or admin)
def can_edit_doc(document):
    # Ensure current_user is authenticated before accessing attributes
    if not current_user.is_authenticated:
        return False
    return current_user.id == document.creator_id or current_user.role == UserRole.GESTAO

@docs_bp.route("/")
@login_required
def list_documents():
    documents = Document.query.order_by(Document.updated_at.desc()).all()
    # Pass the helper function to the template context if needed directly in template
    return render_template("docs/list.html", documents=documents, can_edit_doc=can_edit_doc)

@docs_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_document():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content") # Store as Markdown

        if not title:
            flash("O título do documento é obrigatório.", "danger")
            return render_template("docs/form.html", title=title, content=content)

        new_doc = Document(title=title, content=content, creator_id=current_user.id)
        db.session.add(new_doc)
        db.session.commit()
        flash("Documento criado com sucesso!", "success")
        return redirect(url_for("docs.view_document", doc_id=new_doc.id))

    return render_template("docs/form.html")

@docs_bp.route("/<int:doc_id>")
@login_required
def view_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    html_content = markdown.markdown(doc.content) if doc.content else ""
    return render_template("docs/view.html", doc=doc, html_content=html_content, can_edit=can_edit_doc(doc))

@docs_bp.route("/<int:doc_id>/edit", methods=["GET", "POST"])
@login_required
def edit_document(doc_id):
    doc = Document.query.get_or_404(doc_id)

    if not can_edit_doc(doc):
        flash("Você não tem permissão para editar este documento.", "danger")
        return redirect(url_for("docs.view_document", doc_id=doc.id))

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")

        if not title:
            flash("O título do documento é obrigatório.", "danger")
            # Pass current content back to form
            return render_template("docs/form.html", doc=doc, title=title, content=content)

        doc.title = title
        doc.content = content
        doc.last_editor_id = current_user.id
        # updated_at is handled by onupdate
        db.session.commit()
        flash("Documento atualizado com sucesso!", "success")
        return redirect(url_for("docs.view_document", doc_id=doc.id))

    # Pass existing data to form
    return render_template("docs/form.html", doc=doc, title=doc.title, content=doc.content)

# Add route for deleting documents later if needed, with permission checks

