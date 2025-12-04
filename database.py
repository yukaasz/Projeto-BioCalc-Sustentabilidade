"""
database.py - Configuração completa do banco de dados
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 🔹 1. CRIAR o objeto db PRIMEIRO
db = SQLAlchemy()

# 🔹 2. DEPOIS criar as classes que usam db.Model
class Calculo(db.Model):
    """Modelo simplificado para testes"""
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100))
    data = db.Column(db.DateTime, default=datetime.utcnow)
    dados_entrada = db.Column(db.Text)
    resultados = db.Column(db.Text)
    metodo_acv = db.Column(db.String(50))
    
    def __repr__(self):
        return f'<Calculo {self.id}>'

# 🔹 3. FUNÇÃO para inicializar
def init_db(app):
    """
    Inicializa o banco de dados com a app Flask
    """
    # Conecta o db com a app
    db.init_app(app)
    
    # Cria as tabelas
    with app.app_context():
        db.create_all()
        print("✅ Banco de dados criado: biocalc.db")
        print("✅ Tabelas criadas com sucesso!")
    
    return db

# 🔹 4. Certifique-se que tudo é exportado
__all__ = ['db', 'init_db', 'Calculo']