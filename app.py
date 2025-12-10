from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json

from calculos import calcular_intensidade_carbono
from database import db, init_db, Calculo, User

app = Flask(__name__)

@app.template_filter('from_json')
def from_json(value):
    """Filtro para converter string JSON em dicionário no template"""
    if not value:
        return {}
    try:
        return json.loads(value)
    except Exception as e:
        return {}
    
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biocalc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chave-super-secreta-biocalc'


init_db(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Se tentar acessar página protegida, joga pra cá

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- DADOS AUXILIARES (Mantidos) ---
BIOMASSAS_DISPONIVEIS = [
    {'id': 'residuo_pinus', 'nome': 'Resíduo de Pinus'},
    {'id': 'residuo_eucaliptus', 'nome': 'Resíduo de Eucaliptus'},
    {'id': 'casca_amendoim', 'nome': 'Casca de Amendoim'},
    {'id': 'eucaliptus_virgem', 'nome': 'Eucalipto (Plantio Dedicado)'},
    {'id': 'pinus_virgem', 'nome': 'Pinus (Plantio Dedicado)'}
]

ESTADOS_BRASIL = ['Acre','Amazonas','Amapá','Pará','Roraima','Rondônia','Tocantins','Alagoas','Bahia','Ceará','Maranhão','Paraíba','Pernambuco','Piauí','Rio Grande do Norte','Sergipe','Distrito Federal','Goiás','Mato Grosso','Mato Grosso do Sul','Espírito Santo','Minas Gerais','Rio de Janeiro','São Paulo','Paraná','Rio Grande do Sul','Santa Catarina']

TIPOS_VEICULOS = [
    {'id': 'caminhao_7_5_16t', 'nome': 'Transporte, caminhão 7.5-16t'},
    {'id': 'caminhao_16_32t', 'nome': 'Transporte, caminhão 16-32t'},
    {'id': 'caminhao_maior_32t', 'nome': 'Transporte, caminhão >32t'},
    {'id': 'caminhao_60m3', 'nome': 'Transporte, caminhão 60m³'},
    {'id': 'navio', 'nome': 'Transporte, navio'},
    {'id': 'balsa', 'nome': 'Transporte, balsa'},
    {'id': 'ferroviario', 'nome': 'Transporte, ferroviário'}
]

VALORES_PADRAO = { 'quantidade_biomassa': 12000, 'aproveitamento_biomassa': 1.2, 'distancia_transporte_biomassa': 100 }

# --- ROTAS DE FLUXO ---

@app.route('/')
def root():
    """Rota Raiz: Decide para onde o usuário vai"""
    if current_user.is_authenticated:
        return redirect(url_for('calculadora'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Se já estiver logado, não deixa fazer login de novo, manda pra calculadora
    if current_user.is_authenticated:
        return redirect(url_for('calculadora'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Usuário ou senha incorretos.')
            return redirect(url_for('login'))
            
        login_user(user)
        # SUCESSO: Vai para a calculadora
        return redirect(url_for('calculadora'))
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('calculadora'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        nome = request.form.get('nome')
        
        user_exist = User.query.filter_by(username=username).first()
        if user_exist:
            flash('Nome de usuário já existe!')
            return redirect(url_for('register'))
            
        new_user = User(
            username=username,
            nome=nome,
            password_hash=generate_password_hash(password, method='scrypt')
        )
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('calculadora'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- APLICAÇÃO PROTEGIDA ---

# Mudamos de '/' para '/calculadora' e adicionamos @login_required
@app.route('/calculadora')
@login_required 
def calculadora():
    return render_template('index.html',
                         biomassas=BIOMASSAS_DISPONIVEIS,
                         estados=ESTADOS_BRASIL,
                         veiculos=TIPOS_VEICULOS,
                         default_values=VALORES_PADRAO,
                         user=current_user)

@app.route('/calcular', methods=['POST'])
@login_required
def calcular():
    try:
        dados = request.form.to_dict()
        resultado = calcular_intensidade_carbono(dados)

        novo_calculo = Calculo(
            user_id=current_user.id,
            dados_entrada=json.dumps(dados),
            resultados=json.dumps(resultado),
            biomassa=dados.get('biomassa', 'Desconhecida'),
            metodo_acv="RenovaBio"
        )
        db.session.add(novo_calculo)
        db.session.commit()

        contexto = {
            'resultados': resultado,
            'inputs': dados,
            'user': current_user
        }
        return render_template('resultados.html', **contexto)

    except Exception as e:
        return render_template('erro.html', erro="Erro no cálculo", detalhe=str(e))

@app.route('/historico')
@login_required
def historico():
    calculos = Calculo.query.filter_by(user_id=current_user.id).order_by(Calculo.data.desc()).all()
    return render_template('historico.html', calculos=calculos, user=current_user)

@app.route('/detalhes/<int:id>')
@login_required
def detalhes(id):
    # Busca o cálculo pelo ID ou dá erro 404 se não existir
    calculo = Calculo.query.get_or_404(id)
    
    # SEGURANÇA: Verifica se o cálculo pertence ao usuário logado
    if calculo.user_id != current_user.id:
        flash('Acesso negado: Este cálculo não pertence a você.')
        return redirect(url_for('historico'))
        
    # Recupera os dados salvos e converte de texto JSON para Dicionário Python
    try:
        dados_entrada = json.loads(calculo.dados_entrada)
        resultados = json.loads(calculo.resultados)
        
        # Garante que o fossil_ref exista (para cálculos antigos)
        if 'fossil_ref' not in resultados:
            resultados['fossil_ref'] = 86.7
            
    except Exception as e:
        flash(f'Erro ao ler dados do cálculo: {str(e)}')
        return redirect(url_for('historico'))
    
    # Reutiliza o template de resultados
    contexto = {
        'resultados': resultados,
        'inputs': dados_entrada,
        'user': current_user,
        'modo_visualizacao': True # Flag opcional caso queira esconder botões no futuro
    }
    
    return render_template('resultados.html', **contexto)

if __name__ == '__main__':
    app.run(debug=True, port=5001)