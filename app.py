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
    
# --- CONFIGURAÇÕES DO BANCO DE DADOS ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biocalc.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chave-super-secreta-biocalc'

# Inicializa o banco de dados com a aplicação Flask
init_db(app)

# --- CONFIGURAÇÃO DO SISTEMA DE LOGIN ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- TIPOS DE BIOMASSA DISPONÍVEIS PARA CÁLCULO ---
BIOMASSAS_DISPONIVEIS = [
    {'id': 'residuo_pinus', 'nome': 'Resíduo de Pinus'},
    {'id': 'residuo_eucaliptus', 'nome': 'Resíduo de Eucaliptus'},
    {'id': 'casca_amendoim', 'nome': 'Casca de Amendoim'},
    {'id': 'eucaliptus_virgem', 'nome': 'Eucalipto (Plantio Dedicado)'},
    {'id': 'pinus_virgem', 'nome': 'Pinus (Plantio Dedicado)'}
]

# --- ESTADOS BRASILEIROS ---
ESTADOS_BRASIL = [
    'Acre',
    'Alagoas',
    'Amapá',
    'Amazonas',
    'Bahia',
    'Ceará',
    'Distrito Federal',
    'Espírito Santo',
    'Goiás',
    'Maranhão',
    'Mato Grosso',
    'Mato Grosso do Sul',
    'Minas Gerais',
    'Pará',
    'Paraíba',
    'Paraná',
    'Pernambuco',
    'Piauí',
    'Rio de Janeiro',
    'Rio Grande do Norte',
    'Rio Grande do Sul',
    'Rondônia',
    'Roraima',
    'Santa Catarina',
    'São Paulo',
    'Sergipe',
    'Tocantins'
]

# --- TIPOS DE VEÍCULOS PARA TRANSPORTE ---
TIPOS_VEICULOS = [
    {'id': 'caminhao_7_5_16t', 'nome': 'Transporte, caminhão 7.5-16t'},
    {'id': 'caminhao_16_32t', 'nome': 'Transporte, caminhão 16-32t'},
    {'id': 'caminhao_maior_32t', 'nome': 'Transporte, caminhão >32t'},
    {'id': 'caminhao_60m3', 'nome': 'Transporte, caminhão 60m³'},
    {'id': 'navio', 'nome': 'Transporte, navio'},
    {'id': 'balsa', 'nome': 'Transporte, balsa'},
    {'id': 'ferroviario', 'nome': 'Transporte, ferroviário'}
]

# --- VALORES PADRÃO PARA FORMULÁRIO ---
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
    # Usuário já logado não pode fazer login novamente
    if current_user.is_authenticated:
        return redirect(url_for('calculadora'))

    if request.method == 'POST':
        # Coleta credenciais do formulário
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Busca usuário no banco de dados
        user = User.query.filter_by(username=username).first()
        
        # Valida credenciais
        if not user or not check_password_hash(user.password_hash, password):
            flash('Usuário ou senha incorretos.')
            return redirect(url_for('login'))
            
        # Cria sessão de login
        login_user(user)
        
        return redirect(url_for('calculadora'))
        
    return render_template('login.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    ROTA DE REGISTRO
    
    GET: Exibe formulário de cadastro
    POST: Cria novo usuário no sistema
    
    Validações:
        - Verifica se username já existe
        - Hash seguro da senha com scrypt
        - Login automático após registro
    """
    # Usuário já logado não pode se registrar
    if current_user.is_authenticated:
        return redirect(url_for('calculadora'))

    if request.method == 'POST':
        # Coleta dados do formulário
        username = request.form.get('username')
        password = request.form.get('password')
        nome = request.form.get('nome')
        
        # Verifica se username já existe
        user_exist = User.query.filter_by(username=username).first()
        if user_exist:
            flash('Nome de usuário já existe!')
            return redirect(url_for('register'))
        
        # Cria novo usuário com senha hasheada
        new_user = User(
            username=username,
            nome=nome,
            password_hash=generate_password_hash(password, method='scrypt')
        )
        
        # Salva no banco de dados
        db.session.add(new_user)
        db.session.commit()
        
        # Login automático após registro
        login_user(new_user)
        return redirect(url_for('calculadora'))
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    """
    ROTA DE LOGOUT
    
    Encerra a sessão do usuário e redireciona para login
    @login_required: Apenas usuários autenticados podem acessar
    """
    logout_user()
    return redirect(url_for('login'))


# ROTAS DA CALCULADORA E CÁLCULOS

@app.route('/calculadora')
@login_required
def calculadora():
    """
    ROTA PRINCIPAL DA CALCULADORA
    
    Renderiza o formulário de entrada de dados com:
        - Tipos de biomassa disponíveis
        - Estados do Brasil
        - Tipos de veículos
        - Valores padrão pré-preenchidos
        - Dados do usuário logado
    
    @login_required: Acesso restrito a usuários autenticados
    """
    return render_template('index.html',
                         biomassas=BIOMASSAS_DISPONIVEIS,
                         estados=ESTADOS_BRASIL,
                         veiculos=TIPOS_VEICULOS,
                         default_values=VALORES_PADRAO,
                         user=current_user)


@app.route('/calcular', methods=['POST'])
@login_required
def calcular():
    """
    ROTA DE PROCESSAMENTO DO CÁLCULO ACV
    
    Fluxo:
        1. Recebe dados do formulário
        2. Executa cálculo de intensidade de carbono
        3. Salva resultado no banco de dados
        4. Exibe página de resultados
    
    Tratamento de erros:
        - Exceções são capturadas e exibidas em página de erro
    
    Returns:
        Template de resultados ou template de erro
    """
    try:
        # Converte FormData em dicionário Python
        dados = request.form.to_dict()
        
        # Executa cálculo ACV (do módulo calculos.py)
        resultado = calcular_intensidade_carbono(dados)

        # Cria novo registro no banco de dados
        novo_calculo = Calculo(
            user_id=current_user.id,
            dados_entrada=json.dumps(dados),      
            resultados=json.dumps(resultado),      
            biomassa=dados.get('biomassa', 'Desconhecida'),
            metodo_acv="RenovaBio"
        )
        db.session.add(novo_calculo)
        db.session.commit()

        # Prepara contexto para renderização
        contexto = {
            'resultados': resultado,
            'inputs': dados,
            'user': current_user
        }
        return render_template('resultados.html', **contexto)

    except Exception as e:
        # Em caso de erro, exibe página de erro com detalhes
        return render_template('erro.html', erro="Erro no cálculo", detalhe=str(e))

# ROTAS DE HISTÓRICO E VISUALIZAÇÃO

@app.route('/historico')
@login_required
def historico():
    # Busca cálculos do usuário ordenados por data decrescente
    calculos = Calculo.query.filter_by(user_id=current_user.id)\
                           .order_by(Calculo.data.desc())\
                           .all()
    
    return render_template('historico.html', calculos=calculos, user=current_user)


@app.route('/detalhes/<int:id>')
@login_required
def detalhes(id):
    # Busca o cálculo pelo ID (404 se não existir)
    calculo = Calculo.query.get_or_404(id)
    
    # VALIDAÇÃO DE SEGURANÇA: Verifica propriedade do cálculo
    if calculo.user_id != current_user.id:
        flash('Acesso negado: Este cálculo não pertence a você.')
        return redirect(url_for('historico'))
    
    # Desserializa dados JSON salvos no banco
    try:
        dados_entrada = json.loads(calculo.dados_entrada)
        resultados = json.loads(calculo.resultados)
        
        # Compatibilidade: Garante que fossil_ref exista (cálculos antigos)
        if 'fossil_ref' not in resultados:
            resultados['fossil_ref'] = 86.7
            
    except Exception as e:
        flash(f'Erro ao ler dados do cálculo: {str(e)}')
        return redirect(url_for('historico'))
    
    # Reutiliza template de resultados com flag de visualização
    contexto = {
        'resultados': resultados,
        'inputs': dados_entrada,
        'user': current_user,
        'modo_visualizacao': True  # Desabilita opções de recálculo
    }
    
    return render_template('resultados.html', **contexto)

# INICIALIZAÇÃO DA APLICAÇÃO
if __name__ == '__main__':
    """
    Ponto de entrada da aplicação
    
    Configurações:
        - debug=True: Ativa modo de desenvolvimento com hot-reload
        - port=5001: Porta customizada (evita conflito com porta 5000)
    
    IMPORTANTE: Em produção, usar servidor WSGI como Gunicorn
    """
    app.run(debug=True, port=5001)