"""
calculos.py - Lógica de cálculo simplificada
"""

def calcular_intensidade_carbono(dados):
    """Calcula intensidade de carbono - versão simplificada"""
    
    # Fatores básicos
    fatores = {
        'casca_amendoim': 15.2,
        'residuos_madeira': 12.8,
        'eucalipto': 18.5,
        'pinus': 17.9
    }
    
    # Valor base da biomassa
    base = fatores.get(dados.get('biomassa'), 15.0)
    
    # Ajuste por transporte
    transporte = {
        'rodoviario': 0.1,
        'ferroviario': 0.05,
        'hidroviario': 0.03
    }
    ajuste_transporte = transporte.get(dados.get('transporte_modal', 'rodoviario'), 0.1)
    
    # Ajuste por método ACV
    if dados.get('metodo_acv') == 'CFF':
        ajuste_metodo = 0.7
    elif dados.get('metodo_acv') == 'Zero-Burden':
        ajuste_metodo = 0.5
    else:
        ajuste_metodo = 1.0
    
    # Cálculo final
    resultado = base * (1 + ajuste_transporte) * ajuste_metodo
    return round(resultado, 2)

def calcular_cbios(intensidade, quantidade):
    """Calcula CBIOs estimados"""
    referencia = 83.8  # Referência fóssil
    
    if intensidade >= referencia:
        return 0
    
    # Fórmula simplificada
    cbios = (referencia - intensidade) * quantidade * 0.175
    return round(cbios, 2)

def validar_dados(dados):
    """Valida dados de entrada"""
    erros = []
    
    if not dados.get('biomassa'):
        erros.append("Selecione um tipo de biomassa")
    
    if dados.get('quantidade', 0) <= 0:
        erros.append("Quantidade deve ser maior que zero")
    
    return erros