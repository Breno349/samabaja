from flask_login import UserMixin # Import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash # Keep these for reference
# Import db and bcrypt from extensions
from src.extensions import db, bcrypt 
import enum

# Removed db = SQLAlchemy() as it's now in extensions.py

class UserRole(enum.Enum):
    GESTAO = 'Gestão'      # Admin
    GERENTE = 'Gerente'     # Sub-admin
    MEMBRO = 'Membro'      # Member
    PENDING = 'Solicitado'    # Newly registered, awaiting approval/role assignment

class UserSector(enum.Enum):
    GESTAO = 'Gestão'
    SUSPENSAO_DIRECAO = 'Suspensão e Direção'
    POWERTRAIN = 'PowerTrain'
    MARKETING = 'Marketing'
    DESIGN_ESTRUTURAS = 'Design e Estruturas'
    FREIO_RODAS = 'Freio e Rodas'
    ELETRICA = 'Elétrica'
    CALCULO_ESTRUTURAL = 'Calculo Estrutural'
    NONE = 'visitante' # For pending users or those not assigned yet

# Add UserMixin for Flask-Login compatibility
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False) # Bcrypt hash is typically 60 chars
    role = db.Column(db.Enum(UserRole), default=UserRole.PENDING, nullable=False)
    sector = db.Column(db.Enum(UserSector), default=UserSector.NONE, nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False) # Add is_active for Flask-Login, default to False until approved
    
    # Horários personalizados por usuário (em formato JSON)
    # Exemplo: {"segunda": {"inicio": "08:00", "fim": "17:00"}, "terca": {"inicio": "08:00", "fim": "17:00"}, ...}
    # Se vazio, o usuário não tem horário definido
    work_schedule = db.Column(db.Text, default='{}', nullable=False)
    
    # Total de horas trabalhadas (em minutos)
    total_hours_worked = db.Column(db.Integer, default=0, nullable=False)
    
    # Banco de horas (em minutos) - positivo = a receber, negativo = a descontar
    bank_of_hours = db.Column(db.Integer, default=0, nullable=False)
    
    # Foto de perfil (caminho relativo)
    profile_picture = db.Column(db.String(255), default=None, nullable=True)

    def __repr__(self):
        return f'<User {self.username} ({self.role.value})>'

    # Password hashing and checking methods using bcrypt
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    # Flask-Login required properties/methods are handled by UserMixin and the fields

    # Activate user method (for admin approval)
    def activate_user(self):
        self.is_active = True
        if self.role == UserRole.PENDING: # Assign a default role if still pending
             self.role = UserRole.MEMBRO # Or another default

    def get_work_schedule(self):
        """Retorna o horário de trabalho como dicionário."""
        import json
        try:
            return json.loads(self.work_schedule) if self.work_schedule else {}
        except:
            return {}
    
    def set_work_schedule(self, schedule_dict):
        """Define o horário de trabalho a partir de um dicionário."""
        import json
        self.work_schedule = json.dumps(schedule_dict)
    
    def get_today_schedule(self):
        """Retorna o horário de trabalho de hoje (se definido)."""
        from datetime import datetime
        days_pt = {
            0: 'segunda',
            1: 'terca',
            2: 'quarta',
            3: 'quinta',
            4: 'sexta',
            5: 'sabado',
            6: 'domingo'
        }
        today = days_pt.get(datetime.now().weekday(), None)
        schedule = self.get_work_schedule()
        return schedule.get(today) if today else None
    
    def format_hours(self, minutes):
        """Formata minutos em formato HhMm."""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m"
    
    def get_weekly_hours(self):
        """Calcula o total de horas esperadas na semana (soma de todos os intervalos)."""
        schedule = self.get_work_schedule()
        total_minutes = 0
        
        for day, times in schedule.items():
            if times and 'inicio' in times and 'fim' in times:
                try:
                    start = times['inicio'].split(':')
                    end = times['fim'].split(':')
                    
                    start_minutes = int(start[0]) * 60 + int(start[1])
                    end_minutes = int(end[0]) * 60 + int(end[1])
                    
                    duration = end_minutes - start_minutes
                    if duration > 0:
                        total_minutes += duration
                except:
                    pass
        
        return total_minutes

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'sector': self.sector.value,
            'is_active': self.is_active,
            'work_schedule': self.get_work_schedule(),
            'total_hours_worked': self.total_hours_worked,
            'bank_of_hours': self.bank_of_hours,
            'profile_picture': self.profile_picture,
            'weekly_hours': self.get_weekly_hours()
        }

