from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()

# UserMixin adiciona métodos padrões
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    nome = db.Column(db.String(100))
    # Relacionamento: Um usuário tem muitos cálculos
    calculos = db.relationship('Calculo', backref='owner', lazy=True)

class Calculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    dados_entrada = db.Column(db.Text)
    resultados = db.Column(db.Text)
    metodo_acv = db.Column(db.String(50))
    biomassa = db.Column(db.String(100))
    
    # Chave estrangeira ligando ao usuário (pode ser nulo se for visitante)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data.strftime('%d/%m/%Y'),
            'biomassa': self.biomassa,
            'metodo': self.metodo_acv,
            'resultados': json.loads(self.resultados) if self.resultados else {}
        }

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return db