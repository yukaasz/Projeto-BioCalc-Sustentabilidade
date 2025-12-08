"""
database.py - Configuração do banco de dados
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Calculo(db.Model):
    """Modelo para armazenar cálculos"""
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100), default='anonimo')
    data = db.Column(db.DateTime, default=datetime.utcnow)
    dados_entrada = db.Column(db.Text)
    resultados = db.Column(db.Text)
    metodo_acv = db.Column(db.String(50), default='IPCC')
    biomassa = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<Calculo {self.id}>'

def init_db(app):
    """Inicializa o banco de dados"""
    db.init_app(app)
    with app.app_context():
        # Verifica se a tabela já existe
        try:
            # Tenta fazer uma consulta simples para ver se a tabela tem a estrutura correta
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = inspector.get_columns('calculo')
            column_names = [col['name'] for col in columns]
            
            if 'biomassa' not in column_names:
                print("⚠️  Estrutura da tabela desatualizada. Recriando...")
                db.drop_all()
                db.create_all()
                print("✅ Tabela recriada com a estrutura correta")
            else:
                print("✅ Estrutura do banco de dados está atualizada")
                
        except Exception as e:
            print(f"⚠️  Erro ao verificar estrutura: {e}")
            print("🔄 Criando banco de dados do zero...")
            db.create_all()
            print("✅ Banco de dados criado com sucesso!")
    
    return db