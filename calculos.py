import json

# Fatores de emissão simulados (baseados na planilha original)
FATORES_EMISSAO = {
    'transportes': {
        'rodoviario': 0.162,  # gCO2eq/ton.km
        'ferroviario': 0.022,  # gCO2eq/ton.km
        'hidroviario': 0.015   # gCO2eq/ton.km
    },
    'energia': {
        'eletricidade': 0.082,  # gCO2eq/kWh (média Brasil)
        'diesel': 2.68,         # gCO2eq/L
        'gasolina': 2.31        # gCO2eq/L
    },
    'biomassa': {
        'casca_amendoim': 15.2,
        'residuos_madeira': 12.8,
        'eucalipto': 18.5,
        'pinus': 17.9
    }
}

# Valores de referência
INTENSIDADE_REFERENCIA = 83.8  # gCO2eq/MJ (combustível fóssil de referência)
ENERGIA_ESPECIFICA = 17.5  # MJ/kg (pellets/briquetes)

def calcular_intensidade_carbono(dados):
    """
    Calcula a intensidade de carbono baseado nos dados de entrada
    Simplificado para MVP
    """
    # Componente da biomassa
    fator_biomassa = FATORES_EMISSAO['biomassa'].get(
        dados['biomassa'], 
        15.0  # valor padrão
    )
    
    # Componente do transporte
    fator_transporte = FATORES_EMISSAO['transportes'].get(
        dados['transporte_modal'],
        0.1
    )
    transporte = fator_transporte * dados['transporte_distancia']
    
    # Componente da energia
    energia = dados['energia_eletrica'] * FATORES_EMISSAO['energia']['eletricidade']
    
    # Componente da água (simplificado)
    agua = dados['agua_consumo'] * 0.001
    
    # Intensidade total
    intensidade = fator_biomassa + transporte + energia + agua
    
    # Ajuste baseado no método ACV
    if dados.get('metodo_acv') == 'CFF':
        intensidade *= 0.7  # Redução estimada para CFF
    elif dados.get('metodo_acv') == 'Zero-Burden':
        intensidade *= 0.5  # Redução estimada para Zero-Burden
    
    return intensidade

def calcular_cbios(intensidade_carbono, quantidade_biomassa):
    """
    Calcula CBIOs baseado na intensidade de carbono
    """
    # CBIOs = (Referência - Intensidade) * Quantidade * Energia Específica
    reducao = INTENSIDADE_REFERENCIA - intensidade_carbono
    
    if reducao <= 0:
        return 0
    
    cbios = reducao * quantidade_biomassa * ENERGIA_ESPECIFICA / 1000  # Convertendo para CBIOs
    return cbios

def validar_dados(dados):
    """Validação básica dos dados de entrada"""
    erros = []
    
    if not dados.get('biomassa'):
        erros.append("Tipo de biomassa não especificado")
    
    if dados.get('quantidade', 0) <= 0:
        erros.append("Quantidade deve ser maior que zero")
    
    if dados.get('transporte_distancia', 0) < 0:
        erros.append("Distância de transporte não pode ser negativa")
    
    return erros