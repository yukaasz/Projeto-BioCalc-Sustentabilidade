from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from calculos import calcular_intensidade_carbono, calcular_cbios
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'biocalc-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biocalc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Calculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100))
    data = db.Column(db.DateTime, default=datetime.utcnow)
    dados_entrada = db.Column(db.Text)
    resultados = db.Column(db.Text)
    metodo_acv = db.Column(db.String(50))

@app.route('/')
def index():
    """Página inicial com formulário de entrada de dados"""
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    """Processa os dados e realiza os cálculos"""
    try:
        # Coleta dados do formulário
        dados = {
            'biomassa': request.form.get('biomassa'),
            'quantidade': float(request.form.get('quantidade', 0)),
            'transporte_distancia': float(request.form.get('transporte_distancia', 0)),
            'transporte_modal': request.form.get('transporte_modal'),
            'energia_eletrica': float(request.form.get('energia_eletrica', 0)),
            'agua_consumo': float(request.form.get('agua_consumo', 0)),
            'metodo_acv': request.form.get('metodo_acv', 'IPCC')
        }
        
        # Realiza cálculos
        intensidade_carbono = calcular_intensidade_carbono(dados)
        cbios = calcular_cbios(intensidade_carbono, dados['quantidade'])
        
        # Prepara resultados
        resultados = {
            'intensidade_carbono': round(intensidade_carbono, 2),
            'cbios': round(cbios, 2),
            'dados_entrada': dados,
            'unidades': {
                'intensidade': 'gCO₂eq/MJ',
                'cbios': 'CBIOs/ano'
            }
        }
        
        # Salva no banco de dados (simulado)
        novo_calculo = Calculo(
            usuario='usuario_teste',
            dados_entrada=json.dumps(dados),
            resultados=json.dumps(resultados),
            metodo_acv=dados['metodo_acv']
        )
        db.session.add(novo_calculo)
        db.session.commit()
        
        # Armazena na sessão para mostrar na página de resultados
        session['ultimo_calculo'] = resultados
        
        return render_template('resultados.html', resultados=resultados)
        
    except Exception as e:
        return f"Erro no cálculo: {str(e)}", 400

@app.route('/api/calcular', methods=['POST'])
def api_calcular():
    """API para cálculo (para integração futura)"""
    dados = request.get_json()
    intensidade = calcular_intensidade_carbono(dados)
    cbios = calcular_cbios(intensidade, dados.get('quantidade', 0))
    
    return jsonify({
        'intensidade_carbono': intensidade,
        'cbios': cbios,
        'metodo': dados.get('metodo_acv', 'IPCC')
    })

@app.route('/historico')
def historico():
    """Mostra histórico de cálculos"""
    calculos = Calculo.query.order_by(Calculo.data.desc()).limit(10).all()
    return render_template('historico.html', calculos=calculos)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)