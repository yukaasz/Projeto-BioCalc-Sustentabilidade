"""
calculos.py - Cálculos simplificados baseados na planilha
"""

# Fatores de emissão simplificados (kg CO2 eq/MJ)
FATORES_BIOMASSA = {
    'residuo_pinus': 0.012,
    'residuo_eucaliptus': 0.013,
    'casca_amendoim': 0.015,
    'eucaliptus_virgem': 0.014,
    'pinus_virgem': 0.016,
    'carvao_vegetal_eucalipto': 0.025
}

# PCI (MJ/kg)
PCI_BIOMASSA = {
    'residuo_pinus': 18.8,
    'residuo_eucaliptus': 15.8,
    'casca_amendoim': 17.1,
    'eucaliptus_virgem': 15.8,
    'pinus_virgem': 18.8,
    'carvao_vegetal_eucalipto': 18.5
}

# Fatores de transporte (kg CO2 eq/t.km)
FATORES_TRANSPORTE = {
    'caminhao_16_32t': 0.098,
    'caminhao_32t': 0.061,
    'ferroviario': 0.033,
    'balsa': 0.035,
    'navio': 0.0095
}

# Combustíveis fósseis de referência (kg CO2 eq/MJ)
COMBUSTIVEIS_FOSSEIS = {
    'media_ponderada': 0.0867,
    'gasolina_a': 0.0874,
    'diesel_a': 0.0865,
    'querosene_aviacao': 0.0875,
    'glp': 0.0850
}

def calcular_intensidade_carbono(dados):
    """Calcula intensidade de carbono simplificada"""
    biomassa = dados.get('biomassa', 'casca_amendoim')
    
    # 1. Fase agrícola (produção da biomassa)
    fator_base = FATORES_BIOMASSA.get(biomassa, 0.015)
    aproveitamento = dados.get('aproveitamento_biomassa', 1.2)
    
    # Ajuste por MUT (simplificado)
    estado = dados.get('estado_producao', 'sao_paulo')
    fator_mut = 0.001 if 'sao' in estado.lower() else 0.002
    percentual_mut = dados.get('percentual_alocacao_mut', 0.325)
    
    # Transporte da biomassa
    distancia_biomassa = dados.get('distancia_transporte_biomassa', 100)
    veiculo_biomassa = dados.get('tipo_veiculo_transporte', 'caminhao_16_32t')
    fator_transp_biomassa = FATORES_TRANSPORTE.get(veiculo_biomassa, 0.098)
    
    impacto_agricola = (fator_base + fator_mut * percentual_mut) * aproveitamento
    impacto_transp_biomassa = distancia_biomassa * fator_transp_biomassa / PCI_BIOMASSA.get(biomassa, 17)
    
    # 2. Fase industrial (simplificada)
    quantidade_processada = dados.get('quantidade_biomassa_processada_kg', 12000000)
    quantidade_biocombustivel = quantidade_processada / aproveitamento
    
    # Eletricidade
    eletricidade_total = 0
    for tipo in ['media', 'alta', 'pch', 'biomassa', 'eolica', 'solar']:
        consumo = dados.get(f'eletricidade_{tipo}_kwh', 0)
        fator = 0.5 if tipo == 'biomassa' else 0.8
        eletricidade_total += consumo * fator
    
    impacto_eletricidade = (eletricidade_total * 0.0005) / (quantidade_biocombustivel * PCI_BIOMASSA.get(biomassa, 17))
    
    # Combustíveis
    combustiveis_total = 0
    for comb in ['diesel', 'gas_natural', 'glp', 'gasolina_a', 'etanol_anidro', 'etanol_hidratado']:
        consumo = dados.get(f'{comb}_consumo', 0)
        combustiveis_total += consumo * 2.0
    
    impacto_combustiveis = (combustiveis_total * 0.001) / (quantidade_biocombustivel * PCI_BIOMASSA.get(biomassa, 17))
    
    impacto_industrial = impacto_eletricidade + impacto_combustiveis
    
    # 3. Fase de distribuição
    distancia_domestica = dados.get('distancia_mercado_domestico_km', 100)
    quantidade_domestica = dados.get('quantidade_biocombustivel_distribuicao_ton', 12000) * 1000
    veiculo_domestico = dados.get('tipo_veiculo_rodoviario', 'caminhao_16_32t')
    fator_transp_domestico = FATORES_TRANSPORTE.get(veiculo_domestico, 0.098)
    
    impacto_domestico = (quantidade_domestica * distancia_domestica * fator_transp_domestico * 0.001) / (quantidade_domestica * PCI_BIOMASSA.get(biomassa, 17))
    
    # Exportação (se aplicável)
    impacto_exportacao = 0
    if dados.get('exportacao') == 'Sim':
        distancia_porto = dados.get('distancia_fabrica_porto_km', 410)
        distancia_maritima = dados.get('distancia_porto_destino_km', 10015.23)
        quantidade_exportada = dados.get('quantidade_biocombustivel_exportado_ton', 0) * 1000
        
        impacto_porto = (quantidade_exportada * distancia_porto * fator_transp_domestico * 0.001) / (quantidade_exportada * PCI_BIOMASSA.get(biomassa, 17))
        impacto_mar = (quantidade_exportada * distancia_maritima * 0.0095 * 0.001) / (quantidade_exportada * PCI_BIOMASSA.get(biomassa, 17))
        impacto_exportacao = impacto_porto + impacto_mar
    
    impacto_distribuicao = impacto_domestico + impacto_exportacao
    
    # 4. Fase de uso
    pci = PCI_BIOMASSA.get(biomassa, 17)
    impacto_uso = 0.112 / pci  # Fator de combustão simplificado
    
    # Intensidade total
    intensidade_total = (
        impacto_agricola + 
        impacto_transp_biomassa + 
        impacto_industrial + 
        impacto_distribuicao + 
        impacto_uso
    )
    
    return {
        'intensidade_total_kg_co2eq_mj': intensidade_total,
        'intensidade_total_g_co2eq_mj': intensidade_total * 1000,
        'detalhes': {
            'agricola': impacto_agricola,
            'transporte_biomassa': impacto_transp_biomassa,
            'industrial': impacto_industrial,
            'distribuicao': impacto_distribuicao,
            'uso': impacto_uso
        }
    }

def calcular_nota_eficiencia(intensidade_biocombustivel, combustivel_fossil='media_ponderada'):
    """Calcula nota de eficiência energético-ambiental"""
    referencia = COMBUSTIVEIS_FOSSEIS.get(combustivel_fossil, 0.0867)
    nota = referencia - intensidade_biocombustivel
    return max(nota, 0)

def calcular_cbios(intensidade_biocombustivel, volume_ton, biomassa='casca_amendoim'):
    """Calcula CBIOs estimados"""
    referencia = 0.0867  # Média ponderada fóssil
    nota = referencia - intensidade_biocombustivel
    
    if nota <= 0:
        return 0
    
    # Fator de conversão simplificado
    pci = PCI_BIOMASSA.get(biomassa, 17)
    fator_cbio = 0.8  # Fator simplificado
    
    cbios = nota * pci * volume_ton * fator_cbio
    return round(cbios, 0)