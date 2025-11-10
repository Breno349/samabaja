from datetime import datetime
from src.models.user import db # Import db instance
import enum

class EntryType(enum.Enum):
    ENTRADA = 'Entrada'          # Clock in
    SAIDA = 'Saida'              # Clock out
    OCORRENCIA = 'Ocorrência'    # Occurrence/incident

class TimeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    # duration = db.Column(db.Interval, nullable=True) # Calculating duration might be better done on retrieval
    description = db.Column(db.Text, nullable=True) # Optional description or task
    
    # Tipo de registro (entrada, saída ou ocorrência)
    entry_type = db.Column(db.Enum(EntryType), default=EntryType.ENTRADA, nullable=False)
    
    # Quem registrou a ocorrência (para ocorrências)
    registered_by_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    
    # Add relationship back to User if needed (already commented out in user.py)
    user = db.relationship("User", backref=db.backref("time_entries", lazy=True), foreign_keys=[user_id])
    registered_by = db.relationship("User", foreign_keys=[registered_by_id], backref=db.backref("registered_occurrences", lazy=True))

    def __repr__(self):
        return f"<TimeEntry {self.id} for User {self.user_id}>"
    
    def get_duration_minutes(self):
        """Retorna a duração em minutos."""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        return 0
    
    def format_duration(self):
        """Formata a duração em formato HhMm."""
        minutes = self.get_duration_minutes()
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "description": self.description,
            "entry_type": self.entry_type.value,
            "registered_by_id": self.registered_by_id,
            "duration_minutes": self.get_duration_minutes()
        }

