from datetime import datetime
from src.models.user import db, User, UserSector # Import db instance and User/Sector for relationships
import enum

class OrdemStatus(enum.Enum):
    ABERTA = 'Aberta'
    EM_ANDAMENTO = 'Ema Andamento'
    CONCLUIDA = 'Concluida'
    CANCELADA = 'Cancelada'

class OrdemServico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao_resumida = db.Column(db.String(500), nullable=True)
    descricao_detalhada = db.Column(db.Text, nullable=True)
    setor_responsavel = db.Column(db.Enum(UserSector), nullable=False)
    # user_responsavel_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Optional: assign specific user
    criador_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    data_prevista_conclusao = db.Column(db.Date, nullable=True)
    status = db.Column(db.Enum(OrdemStatus), default=OrdemStatus.ABERTA, nullable=False)
    materiais_necessarios = db.Column(db.Text, nullable=True)
    materiais_indiretos = db.Column(db.Text, nullable=True)
    equipamentos_ferramentas = db.Column(db.Text, nullable=True)
    epis = db.Column(db.Text, nullable=True)
    anexos_link = db.Column(db.String(500), nullable=True) # Link to Drive/etc.
    observacoes = db.Column(db.Text, nullable=True)

    # Relationships
    criador = db.relationship('User', foreign_keys=[criador_id], backref=db.backref('ordens_criadas', lazy=True))
    # responsavel = db.relationship('User', foreign_keys=[user_responsavel_id], backref=db.backref('ordens_responsaveis', lazy=True))

    def __repr__(self):
        return f'<OrdemServico {self.id}: {self.titulo}>'

    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descricao_resumida': self.descricao_resumida,
            'setor_responsavel': self.setor_responsavel.value,
            'criador_id': self.criador_id,
            'data_criacao': self.data_criacao.isoformat(),
            'data_prevista_conclusao': self.data_prevista_conclusao.isoformat() if self.data_prevista_conclusao else None,
            'status': self.status.value,
            # Add other fields as needed
        }

