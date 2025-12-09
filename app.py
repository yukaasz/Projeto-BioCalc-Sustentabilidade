from flask import Flask, render_template, request, url_for
import json
from calculos import calcular_intensidade_carbono
from database import db, init_db, Calculo

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biocalc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)

BIOMASSAS_DISPONIVEIS = [
    {'id': 'residuo_pinus', 'nome': 'Resíduo de Pinus'},
    {'id': 'residuo_eucaliptus', 'nome': 'Resíduo de Eucaliptus'},
    {'id': 'casca_amendoim', 'nome': 'Casca de Amendoim'}
]

ESTADOS_BRASIL = [
    'São Paulo', 'Minas Gerais', 'Paraná', 'Rio Grande do Sul',
    'Santa Catarina', 'Rio de Janeiro', 'Bahia', 'Goiás'
]

TIPOS_VEICULOS = [
    {'id': 'caminhao_16_32t', 'nome': 'Caminhão 16-32t'},
    {'id': 'caminhao_32t', 'nome': 'Caminhão >32t'},
    {'id': 'ferroviario', 'nome': 'Ferroviário'},
    {'id': 'balsa', 'nome': 'Balsa/Hidroviário'}
]

VALORES_PADRAO = {
    'quantidade_biomassa': 12000,
    'aproveitamento_biomassa': 1.2,
    'distancia_transporte_biomassa': 100,
    'quantidade_biomassa_processada_kg': 12000000,
    'distancia_mercado_domestico_km': 100,
    'volume_producao_ton_cbios': 12000
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
        dados = request.form.to_dict()
        resultado = calcular_intensidade_carbono(dados)

        novo_calculo = Calculo(
            usuario="Visitante",
            dados_entrada=json.dumps(dados),
            resultados=json.dumps(resultado),
            biomassa=dados.get('biomassa', 'Desconhecida'),
            metodo_acv="RenovaBio"
        )
        db.session.add(novo_calculo)
        db.session.commit()

#Contexto completo para o HTML
        contexto = {
            'resultados': resultado,
            'inputs': dados
        }
        return render_template('resultados.html', **contexto)

    except Exception as e:
        return render_template('erro.html', erro="Erro no cálculo", detalhe=str(e))

@app.route('/historico')
def historico():
    calculos = Calculo.query.order_by(Calculo.data.desc()).limit(20).all()
    return render_template('historico.html', calculos=calculos)

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

if __name__ == 'main':
    app.run(debug=True, port=5001)