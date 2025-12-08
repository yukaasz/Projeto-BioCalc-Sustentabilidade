"""
app.py - Aplicação principal BioCalc
Versão enxuta e funcional
"""

from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import json
import os

# Criar a aplicação Flask
app = Flask(__name__)
app.secret_key = 'chave_secreta_biocalc'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biocalc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar banco de dados
from database import db, init_db
init_db(app)

# Importar funções de cálculo
from calculos import calcular_intensidade_carbono, calcular_cbios, calcular_nota_eficiencia

# Dados para formulários
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
    """Página principal com formulário"""
    return render_template('index.html',
                         biomassas=BIOMASSAS_DISPONIVEIS,
                         estados=ESTADOS_BRASIL,
                         veiculos=TIPOS_VEICULOS,
                         default_values=VALORES_PADRAO)

@app.route('/calcular', methods=['POST'])
def calcular():
    """Processa o cálculo"""
    
    print("DEBUG: Entrou na função calcular")
    print(f"DEBUG: Método: {request.method}")
    print(f"DEBUG: Dados do formulário: {request.form}")
    
    try:
        # Coletar dados do formulário
        dados = request.form.to_dict()
        
        # Converter valores numéricos
        for key in dados:
            if key not in ['biomassa', 'estado_producao', 'tipo_veiculo_transporte', 
                          'tipo_veiculo_rodoviario', 'metodo_acv', 
                          'combustivel_fossil_substituto', 'co_geracao', 'exportacao']:
                if dados[key] == '':
                    dados[key] = 0
                else:
                    try:
                        dados[key] = float(dados[key])
                    except:
                        pass
        
        # Calcular intensidade de carbono
        resultado_calculo = calcular_intensidade_carbono(dados)
        
        # Calcular nota de eficiência
        intensidade = resultado_calculo.get('intensidade_total_kg_co2eq_mj', 0)
        nota = calcular_nota_eficiencia(intensidade, dados.get('combustivel_fossil_substituto', 'media_ponderada'))
        
        # Calcular CBIOs
        volume = dados.get('volume_producao_ton_cbios', 12000)
        cbios = calcular_cbios(intensidade, volume, dados.get('biomassa', 'casca_amendoim'))
        
        # Salvar no banco de dados
        from database import Calculo
        calculo = Calculo(
            usuario='anonimo',
            dados_entrada=json.dumps(dados),
            resultados=json.dumps({
                'intensidade_carbono_g': resultado_calculo.get('intensidade_total_g_co2eq_mj', 0),
                'cbios': cbios,
                'nota_eficiencia': nota
            }),
            metodo_acv=dados.get('metodo_acv', 'IPCC'),
            biomassa=dados.get('biomassa', '')
        )
        db.session.add(calculo)
        db.session.commit()
        
        # Preparar dados para template
        resultados_template = {
            'intensidade_carbono': f"{resultado_calculo.get('intensidade_total_g_co2eq_mj', 0):.2f}",
            'cbios': int(cbios),
            'nota_eficiencia': f"{nota:.2f}" if nota else "0.00",
            'dados_entrada': {
                'biomassa': dados.get('biomassa', ''),
                'quantidade': dados.get('quantidade_biomassa', ''),
                'metodo_acv': dados.get('metodo_acv', 'IPCC')
            }
        }
        
        return render_template('resultados.html', resultados=resultados_template)
        
    except Exception as e:
        print(f"Erro: {e}")
        return render_template('erro.html', 
                             erro="Erro no processamento", 
                             detalhe=str(e))

@app.route('/historico')
def historico():
    """Página de histórico"""
    from database import Calculo
    calculos = Calculo.query.order_by(Calculo.data.desc()).limit(50).all()
    return render_template('historico.html', calculos=calculos, total=len(calculos))

@app.route('/sobre')
def sobre():
    """Página sobre o projeto"""
    return render_template('sobre.html')

@app.template_filter('from_json')
def from_json_filter(value):
    """Filtro para converter JSON em objeto"""
    try:
        return json.loads(value)
    except:
        return {}

if __name__ == '__main__':
    app.run(debug=True, port=5001)