import math

# Fase Agricola
FATORES_IMPACTO = {
    'residuo_pinus': 0.0251,
    'residuo_eucaliptus': 0.0251,
    'carvao_eucalipto': 1.76,
    'casca_amendoim': 0.153,
    'eucaliptus_virgem': 0.104,
    'pinus_virgem': 0.422,
    'padrao': 0.0
}

PODER_CALORIFICO = {
    'residuo_pinus': 0.0532,
    'residuo_eucaliptus': 0.0633,
    'carvao_eucalipto': 0.0633,
    'casca_amendoim': 0.0585,
    'eucaliptus_virgem': 0.0633,
    'pinus_virgem': 0.532,
    'padrao': 0.0
}

CULTIVO_AGRICOLA = {
    'residuo_pinus': 'Pinus',
    'residuo_eucaliptus': 'Eucalipto',
    'carvao_eucalipto': 'Eucalipto',
    'casca_amendoim': 'Amendoim',
    'eucaliptus_virgem': 'Eucalipto',
    'pinus_virgem': 'Pinus',
}

EMISSAO_PINUS_IMPACTO_MUT = {
    'Acre': 0,
    'Alagoas': 0,
    'Amapá': 7.72,
    'Amazonas': 0,
    'Bahia': -0.59,
    'Ceará': 0,
    'Distrito Federal': -1.19,
    'Espírito Santo': -0.34,
    'Goiás': -2.09,
    'Maranhão': 8.73,
    'Mato Grosso': -2.29,
    'Mato Grosso do Sul': -2.65,
    'Minas Gerais': 0.38,
    'Pará': 12.23,
    'Paraíba': -4.43,
    'Paraná': 0.01,
    'Pernambuco': -4.06,
    'Piauí': -1.45,
    'Rio de Janeiro': 3.79,
    'Rio Grande do Norte': 0,
    'Rio Grande do Sul': 0.5,
    'Rondônia': 15.79,
    'Roraima': 11.18,
    'Santa Catarina': 1.47,
    'São Paulo': -0.48,
    'Sergipe': -3.09,
    'Tocantins': 9.16
}

EMISSAO_EUCALIPTOS_IMPACTO_MUT = {
    'Acre': 0,
    'Alagoas': 0,
    'Amapá': 2.619317,
    'Amazonas': 0,
    'Bahia': -0.200181,
    'Ceará': 0,
    'Distrito Federal': -0.403755,
    'Espírito Santo': -0.115359,
    'Goiás': -0.709116,
    'Maranhão': 2.962,
    'Mato Grosso': -0.776974,
    'Mato Grosso do Sul': -0.899118,
    'Minas Gerais': 0.12893,
    'Pará': 4.149514,
    'Paraíba': -1.503054,
    'Paraná': 0.0033929,
    'Pernambuco': -1.377517,
    'Piauí': -0.49197,
    'Rio de Janeiro': 1.285908,
    'Rio Grande do Norte': 0,
    'Rio Grande do Sul': 0.169645,
    'Rondônia': 5.357386,
    'Roraima': 3.79326,
    'Santa Catarina': 0.498756,
    'São Paulo': -0.162859,
    'Sergipe': -1.048406,
    'Tocantins': 3.107895
}

EMISSAO_AMENDOIM_IMPACTO_MUT = {
    'Acre': 0.162114,
    'Alagoas': 0,
    'Amapá': 0.100129,
    'Amazonas': 0,
    'Bahia': 0,
    'Ceará': 0.19549,
    'Distrito Federal': 0.148763,
    'Espírito Santo': 0,
    'Goiás': 0.400517,
    'Maranhão': 0,
    'Mato Grosso': 0.925957,
    'Mato Grosso do Sul': 0.243171,
    'Minas Gerais': 0.142088,
    'Pará': 0.170696,
    'Paraíba': 1.592531,
    'Paraná': 0.06866,
    'Pernambuco': 0.129691,
    'Piauí': 0.045773,
    'Rio de Janeiro': 0.151624,
    'Rio Grande do Norte': 0,
    'Rio Grande do Sul': 0,
    'Rondônia': 0.156392,
    'Roraima': 0.580749,
    'Santa Catarina': 0,
    'São Paulo': 0.141135,
    'Sergipe': 0.173557,
    'Tocantins': 0.200258
}


PERCENTUAL_RESIDUOS = {
    'residuos_galhos_folhas': 0.325,
    'residuos_casca': 0.0675,
    'residuo_serragem': 0.30375,
    'nao_aplica': 0.232083333
}


PERCENTUAL_SIMPLES = {
    'carvao_vegetal_eucalipto': 1,
    'casca_amendoin': 0.23,
    'eucaliptus_virgem': 0.675,
    'pinus_virgem': 0.675
}

QTD_BIOMASSA_VEICULO = {
    'residuo_pinus': 0.0000531915,
    'residuo_eucaliptus': 0.0000632911,
    'carvao_vegetal_eucalipto': 0.0000632911,
    'casca_amendoim': 0.0000584795,
    'eucaliptus_virgem': 0.0000632911,
    'pinus_virgem': 0.0000531915,
    'padrao': 0.0
}

IMPACTO_TRANSPORTE_BIOMASSA = {
    'caminhao_7_5_16t': 0.093697468,
    'caminhao_16_32t': 0.098020519,
    'caminhao_maior_32t': 0.06112449,
    'caminhao_60m3': 0.06112449,
    'navio': 0.009518329,
    'balsa': 0.03497023,
    'ferroviario': 0.033358047,
    'padrao': 0.0
}

# Fase Industrial
BIOMASSA_COMBUSTAO = {
    'residuo_pinus': 1.9719578,
    'residuo_eucaliptus': 1.9719578,
    'carvao_vegetal_eucalipto': 1.8810216,
    'casca_amendoim': 1.7439606,
    'eucaliptus_virgem': 1.9719578,
    'pinus_virgem': 1.9719578
}

# Resultados
USO = {
    'residuo_pinus': 0.000369179,
    'residuo_eucaliptus': 0.000369179,
    'carvao_vegetal_eucalipto': 0.119052,
    'casca_amendoim': 0.000373497,
    'eucaliptus_virgem': 0.000369179,
    'pinus_virgem': 0.000369179
}

CBIO = {
    'residuo_pinus': 18.80,
    'residuo_eucaliptus': 15.80,
    'carvao_vegetal_eucalipto': 15.80,
    'casca_amendoim': 17.10,
    'eucaliptus_virgem': 15.80,
    'pinus_virgem': 18.80
}

INTENSIDADE_CARBONO_FOSSIL = {
    'media_ponderada': 0.0867,
    'oleo_combustivel': 0.094,
    'coque_petroleo': 0.120

}


def get_float(val, default=0.0):
    if not val or val == '': return default
    try: return float(val)
    except: return default

def calcular_intensidade_carbono(inputs):
    ## Fase Agrícola

    # Produção biomassa
    tipo_bio = inputs.get('biomassa', 'residuo_pinus')
    
    yield_padrao = 1.2
    entrada_biomassa = get_float(inputs.get('entrada_especifica_biomassa'), yield_padrao)

    fator_impacto_biomassa = FATORES_IMPACTO.get(tipo_bio, 0.0)

    poder_calorifico_biomassa = PODER_CALORIFICO.get(tipo_bio, 0.0)

    impacto_consumo_amido_milho = 1.2 * get_float(inputs.get('entrada_amido_milho', '0.0'))

    impacto_producao_biomassa = 0.0
    if inputs.get('possui_info_consumo') == 'Sim':
        impacto_producao_biomassa = (entrada_biomassa * poder_calorifico_biomassa * fator_impacto_biomassa) + impacto_consumo_amido_milho
    else:
        impacto_producao_biomassa = (poder_calorifico_biomassa * fator_impacto_biomassa) + impacto_consumo_amido_milho

    # Mudança de Uso da Terra
    estado_producao_biomassa = inputs.get('estado_producao', 'São Paulo')

    cultivo_agricola = CULTIVO_AGRICOLA.get(tipo_bio, 'Pinus')

    ciclo_de_vida_residuo = inputs.get('etapa_ciclo_vida', 'nao_aplica')

    fator_impacto_mut = 0.0
    if cultivo_agricola == 'Pinus':
        fator_impacto_mut = EMISSAO_PINUS_IMPACTO_MUT.get(estado_producao_biomassa, 'São Paulo')
    elif cultivo_agricola == 'Eucalipto':
        fator_impacto_mut = EMISSAO_EUCALIPTOS_IMPACTO_MUT.get(estado_producao_biomassa, 'São Paulo')
    else:
        fator_impacto_mut = EMISSAO_AMENDOIM_IMPACTO_MUT.get(estado_producao_biomassa, 'São Paulo')

    percentual_alocacao_biomassa = 0.0

    if tipo_bio in ['residuo_pinus', 'residuo_eucaliptus']:
        percentual_alocacao_biomassa = PERCENTUAL_RESIDUOS.get(ciclo_de_vida_residuo, 0.232083333)
    else:
        percentual_alocacao_biomassa = PERCENTUAL_SIMPLES.get(tipo_bio, 0)


    impacto_mut = poder_calorifico_biomassa * (fator_impacto_mut * percentual_alocacao_biomassa)

    # Transporte da biomassa até a planta industrial

    distancia_transporte_biomassa_fabrica = get_float(inputs.get('distancia_transporte_biomassa', 100))

    tipo_veiculo_transporte = inputs.get('tipo_veiculo_transporte', 'caminhao_16_32t')

    qtd_media_biomassa_por_veiculo = QTD_BIOMASSA_VEICULO.get(tipo_bio, 0.0)


    demanda_transporte = distancia_transporte_biomassa_fabrica * qtd_media_biomassa_por_veiculo


    impacto_transporte_biomassa = demanda_transporte * IMPACTO_TRANSPORTE_BIOMASSA.get(tipo_veiculo_transporte, 0.0)


    total_agricola = impacto_producao_biomassa + impacto_mut + impacto_transporte_biomassa

    ## Fase Industrial

    # Dados do sistema
    coogeracao_energia = inputs.get('existe_cogeneration', 'Não')

    qtd_biomassa_processada = get_float(inputs.get('quantidade_biomassa_processada_kg', '0'))

    qtd_biomassa_coogeracao = get_float(inputs.get('biomassa_cogeracao_kg', '0'))

    # Energia - Eletricidade
    eletricidade_rede_media_voltagem = get_float(inputs.get('eletricidade_rede_media_kwh', '0'))
    
    eletricidade_rede_alta_voltagem = get_float(inputs.get('eletricidade_rede_alta_kwh', '0'))
    
    eletricidade_pch = get_float(inputs.get('eletricidade_pch_kwh', '0'))
    
    eletricidade_biomassa = get_float(inputs.get('eletricidade_biomassa_kwh', '0'))
    
    eletricidade_eolica = get_float(inputs.get('eletricidade_eolica_kwh', '0'))
    
    eletricidade_solar = get_float(inputs.get('eletricidade_solar_kwh', '0'))
    
    impacto_consumo_eletricidade_ano = (eletricidade_rede_media_voltagem * 0.50231324) + (eletricidade_rede_alta_voltagem * 0.128769234) + (eletricidade_pch * 0.036744999) + (eletricidade_biomassa * 0.109958818) + (eletricidade_eolica * 0.000138043) + (eletricidade_solar * 0.080086696)
    
    impacto_consumo_eletricidade_mj = impacto_consumo_eletricidade_ano * (1/qtd_biomassa_processada) * poder_calorifico_biomassa


    # Energia - Combustível
    
    diesel_consumo = get_float(inputs.get('diesel_consumo', '0'))

    gas_natural_consumoo = get_float(inputs.get('gas_natural_consumo', '0'))
    
    glp_consumo = get_float(inputs.get('glp_consumo', '0'))

    gasolina_a_consumo = get_float(inputs.get('gasolina_a_consumo', '0'))
    
    etanol_anidro_consumo = get_float(inputs.get('etanol_anidro_consumo', '0'))
    
    etanol_hidratado_consumo = get_float(inputs.get('etanol_hidratado_consumo', '0'))
    
    cavaco_madeira_consumo = get_float(inputs.get('cavaco_madeira_consumo', '0'))
    
    lenha_consumo = get_float(inputs.get('lenha_consumo', '0'))

    impacto_producao_combustivel = (diesel_consumo * 0.796) + (gas_natural_consumoo * 0.335) + (glp_consumo * 0.722) + (gasolina_a_consumo * 1.31) + (etanol_anidro_consumo * 1.23) + (etanol_hidratado_consumo * 0.607) + (cavaco_madeira_consumo * 0.365) + (lenha_consumo * 0.026)

    impacto_combustao_estacionaria = (diesel_consumo * 2.64) + (gas_natural_consumoo * 1.53) + (glp_consumo * 2.93) + (gasolina_a_consumo * 2.25) + (etanol_anidro_consumo * 1.79) + (etanol_hidratado_consumo * 1.70) + (cavaco_madeira_consumo * 1.97) + (lenha_consumo * 1.97)
    
    impacto_consumo_biocombustivel = (impacto_producao_combustivel + impacto_combustao_estacionaria) * (1 / qtd_biomassa_processada) * poder_calorifico_biomassa
    
    # Co-geração (Aproveitamento energético)

    fator_emissao_combustao = BIOMASSA_COMBUSTAO.get(tipo_bio, 0.0)

    impacto_combustao_biomassa_ano = qtd_biomassa_coogeracao * fator_emissao_combustao

    impacto_combustao_biomassa_mj = impacto_combustao_biomassa_ano * (1/qtd_biomassa_processada) * poder_calorifico_biomassa
    
    # Insumos de manufatura

    agua = get_float(inputs.get('agua_litros', '0'))
    lubrificante = get_float(inputs.get('oleo_lubrificante_kg', '0'))
    areia = get_float(inputs.get('areia_silica_kg', '0'))

    impacto_fase_idustrial_ano = (agua * 0.0000237497088) + (lubrificante * 1.5124) + (areia * 0.0357757137501474)

    impacto_fase_idustrial_mj = impacto_fase_idustrial_ano * (1/qtd_biomassa_processada) * poder_calorifico_biomassa
    
    total_industrial = impacto_consumo_eletricidade_mj + impacto_consumo_biocombustivel + impacto_combustao_biomassa_mj + impacto_fase_idustrial_mj

    ## Fase de Distribuicao
    
    # Mercado Domestico
    quantidade_biocombustivel_distribuicao_ton = get_float(inputs.get('quantidade_biocombustivel_distribuicao_ton'), 1)
    distancia_mercado_domestico_km = get_float(inputs.get('distancia_mercado_domestico_km'), 100)
    
    percentual_ferroviario = get_float(inputs.get('percentual_ferroviario'), 0) / 100.0
    percentual_hidroviario= get_float(inputs.get('percentual_hidroviario'), 0) / 100.0
    percentual_rodoviario = max(0.0, 1.0 - (percentual_ferroviario + percentual_hidroviario))
    
    tipo_veiculo_rodoviario = inputs.get('tipo_veiculo_rodoviario', 'caminhao_16_32t')

    if tipo_veiculo_rodoviario == "caminhao_7_5_16t":
        temp = 0.0937
    elif tipo_veiculo_rodoviario == "caminhao_16_32t":
        temp = 0.0980
    elif tipo_veiculo_rodoviario == "caminhao_maior_32t":
        temp = 0.0611
    elif tipo_veiculo_rodoviario == "caminhao_60m3":
        temp = 0.0611
    
    impacto_distribuica_domestico_ano = ((quantidade_biocombustivel_distribuicao_ton * (distancia_mercado_domestico_km * percentual_ferroviario) * 0.0334) + (quantidade_biocombustivel_distribuicao_ton * (distancia_mercado_domestico_km * percentual_hidroviario) * 0.0350) + (quantidade_biocombustivel_distribuicao_ton * (distancia_mercado_domestico_km * percentual_rodoviario) * temp)) 

    MJ_transportado_domestico_anualmente = quantidade_biocombustivel_distribuicao_ton * 1000 * (1 / poder_calorifico_biomassa)

    impacto_distribuicao_domestico_MJ = impacto_distribuica_domestico_ano / MJ_transportado_domestico_anualmente

    # Exportação
    quantidade_exportada_ton = get_float(inputs.get('quantidade_exportada_ton'), 1)
    
    if quantidade_exportada_ton > 0:
        distancia_fabrica_porto_km = get_float(inputs.get('distancia_fabrica_porto_km'), 0)
        distancia_porto_consumidor = get_float(inputs.get('distancia_porto_consumidor'), 0)
        
        percentual_ferroviario_porto = get_float(inputs.get('percentual_ferroviario_porto'), 0) / 100.0
        percentual_hidroviario_porto = get_float(inputs.get('percentual_hidroviario_porto'), 0) / 100.0
        percentual_rodoviario_porto = max(0.0, 1.0 - (percentual_ferroviario_porto + percentual_hidroviario_porto))
        
        tipo_veiculo_porto = inputs.get('tipo_veiculo_porto', 'caminhao_16_32t')

        if tipo_veiculo_porto == "caminhao_7_5_16t":
            temp2 = 0.0937
        elif tipo_veiculo_porto == "caminhao_16_32t":
            temp2 = 0.0980
        elif tipo_veiculo_porto == "caminhao_maior_32t":
            temp2 = 0.0611
        elif tipo_veiculo_porto == "caminhao_60m3":
            temp2 = 0.0611
        
        # Fábrica->Porto
        impacto_distribuicao_externo_fabricaporto = (quantidade_exportada_ton * (distancia_fabrica_porto_km * percentual_ferroviario_porto) * 0.0334) + (quantidade_exportada_ton * (distancia_fabrica_porto_km * percentual_hidroviario_porto) * 0.0350) + (quantidade_exportada_ton * (distancia_fabrica_porto_km * percentual_rodoviario_porto) * temp2)
        
        # Porto->Consumidor
        impacto_distribuicao_externo_porto_consumidor = quantidade_exportada_ton * distancia_porto_consumidor * 0.00952
        
        # MJ Exportado
        mj_exportado = quantidade_exportada_ton * 1000 * (1 / poder_calorifico_biomassa)
        if mj_exportado == 0: mj_exportado = 1
        
        impacto_export_mj = (impacto_distribuicao_externo_fabricaporto + impacto_distribuicao_externo_porto_consumidor) / mj_exportado
        
    # Soma total ABSOLUTA para o cálculo final da ACV
    total_transporte = impacto_distribuicao_domestico_MJ + impacto_export_mj 
    
    # Uso
    total_uso = USO.get(tipo_bio, 0.0)

    # --- RESULTADOS ---
    intensidade_carbono = total_agricola + total_industrial + total_transporte + total_uso
    
    tipo_fossil = inputs.get('combustivel_fossil_substituto', 'media_ponderada')
    
    fossil_ref = INTENSIDADE_CARBONO_FOSSIL.get(tipo_fossil, 0)
    
    nota_eficiencia_ambiental = fossil_ref - intensidade_carbono
    
    cbios = CBIO.get(tipo_bio, 0.0) * get_float(inputs.get('volume_producao_ton_cbios'), 0) * nota_eficiencia_ambiental
    
    return {
        'intensidade_total_g_co2eq_mj': intensidade_carbono,
        'cbios': cbios,
        'nota_eficiencia': nota_eficiencia_ambiental,
        'fossil_ref': fossil_ref,
        'detalhes': {
            'agricola': total_agricola ,
            'industrial': total_industrial ,
            'transporte': total_transporte,
            'uso': total_uso
        }
    }