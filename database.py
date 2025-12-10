"""
database.py - Configuração do banco de dados
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Calculo(db.Model):
    """Modelo para armazenar cálculos"""
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100), default='Visitante')
    data = db.Column(db.DateTime, default=datetime.utcnow)
    # Armazenaremos os JSONs como TEXT para compatibilidade com SQLite
    dados_entrada = db.Column(db.Text) 
    resultados = db.Column(db.Text)
    metodo_acv = db.Column(db.String(50))
    biomassa = db.Column(db.String(100))
    
    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data.strftime('%d/%m/%Y'),
            'biomassa': self.biomassa,
            'metodo': self.metodo_acv,
            'resultados': json.loads(self.resultados) if self.resultados else {}
        }

def init_db(app):
    """Inicializa o banco de dados"""
    db.init_app(app)
    with app.app_context():
        # Cria as tabelas se não existirem
        db.create_all()
    return db