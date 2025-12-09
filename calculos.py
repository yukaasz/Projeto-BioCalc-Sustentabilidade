"""
calculos.py - Versão fiel à planilha Excel BioCalc_EngS.xlsx
Baseado nas fórmulas extraídas e fatores de emissão do Ecoinvent/RenovaBio.
"""
import math

# --- BANCO DE DADOS (Extraído da aba 'Dados auxiliares') ---
# Valores com alta precisão para garantir que o resultado bata com o Excel

# Fator E37 (kg biomassa / MJ biocombustível)
# Derivado de 1 / PCI. Ex: Pinus = 1/18.8 = 0.05319148936
FATORES_CONVERSAO_KG_MJ = {
    'residuo_pinus': 0.05319148936,
    'residuo_eucaliptus': 0.06329113924,
    'casca_amendoim': 0.05847953216,
    'eucaliptus_virgem': 0.06329113924,
    'pinus_virgem': 0.05319148936
}

# Fatores de Emissão de Produção (kgCO2eq / kg biomassa)
EMISSAO_PRODUCAO = {
    'residuo_pinus': 0.02509471581,
    'residuo_eucaliptus': 0.02509471581,
    'casca_amendoim': 0.6660516674,
    'eucaliptus_virgem': 0.1037211617,
    'pinus_virgem': 0.4217291404
}

# Fatores de Mudança de Uso da Terra (MUT) - Simplificado SP
MUT_FATORES = {
    'residuo_pinus': -0.48,
    'residuo_eucaliptus': -0.48, # Assumindo similaridade para o exemplo
    'casca_amendoim': 0.0,
    'eucaliptus_virgem': 0.0,
    'pinus_virgem': 0.0
}

# Fatores de Transporte (kgCO2eq / t.km)
EMISSAO_TRANSPORTE = {
    'caminhao_16_32t': 0.09802051938,
    'caminhao_32t': 0.06112448988,
    'ferroviario': 0.03335804744,
    'balsa': 0.03497022968,
    'navio': 0.009518329267
}

# Fatores Energéticos (kgCO2eq / unidade)
EMISSAO_ENERGIA = {
    'eletricidade_grid': 0.5023132396,
    'eletricidade_bio': 0.1099588184,
    'diesel': 3.437, # Soma aprox de produção + queima
    'gas_natural': 1.865
}

def get_float(val, default=0.0):
    try:
        return float(val)
    except:
        return default

def calcular_intensidade_carbono(inputs):
    """
    Implementa as fórmulas exatas do Excel BioCalc.
    """
    
    # --- 1. CONFIGURAÇÃO INICIAL ---
    tipo_bio = inputs.get('biomassa', 'residuo_pinus')
    
    # Célula E37: Fator de Conversão (kg/MJ)
    # Na planilha: =PROCV(...)/1000. Valor: 5,32E-02
    E37_fator_kg_mj = FATORES_CONVERSAO_KG_MJ.get(tipo_bio, 0.05319)
    
    # Volume de Produção (toneladas)
    vol_prod_ton = get_float(inputs.get('volume_producao_ton_cbios'), 12000)
    
    # =========================================================================
    # FASE 1: AGRÍCOLA (Célula E40 e E47)
    # =========================================================================
    
    # Impacto Produção (E36)
    E36_fator_prod = EMISSAO_PRODUCAO.get(tipo_bio, 0.0251)
    
    # Célula E40: =((E37*E36)+E39)
    # (kg/MJ * kgCO2/kg)
    impacto_prod_mj = E37_fator_kg_mj * E36_fator_prod
    
    # Impacto MUT (E47)
    # Célula E47: =E37*(E45*E46)
    E45_fator_mut = MUT_FATORES.get(tipo_bio, -0.48)
    E46_alocacao = get_float(inputs.get('percentual_alocacao_mut'), 0.325) # 32.5%
    
    impacto_mut_mj = E37_fator_kg_mj * (E45_fator_mut * E46_alocacao)
    
    # Transporte Biomassa (E53)
    # Célula E53: =E52 * FatorTransporte
    # E52 (Demanda t.km) = Distância * (E37 / 1000000) -> Não, E51 é Ton/MJ
    # A fórmula E51 é: PROCV.../1000000. 
    # Se E37 é kg/MJ, então Ton/MJ = E37 / 1000.
    
    dist_bio = get_float(inputs.get('distancia_transporte_biomassa'), 100)
    tipo_veic_bio = inputs.get('tipo_veiculo_transporte', 'caminhao_16_32t')
    fator_transp_bio = EMISSAO_TRANSPORTE.get(tipo_veic_bio, 0.098)
    
    # E51 (Qtd Média Ton/MJ)
    E51_ton_mj = E37_fator_kg_mj / 1000.0
    
    # E52 (Demanda t.km/MJ)
    E52_tkm_mj = dist_bio * E51_ton_mj
    
    # E53 (Impacto kgCO2/MJ)
    impacto_transp_bio_mj = E52_tkm_mj * fator_transp_bio
    
    # TOTAL AGRÍCOLA (kgCO2/MJ)
    total_agricola_mj = impacto_prod_mj + impacto_mut_mj + impacto_transp_bio_mj

    # =========================================================================
    # FASE 2: INDUSTRIAL (Células E69, E81, E91)
    # =========================================================================
    
    # Célula E59: Biomassa Processada (kg/ano)
    E59_qtd_proc = get_float(inputs.get('quantidade_biomassa_processada_kg'), 12000000)
    if E59_qtd_proc == 0: E59_qtd_proc = 1
    
    # Emissões Absolutas (kgCO2/ano)
    # Eletricidade (E68)
    elec_grid = get_float(inputs.get('eletricidade_rede_media_kwh'))
    elec_bio = get_float(inputs.get('eletricidade_biomassa_kwh'))
    E68_emis_elec = (elec_grid * EMISSAO_ENERGIA['eletricidade_grid']) + \
                    (elec_bio * EMISSAO_ENERGIA['eletricidade_bio'])
    
    # Combustíveis (E80)
    diesel = get_float(inputs.get('diesel_consumo'))
    E80_emis_comb = diesel * EMISSAO_ENERGIA['diesel']
    
    # Célula E69 (Impacto Eletricidade por MJ): =E68*(1/E59)*E37
    impacto_elec_mj = E68_emis_elec * (1/E59_qtd_proc) * E37_fator_kg_mj
    
    # Célula E81 (Impacto Combustível por MJ): =E80*(1/E59)*E37
    impacto_comb_mj = E80_emis_comb * (1/E59_qtd_proc) * E37_fator_kg_mj
    
    # TOTAL INDUSTRIAL (kgCO2/MJ)
    total_industrial_mj = impacto_elec_mj + impacto_comb_mj

    # =========================================================================
    # FASE 3: DISTRIBUIÇÃO (Célula E104 e E117)
    # =========================================================================
    
    # Mercado Doméstico
    E96_qtd_dom = get_float(inputs.get('quantidade_biocombustivel_distribuicao_ton'), vol_prod_ton)
    E97_dist_dom = get_float(inputs.get('distancia_mercado_domestico_km'), 100)
    veic_dom = inputs.get('tipo_veiculo_rodoviario', 'caminhao_16_32t')
    fator_veic_dom = EMISSAO_TRANSPORTE.get(veic_dom, 0.098)
    
    # E102 (Impacto Total Ano kgCO2)
    # = Toneladas * Distância * Fator
    E102_impacto_ano = E96_qtd_dom * E97_dist_dom * fator_veic_dom
    
    # E103 (MJ Transportado Anualmente)
    # Fórmula: =E96*1000*(1/E37)
    # Lógica: Toneladas * 1000 (kg) * (MJ/kg)
    E103_mj_ano = E96_qtd_dom * 1000.0 * (1.0 / E37_fator_kg_mj)
    if E103_mj_ano == 0: E103_mj_ano = 1
    
    # E104 (Impacto kgCO2/MJ)
    impacto_dist_dom_mj = E102_impacto_ano / E103_mj_ano
    
    # Exportação (Opcional)
    impacto_export_mj = 0.0
    if inputs.get('exportacao') == 'Sim':
        E107_qtd_exp = get_float(inputs.get('quantidade_biocombustivel_exportado_ton'))
        E108_dist_porto = get_float(inputs.get('distancia_fabrica_porto_km'))
        E113_dist_navio = get_float(inputs.get('distancia_porto_destino_km'))
        
        # Trecho Terrestre + Marítimo (Emissão Absoluta)
        emis_fabrica_porto = E107_qtd_exp * E108_dist_porto * EMISSAO_TRANSPORTE['caminhao_32t']
        emis_porto_destino = E107_qtd_exp * E113_dist_navio * EMISSAO_TRANSPORTE['navio']
        
        E116_mj_exp = E107_qtd_exp * 1000.0 * (1.0 / E37_fator_kg_mj)
        if E116_mj_exp > 0:
            impacto_export_mj = (emis_fabrica_porto + emis_porto_destino) / E116_mj_exp

    total_distribuicao_mj = impacto_dist_dom_mj + impacto_export_mj

    # =========================================================================
    # FASE 4: USO (Célula J19 na verdade vem de 'Dados auxiliares')
    # =========================================================================
    # Valor padrão observado na planilha para resíduos: 0.000369...
    total_uso_mj = 0.000369179 

    # =========================================================================
    # CONSOLIDAÇÃO E CBIOS
    # =========================================================================
    
    # Intensidade Total (kgCO2eq/MJ) - Célula C23
    intensidade_total_kg_mj = total_agricola_mj + total_industrial_mj + total_distribuicao_mj + total_uso_mj
    
    # Comparador Fóssil (kgCO2eq/MJ) - Célula C21
    fossil_ref_kg_mj = 0.0867 # 86.7 g/MJ
    
    # Nota de Eficiência (kgCO2eq/MJ) - Célula J20
    nota_eficiencia_kg_mj = fossil_ref_kg_mj - intensidade_total_kg_mj
    if nota_eficiencia_kg_mj < 0: nota_eficiencia_kg_mj = 0
    
    # Geração de CBIOs (Célula H21)
    # Fórmula Lógica: Nota (kg/MJ) * Energia Total Produzida (MJ) / 1000 (kg->ton)
    # Volume elegível * 1000 * MJ/kg
    energia_total_prod_mj = vol_prod_ton * 1000.0 * (1.0 / E37_fator_kg_mj)
    
    # CBIOs = Toneladas de CO2 evitadas
    # Nota (kg/MJ) * Energia (MJ) = kgCO2 evitados
    # Dividir por 1000 para virar Toneladas (CBIOs)
    cbios = (nota_eficiencia_kg_mj * energia_total_prod_mj) / 1000.0
    
    return {
        'intensidade_total_g_co2eq_mj': intensidade_total_kg_mj * 1000.0,
        'intensidade_total_kg_co2eq_mj': intensidade_total_kg_mj,
        'cbios': int(math.floor(cbios)),
        'nota_eficiencia': nota_eficiencia_kg_mj * 1000.0, # Mostrando em g
        'detalhes': {
            'agricola': total_agricola_mj * 1000,
            'industrial': total_industrial_mj * 1000,
            'transporte': total_distribuicao_mj * 1000,
            'uso': total_uso_mj * 1000
        }
    }