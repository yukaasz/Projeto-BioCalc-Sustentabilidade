"""
app.py - Aplicação principal BioCalc
"""

from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import json

# 🔹 IMPORT correto - SÓ importe o que existe
try:
    from database import init_db, db, Calculo
    print("Imports do database OK!")
except ImportError as e:
    print(f"Erro nos imports: {e}")
    print("Verifique se database.py existe e tem db, init_db, Calculo")
    exit(1)

# Import dos cálculos
try:
    from calculos import calcular_intensidade_carbono, calcular_cbios
    print("Imports dos cálculos OK!")
except ImportError:
    print("calculos.py não encontrado. Criando versão simples...")
    # Cria funções simples se o arquivo não existir
    def calcular_intensidade_carbono(dados):
        return 25.0  # Valor fixo para teste
    
    def calcular_cbios(intensidade, quantidade):
        return intensidade * quantidade * 0.1

# 🔹 CRIAR a app Flask
app = Flask(__name__)
app.secret_key = 'biocalc-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biocalc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 🔹 INICIALIZAR o banco
print("Inicializando banco de dados...")
try:
    init_db(app)
    print("Banco inicializado com sucesso!")
except Exception as e:
    print(f"Erro ao inicializar banco: {e}")

# 🔹 ROTAS
@app.route('/')
def index():
    """Página inicial"""
    return render_template('index.html')

@app.route('/calcular', methods=['POST'])
def calcular():
    """Processa cálculo"""
    try:
        # Coletar dados
        dados = {
            'biomassa': request.form.get('biomassa', 'casca_amendoim'),
            'quantidade': float(request.form.get('quantidade', 100)),
            'transporte_distancia': float(request.form.get('transporte_distancia', 50)),
            'transporte_modal': request.form.get('transporte_modal', 'rodoviario'),
            'energia_eletrica': float(request.form.get('energia_eletrica', 10)),
            'agua_consumo': float(request.form.get('agua_consumo', 5)),
            'metodo_acv': request.form.get('metodo_acv', 'IPCC')
        }
        
        # Calcular
        intensidade = calcular_intensidade_carbono(dados)
        cbios = calcular_cbios(intensidade, dados['quantidade'])
        
        # Resultados
        resultados = {
            'intensidade_carbono': round(intensidade, 2),
            'cbios': round(cbios, 2),
            'dados_entrada': dados,
            'unidades': {
                'intensidade': 'gCO₂eq/MJ',
                'cbios': 'CBIOs/ano'
            }
        }
        
        # Salvar no banco
        novo_calculo = Calculo(
            usuario='usuario_teste',
            dados_entrada=json.dumps(dados),
            resultados=json.dumps(resultados),
            metodo_acv=dados['metodo_acv']
        )
        
        db.session.add(novo_calculo)
        db.session.commit()
        print(f"Cálculo #{novo_calculo.id} salvo no banco!")
        
        # Mostrar resultados
        return render_template('resultados.html', resultados=resultados)
        
    except Exception as e:
        error_msg = f"Erro: {str(e)}"
        print(f"{error_msg}")
        return error_msg, 400

@app.route('/historico')
def historico():
    """Mostra histórico"""
    try:
        calculos = Calculo.query.order_by(Calculo.data.desc()).limit(10).all()
        
        calculos_simples = []
        for c in calculos:
            calculos_simples.append({
                'id': c.id,
                'data': c.data.strftime('%d/%m %H:%M'),
                'biomassa': json.loads(c.dados_entrada)['biomassa'] if c.dados_entrada else 'N/A',
                'metodo': c.metodo_acv
            })
        
        return render_template('historico.html', 
                             calculos=calculos_simples,
                             total=len(calculos))
        
    except Exception as e:
        return f"Erro no histórico: {e}", 500

@app.route('/teste')
def teste():
    """Página de teste"""
    return """
    <h1>BioCalc - Teste</h1>
    <p>Aplicação está funcionando!</p>
    <p><a href="/">Ir para o formulário</a></p>
    <p><a href="/historico">Ver histórico</a></p>
    """

# 🔹 EXECUTAR
if __name__ == '__main__':
    print("\n" + "="*50)
    print("BIO-CALC INICIANDO")
    print("="*50)
    print(f"Banco: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"URL: http://localhost:5000")
    print(f"URL: http://127.0.0.1:5000")
    print("="*50 + "\n")
    
    app.run(debug=True, port=5000)