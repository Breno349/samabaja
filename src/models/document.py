from datetime import datetime
from src.models.user import db, User # Import db instance and User for relationships

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=True) # Store content as Markdown or plain text
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    last_editor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Optional: Add sector or project relationship later
    # sector = db.Column(db.Enum(UserSector), nullable=True)

    # Relationships
    creator = db.relationship("User", foreign_keys=[creator_id], backref=db.backref("created_documents", lazy=True))
    last_editor = db.relationship("User", foreign_keys=[last_editor_id], backref=db.backref("edited_documents", lazy=True))

    def __repr__(self):
        return f"<Document {self.id}: {self.title}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "creator_id": self.creator_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            # Content might be too large for a simple dict representation
        }

