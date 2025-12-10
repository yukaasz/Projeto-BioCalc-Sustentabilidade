from flask import Flask, render_template, request, jsonify
import json
from calculos import calcular_intensidade_carbono, COMPARADOR_FOSSIL
from database import db, init_db, Calculo

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biocalc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa Banco de Dados
init_db(app)

# --- LISTAS AUXILIARES PARA O TEMPLATE ---
BIOMASSAS_DISPONIVEIS = [
    {'id': 'residuo_pinus', 'nome': 'Resíduo de Pinus'},
    {'id': 'residuo_eucaliptus', 'nome': 'Resíduo de Eucaliptus'},
    {'id': 'casca_amendoim', 'nome': 'Casca de Amendoim'},
    {'id': 'eucaliptus_virgem', 'nome': 'Eucalipto (Plantio Dedicado)'},
    {'id': 'pinus_virgem', 'nome': 'Pinus (Plantio Dedicado)'}
]

ESTADOS_BRASIL = [
    'São Paulo', 'Minas Gerais', 'Paraná', 'Rio Grande do Sul',
    'Santa Catarina', 'Rio de Janeiro', 'Bahia', 'Goiás', 'Mato Grosso', 'Mato Grosso do Sul'
]

TIPOS_VEICULOS = [
    {'id': 'caminhao_16_32t', 'nome': 'Caminhão Médio (16-32t)'},
    {'id': 'caminhao_32t', 'nome': 'Carreta (>32t)'},
    {'id': 'ferroviario', 'nome': 'Trem/Ferroviário'},
    {'id': 'balsa', 'nome': 'Balsa/Hidroviário'}
]

# Valores pré-preenchidos para facilitar o uso (Placeholder)
VALORES_PADRAO = {
    'quantidade_biomassa': 12000,
    'aproveitamento_biomassa': 1.2,
    'distancia_transporte_biomassa': 50,
    'quantidade_biomassa_processada_kg': 10000000,
    'distancia_mercado_domestico_km': 150,
    'volume_producao_ton_cbios': 10000,
    'quantidade_media_transportada_ton': 27
}

@app.route('/')
def index():
    return render_template('index.html',
                         biomassas=BIOMASSAS_DISPONIVEIS,
                         estados=ESTADOS_BRASIL,
                         veiculos=TIPOS_VEICULOS,
                         default_values=VALORES_PADRAO)

@app.route('/calcular', methods=['POST'])
def calcular():
    try:
        # Pega todos os dados do form como dicionário
        dados = request.form.to_dict()
        
        # Executa o cálculo (Backend robusto)
        resultado = calcular_intensidade_carbono(dados)

        # Salva no Banco de Dados
        novo_calculo = Calculo(
            usuario="Visitante",
            dados_entrada=json.dumps(dados),
            resultados=json.dumps(resultado),
            biomassa=dados.get('biomassa', 'Desconhecida'),
            metodo_acv=dados.get('metodo_acv', 'RenovaBio')
        )
        db.session.add(novo_calculo)
        db.session.commit()

        # Prepara contexto para o template de resultados
        contexto = {
            'resultados': resultado,
            'inputs': dados
        }
        return render_template('resultados.html', **contexto)

    except Exception as e:
        # Em produção, use logging. Aqui mostraremos o erro na tela.
        return render_template('erro.html', erro="Ocorreu um erro no cálculo", detalhe=str(e))

@app.route('/historico')
def historico():
    # Busca os últimos 20 cálculos
    calculos_db = Calculo.query.order_by(Calculo.data.desc()).limit(20).all()
    return render_template('historico.html', calculos=calculos_db, total=len(calculos_db))

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/teste')
def teste():
    # Rota atalho para debug rápido
    return render_template('index.html', 
                         biomassas=BIOMASSAS_DISPONIVEIS,
                         estados=ESTADOS_BRASIL,
                         veiculos=TIPOS_VEICULOS,
                         default_values=VALORES_PADRAO)

if __name__ == '__main__':
    app.run(debug=True, port=5001)