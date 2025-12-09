"""
calculos.py - Sistema de cálculo completo para biocombustíveis sólidos (Pellets/Briquetes)
Baseado na planilha BioCalc_EngS, seguindo a metodologia RenovaBio/RenovaCalc
Substitui a versão simplificada anterior
"""

import math
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# ============================================================================
# DADOS AUXILIARES (baseados na planilha 'Dados auxiliares')
# ============================================================================

class DadosAuxiliares:
    """Dados auxiliares extraídos da planilha"""
    
    # Poder calorífico inferior das biomassas (MJ/kg)
    PCI_BIOMASSA = {
        'residuo_pinus': 18.8,
        'residuo_eucaliptus': 15.8,
        'carvao_vegetal_eucalipto': 18.5,
        'casca_amendoim': 17.1,
        'eucaliptus_virgem': 15.8,
        'pinus_virgem': 18.8
    }
    
    # Mapeamento de IDs do formulário para nomes da planilha
    MAPEAMENTO_BIOMASSA = {
        'residuo_pinus': 'Resíduo de Pinus',
        'residuo_eucaliptus': 'Resíduo de Eucaliptus',
        'casca_amendoim': 'Casca de Amendoin',
        'eucaliptus_virgem': 'Eucaliptus Virgem',
        'pinus_virgem': 'Pinus Virgem',
        'carvao_vegetal_eucalipto': 'Carvão vegetal de eucalipto'
    }
    
    # Fatores de caracterização GWP (kg CO2eq/kg)
    GWP = {
        'CO2 - Dióxido de Carbono Fóssil': 1.0,
        'CH4 - Metano Fóssil': 29.8,
        'CH4 - biogênico - Metano Biogênico': 27.2,
        'N2O - Óxido Nitroso': 273.0
    }
    
    # Emissões do ciclo de vida - Produção de biomassa (kg CO2eq/kg biomassa)
    EMISSOES_PRODUCAO_BIOMASSA = {
        'Resíduo de Pinus': 0.0250947158128894,
        'Resíduo de Eucaliptus': 0.0250947158128894,
        'Carvão vegetal de eucalipto': 1.76253630637048,
        'Casca de Amendoin': 0.666051667404622,
        'Eucaliptus Virgem': 0.103721161693219,
        'Pinus Virgem': 0.42172914039108,
        'Amido de milho': 1.20067098542324
    }
    
    # Emissões da combustão da biomassa (kg CO2/kg biomassa queimada)
    EMISSOES_COMBUSTAO_BIOMASSA = {
        'Resíduo de Pinus': 0.112,  # Valor calculado M171/G171
        'Resíduo de Eucaliptus': 0.112,
        'Carvão vegetal de eucalipto': 0.102,  # M172/G172
        'Casca de Amendoin': 0.077,  # M173/G173
        'Eucaliptus Virgem': 0.112,
        'Pinus Virgem': 0.112
    }
    
    # Emissões da eletricidade (kg CO2eq/kWh)
    EMISSOES_ELETRICIDADE = {
        'Eletricidade da rede - mix média voltagem': 0.50231323962,
        'Eletricidade da rede - mix alta voltagem': 0.128769234,
        'Eletricidade - PCH': 0.036744998654,
        'Eletricidade - biomassa': 0.1099588184,
        'Eletricidade - eólica': 0.000138043213591,
        'Eletricidade - solar': 0.08008669637
    }
    
    # Emissões da produção de combustíveis (kg CO2eq/unidade)
    EMISSOES_PRODUCAO_COMBUSTIVEL = {
        'Diesel': 0.6685,  # kg CO2eq/litro
        'Gás natural': 0.3345,  # kg CO2eq/Nm³
        'GLP': 0.72196735612,  # kg CO2eq/kg
        'Gasolina A': 0.96953793802,  # kg CO2eq/litro
        'Etanol anidro': 0.9695,  # kg CO2eq/litro
        'Etanol hidratado': 0.4907,  # kg CO2eq/litro
        'Cavaco de madeira': 0.3647,  # kg CO2eq/kg
        'Lenha': 0.026  # kg CO2eq/kg
    }
    
    # Emissões da combustão estacionária (kg CO2eq/unidade)
    EMISSOES_COMBUSTAO_ESTACIONARIA = {
        'Diesel': 2.635,  # kg CO2eq/litro (aproximado)
        'Gás natural': 2.0734,  # kg CO2eq/Nm³
        'GLP': 2.9358,  # kg CO2eq/kg
        'Gasolina A': 2.315,  # kg CO2eq/litro
        'Etanol anidro': 1.548,  # kg CO2eq/litro
        'Etanol hidratado': 1.386,  # kg CO2eq/litro
        'Cavaco de madeira': 0.112,  # kg CO2eq/kg (mesmo que biomassa)
        'Lenha': 0.112  # kg CO2eq/kg
    }
    
    # Emissões de insumos industriais (kg CO2eq/unidade)
    EMISSOES_INSUMOS = {
        'Água': 0.0000237497088,  # kg CO2eq/litro
        'Óleo lubrificante': 1.5124,  # kg CO2eq/kg
        'Areia de silica': 0.0357757137501474  # kg CO2eq/kg
    }
    
    # Fatores de emissão de transporte (kg CO2eq/t.km)
    EMISSOES_TRANSPORTE = {
        'caminhao_16_32t': 0.098020519375,
        'caminhao_32t': 0.061124489876,
        'ferroviario': 0.03335804744,
        'balsa': 0.0349702296846,
        'navio': 0.00951832926726,
        'caminhao_7_5_16t': 0.093697467968,
        'caminhao_60m3': 0.061124489876
    }
    
    # Mapeamento de nomes de transporte
    MAPEAMENTO_TRANSPORTE = {
        'caminhao_16_32t': 'Transporte caminhão 16-32t',
        'caminhao_32t': 'Transporte, caminhão >32t',
        'ferroviario': 'Transporte, ferroviário',
        'balsa': 'Transporte, balsa',
        'navio': 'Transporte, navio'
    }
    
    # Mudança de Uso da Terra (MUT) por estado (tCO2/kg biomassa)
    MUT_ESTADOS = {
        'acre': 0.0,
        'alagoas': 0.0,
        'amapa': 0.00772,
        'amazonas': 0.0,
        'bahia': -0.00059,
        'ceara': 0.0,
        'distrito_federal': -0.00119,
        'espirito_santo': -0.00034,
        'goias': -0.00209,
        'maranhao': 0.00873,
        'mato_grosso': -0.00229,
        'mato_grosso_do_sul': -0.00265,
        'minas_gerais': 0.00038,
        'para': 0.01223,
        'paraiba': -0.00443,
        'parana': 0.00001,
        'pernambuco': -0.00406,
        'piaui': -0.00145,
        'rio_de_janeiro': 0.00379,
        'rio_grande_do_norte': 0.0,
        'rio_grande_do_sul': 0.0005,
        'rondonia': 0.01579,
        'roraima': 0.01118,
        'santa_catarina': 0.00147,
        'sao_paulo': -0.00048,
        'sergipe': -0.00309,
        'tocantins': 0.00916,
        'brasil': 0.00007
    }
    
    # Alocação para Mudança de Uso da Terra
    ALOCACAO_MUT = {
        ('Resíduo de Pinus', 'residuos_galhos_folhas'): 0.325,
        ('Resíduo de Pinus', 'residuos_casca'): 0.0675,
        ('Resíduo de Pinus', 'residuo_serragem'): 0.30375,
        ('Resíduo de Pinus', 'nao_especificado'): 0.232083333,
        ('Resíduo de Eucaliptus', 'residuos_galhos_folhas'): 0.325,
        ('Resíduo de Eucaliptus', 'residuos_casca'): 0.0675,
        ('Resíduo de Eucaliptus', 'residuo_serragem'): 0.30375,
        ('Resíduo de Eucaliptus', 'nao_especificado'): 0.232083333,
        ('Carvão vegetal de eucalipto', 'nao_aplica'): 1.0,
        ('Casca de Amendoin', 'nao_aplica'): 0.23,
        ('Eucaliptus Virgem', 'nao_aplica'): 0.675,
        ('Pinus Virgem', 'nao_aplica'): 0.675
    }
    
    # Combustíveis fósseis substitutos (kg CO2eq/MJ)
    COMBUSTIVEIS_FOSSEIS = {
        'media_ponderada': 0.0867,
        'gasolina_a': 0.0874,
        'diesel_a': 0.0865,
        'querosene_aviacao': 0.0875,
        'glp': 0.0850,
        'coque_petroleo': 0.102,
        'oleo_combustivel': 0.077
    }
    
    # Massas específicas e PCI dos combustíveis
    PROPRIEDADES_COMBUSTIVEIS = {
        'Etanol anidro': {'densidade': 0.791, 'pci': 28.26},
        'Etanol hidratado': {'densidade': 0.809, 'pci': 26.38},
        'Gasolina A': {'densidade': 0.742, 'pci': 43.54},
        'Diesel A': {'densidade': 0.84, 'pci': 42.29},
        'Gás natural seco': {'densidade': 0.00074, 'pci': 36.84},
        'GLP': {'densidade': 0.552, 'pci': 46.47},
        'Óleo combustível': {'densidade': 1.013, 'pci': 40.15}
    }

# ============================================================================
# CLASSES DE DADOS DE ENTRADA
# ============================================================================

@dataclass
class DadosEmpresa:
    """Dados da empresa produtora"""
    nome: str = "Empresa Teste"
    cnpj: str = "00.000.000/0001-00"
    estado: str = "São Paulo"
    cidade: str = "São Paulo"
    responsavel: str = "Usuário"
    telefone: str = "(11) 99999-9999"
    email: str = "usuario@empresa.com"

@dataclass
class DadosBiomassa:
    """Dados da biomassa"""
    tipo: str  # Resíduo de Pinus, Resíduo de Eucaliptus, etc.
    possui_info_consumo: bool  # Sim ou Não
    entrada_biomassa_especifica: Optional[float] = None  # kg biomassa/kg biocombustível
    entrada_amido_milho: float = 0.0  # kg/MJ de biocombustível
    estado_producao: str = "sao_paulo"
    etapa_ciclo_vida: str = "residuos_galhos_folhas"

@dataclass
class DadosTransporteBiomassa:
    """Dados do transporte da biomassa até a fábrica"""
    distancia: float  # km
    tipo_veiculo: str  # Transporte caminhão 16-32t, etc.

@dataclass
class DadosFaseIndustrial:
    """Dados da fase industrial"""
    # Sistema
    co_geracao: bool = False
    quantidade_biomassa_processada: float = 0.0  # kg/ano
    quantidade_biomassa_co_geracao: float = 0.0  # kg/ano
    
    # Eletricidade (kWh/ano)
    eletricidade_rede_media: float = 0.0
    eletricidade_rede_alta: float = 0.0
    eletricidade_pch: float = 0.0
    eletricidade_biomassa: float = 0.0
    eletricidade_eolica: float = 0.0
    eletricidade_solar: float = 0.0
    
    # Combustíveis
    diesel: float = 0.0  # litros/ano
    gas_natural: float = 0.0  # Nm³/ano
    glp: float = 0.0  # kg/ano
    gasolina_a: float = 0.0  # litros/ano
    etanol_anidro: float = 0.0  # litros/ano
    etanol_hidratado: float = 0.0  # litros/ano
    cavaco_madeira: float = 0.0  # kg/ano
    lenha: float = 0.0  # kg/ano
    
    # Insumos
    agua: float = 0.0  # litros/ano
    oleo_lubrificante: float = 0.0  # kg/ano
    areia_silica: float = 0.0  # kg/ano

@dataclass
class DadosDistribuicao:
    """Dados da fase de distribuição"""
    # Mercado doméstico
    quantidade_domestico: float = 0.0  # tonelada
    distancia_domestico: float = 0.0  # km
    percentual_ferroviario: float = 0.0  # %
    percentual_hidroviario: float = 0.0  # %
    tipo_veiculo_rodoviario: str = "caminhao_16_32t"
    
    # Exportação
    quantidade_exportado: float = 0.0  # tonelada(s)
    distancia_fabrica_porto: float = 0.0  # km
    percentual_ferroviario_porto: float = 0.0  # %
    percentual_hidroviario_porto: float = 0.0  # %
    tipo_veiculo_porto: str = "caminhao_16_32t"
    distancia_porto_destino: float = 0.0  # km

@dataclass
class DadosCalculo:
    """Dados completos para o cálculo"""
    empresa: DadosEmpresa
    biomassa: DadosBiomassa
    transporte_biomassa: DadosTransporteBiomassa
    fase_industrial: DadosFaseIndustrial
    distribuicao: DadosDistribuicao
    volume_producao: float = 12000.0  # Toneladas de biocombustível
    preco_cbio: float = 78.07  # R$/CBIO

# ============================================================================
# CLASSE DE CÁLCULO PRINCIPAL
# ============================================================================

class CalculadoraBiocombustiveis:
    """Calculadora completa para biocombustíveis sólidos"""
    
    def __init__(self, dados: DadosCalculo):
        self.dados = dados
        self.dados_aux = DadosAuxiliares()
        self.resultados = {}
        
    def calcular(self) -> Dict:
        """Executa todos os cálculos"""
        # 1. Calcular fator de conversão biomassa/biocombustível
        fator_conversao = self._calcular_fator_conversao()
        
        # 2. Calcular fase agrícola
        impacto_agricola = self._calcular_fase_agricola(fator_conversao)
        
        # 3. Calcular fase industrial
        impacto_industrial = self._calcular_fase_industrial(fator_conversao)
        
        # 4. Calcular fase de transporte/distribuição
        impacto_transporte = self._calcular_fase_transporte(fator_conversao)
        
        # 5. Calcular fase de uso
        impacto_uso = self._calcular_fase_uso()
        
        # 6. Calcular intensidade total de carbono
        intensidade_total = impacto_agricola + impacto_industrial + impacto_transporte + impacto_uso
        
        # 7. Calcular nota de eficiência
        nota_eficiencia = self._calcular_nota_eficiencia(intensidade_total)
        
        # 8. Calcular CBIOs
        cbios = self._calcular_cbios(intensidade_total)
        
        # 9. Calcular remuneração
        remuneracao = cbios * self.dados.preco_cbio
        
        self.resultados = {
            'intensidade_total': intensidade_total,
            'intensidade_total_g': intensidade_total * 1000,
            'intensidade_agricola': impacto_agricola,
            'intensidade_industrial': impacto_industrial,
            'intensidade_transporte': impacto_transporte,
            'intensidade_uso': impacto_uso,
            'nota_eficiencia': nota_eficiencia,
            'reducao_emissoes': (0.0867 - intensidade_total) / 0.0867 if intensidade_total > 0 else 0,
            'cbios': cbios,
            'remuneracao': remuneracao,
            'fator_conversao': fator_conversao
        }
        
        return self.resultados
    
    def _calcular_fator_conversao(self) -> float:
        """Calcula kg de biomassa por MJ de biocombustível"""
        # Mapear ID para nome da biomassa
        biomassa_id = self.dados.biomassa.tipo
        biomassa_nome = self.dados_aux.MAPEAMENTO_BIOMASSA.get(biomassa_id, biomassa_id)
        
        if self.dados.biomassa.possui_info_consumo and self.dados.biomassa.entrada_biomassa_especifica:
            # Usar valor específico fornecido pelo usuário
            kg_biomassa_kg_biocombustivel = self.dados.biomassa.entrada_biomassa_especifica
        else:
            # Usar valor padrão baseado no PCI (assumindo 1:1 para simplificação)
            pci_biomassa = self.dados_aux.PCI_BIOMASSA.get(biomassa_id, 17.0)
            # Para biomassa residual, assumir que 1 kg de biomassa produz ~0.9 kg de biocombustível
            if 'residuo' in biomassa_id:
                kg_biomassa_kg_biocombustivel = 1.1
            else:
                kg_biomassa_kg_biocombustivel = 1.2
        
        # Converter para kg biomassa/MJ biocombustível
        pci_biocombustivel = self.dados_aux.PCI_BIOMASSA.get(biomassa_id, 17.0)
        kg_biomassa_mj_biocombustivel = kg_biomassa_kg_biocombustivel / pci_biocombustivel
        
        return kg_biomassa_mj_biocombustivel
    
    def _calcular_fase_agricola(self, fator_conversao: float) -> float:
        """Calcula impacto da fase agrícola (kg CO2eq/MJ)"""
        # Mapear ID para nome da biomassa
        biomassa_id = self.dados.biomassa.tipo
        biomassa_nome = self.dados_aux.MAPEAMENTO_BIOMASSA.get(biomassa_id, biomassa_id)
        
        # 1. Produção da biomassa
        emissao_producao = self.dados_aux.EMISSOES_PRODUCAO_BIOMASSA.get(biomassa_nome, 0.025)
        impacto_producao = emissao_producao * fator_conversao
        
        # 2. Amido de milho (se aplicável)
        impacto_amido = self.dados.biomassa.entrada_amido_milho * self.dados_aux.EMISSOES_PRODUCAO_BIOMASSA['Amido de milho']
        
        # 3. Mudança de Uso da Terra (MUT)
        mut_estado = self.dados_aux.MUT_ESTADOS.get(self.dados.biomassa.estado_producao, 0.0)
        
        # Ajustar por tipo de biomassa (simplificado)
        if 'pinus' in biomassa_id:
            fator_mut = mut_estado
        elif 'eucaliptus' in biomassa_id:
            fator_mut = mut_estado * 0.7  # Aproximação
        elif 'amendoim' in biomassa_id:
            fator_mut = mut_estado * 0.5  # Aproximação
        else:
            fator_mut = mut_estado
        
        # Alocação MUT
        chave_alocacao = (biomassa_nome, self.dados.biomassa.etapa_ciclo_vida)
        percentual_alocacao = self.dados_aux.ALOCACAO_MUT.get(chave_alocacao, 0.325)
        
        impacto_mut = fator_mut * percentual_alocacao * fator_conversao
        
        # 4. Transporte da biomassa até a fábrica
        distancia = self.dados.transporte_biomassa.distancia
        tipo_veiculo = self.dados.transporte_biomassa.tipo_veiculo
        fator_transporte = self.dados_aux.EMISSOES_TRANSPORTE.get(tipo_veiculo, 0.098)
        
        # Quantidade média transportada (t.km/MJ)
        # Simplificação: usar fator_conversao para estimar biomassa por MJ
        impacto_transporte_biomassa = distancia * fator_transporte * fator_conversao / 1000  # /1000 para converter kg para ton
        
        # Soma dos impactos
        impacto_total = impacto_producao + impacto_amido + impacto_mut + impacto_transporte_biomassa
        
        return impacto_total
    
    def _calcular_fase_industrial(self, fator_conversao: float) -> float:
        """Calcula impacto da fase industrial (kg CO2eq/MJ)"""
        dados = self.dados.fase_industrial
        biomassa_id = self.dados.biomassa.tipo
        biomassa_nome = self.dados_aux.MAPEAMENTO_BIOMASSA.get(biomassa_id, biomassa_id)
        
        # Quantidade de biocombustível produzido (kg/ano)
        quantidade_biocombustivel_kg = dados.quantidade_biomassa_processada / (fator_conversao * self.dados_aux.PCI_BIOMASSA.get(biomassa_id, 17.0))
        
        if quantidade_biocombustivel_kg <= 0:
            quantidade_biocombustivel_kg = self.dados.volume_producao * 1000  # Fallback
        
        # 1. Eletricidade
        impactos_eletricidade = [
            dados.eletricidade_rede_media * self.dados_aux.EMISSOES_ELETRICIDADE['Eletricidade da rede - mix média voltagem'],
            dados.eletricidade_rede_alta * self.dados_aux.EMISSOES_ELETRICIDADE['Eletricidade da rede - mix alta voltagem'],
            dados.eletricidade_pch * self.dados_aux.EMISSOES_ELETRICIDADE['Eletricidade - PCH'],
            dados.eletricidade_biomassa * self.dados_aux.EMISSOES_ELETRICIDADE['Eletricidade - biomassa'],
            dados.eletricidade_eolica * self.dados_aux.EMISSOES_ELETRICIDADE['Eletricidade - eólica'],
            dados.eletricidade_solar * self.dados_aux.EMISSOES_ELETRICIDADE['Eletricidade - solar']
        ]
        
        impacto_eletricidade_total = sum(impactos_eletricidade)
        impacto_eletricidade_mj = impacto_eletricidade_total * fator_conversao / quantidade_biocombustivel_kg
        
        # 2. Combustíveis (produção + combustão)
        combustiveis = {
            'Diesel': dados.diesel,
            'Gás natural': dados.gas_natural,
            'GLP': dados.glp,
            'Gasolina A': dados.gasolina_a,
            'Etanol anidro': dados.etanol_anidro,
            'Etanol hidratado': dados.etanol_hidratado,
            'Cavaco de madeira': dados.cavaco_madeira,
            'Lenha': dados.lenha
        }
        
        impacto_combustiveis_total = 0
        for tipo, consumo in combustiveis.items():
            if consumo > 0:
                # Produção
                impacto_producao = consumo * self.dados_aux.EMISSOES_PRODUCAO_COMBUSTIVEL.get(tipo, 0.0)
                # Combustão estacionária
                impacto_combustao = consumo * self.dados_aux.EMISSOES_COMBUSTAO_ESTACIONARIA.get(tipo, 0.0)
                impacto_combustiveis_total += impacto_producao + impacto_combustao
        
        impacto_combustiveis_mj = impacto_combustiveis_total * fator_conversao / quantidade_biocombustivel_kg
        
        # 3. Co-geração (se houver)
        impacto_co_geracao = 0
        if dados.co_geracao and dados.quantidade_biomassa_co_geracao > 0:
            fator_emissao = self.dados_aux.EMISSOES_COMBUSTAO_BIOMASSA.get(biomassa_nome, 0.112)
            impacto_co_geracao_total = dados.quantidade_biomassa_co_geracao * fator_emissao
            impacto_co_geracao = impacto_co_geracao_total * fator_conversao / quantidade_biocombustivel_kg
        
        # 4. Insumos industriais
        impactos_insumos = [
            dados.agua * self.dados_aux.EMISSOES_INSUMOS['Água'],
            dados.oleo_lubrificante * self.dados_aux.EMISSOES_INSUMOS['Óleo lubrificante'],
            dados.areia_silica * self.dados_aux.EMISSOES_INSUMOS['Areia de silica']
        ]
        
        impacto_insumos_total = sum(impactos_insumos)
        impacto_insumos_mj = impacto_insumos_total * fator_conversao / quantidade_biocombustivel_kg
        
        # Impacto total da fase industrial
        impacto_total = impacto_eletricidade_mj + impacto_combustiveis_mj + impacto_co_geracao + impacto_insumos_mj
        
        return impacto_total
    
    def _calcular_fase_transporte(self, fator_conversao: float) -> float:
        """Calcula impacto da fase de transporte/distribuição (kg CO2eq/MJ)"""
        dados = self.dados.distribuicao
        biomassa_id = self.dados.biomassa.tipo
        
        pci_biocombustivel = self.dados_aux.PCI_BIOMASSA.get(biomassa_id, 17.0)
        
        # 1. Mercado doméstico
        impacto_domestico = 0
        if dados.quantidade_domestico > 0 and dados.distancia_domestico > 0:
            # Cálculo de t.km
            percentual_rodoviario = 100 - dados.percentual_ferroviario - dados.percentual_hidroviario
            impacto_rodoviario = impacto_ferroviario = impacto_hidroviario = 0
            
            # Rodoviário
            if percentual_rodoviario > 0:
                fator_rodoviario = self.dados_aux.EMISSOES_TRANSPORTE.get(dados.tipo_veiculo_rodoviario, 0.098)
                tkm_rodoviario = dados.quantidade_domestico * dados.distancia_domestico * (percentual_rodoviario/100)
                impacto_rodoviario = tkm_rodoviario * fator_rodoviario
            
            # Ferroviário
            if dados.percentual_ferroviario > 0:
                fator_ferroviario = self.dados_aux.EMISSOES_TRANSPORTE.get('ferroviario', 0.033)
                tkm_ferroviario = dados.quantidade_domestico * dados.distancia_domestico * (dados.percentual_ferroviario/100)
                impacto_ferroviario = tkm_ferroviario * fator_ferroviario
            
            # Hidroviário
            if dados.percentual_hidroviario > 0:
                fator_hidroviario = self.dados_aux.EMISSOES_TRANSPORTE.get('balsa', 0.035)
                tkm_hidroviario = dados.quantidade_domestico * dados.distancia_domestico * (dados.percentual_hidroviario/100)
                impacto_hidroviario = tkm_hidroviario * fator_hidroviario
            
            # Total em kg CO2eq/ano
            impacto_total_ano = impacto_rodoviario + impacto_ferroviario + impacto_hidroviario
            
            # Converter para kg CO2eq/MJ
            mj_anual = dados.quantidade_domestico * 1000 * pci_biocombustivel
            impacto_domestico = impacto_total_ano / mj_anual if mj_anual > 0 else 0
        
        # 2. Exportação
        impacto_exportacao = 0
        if dados.quantidade_exportado > 0:
            # Trecho fábrica-porto
            percentual_rodoviario_porto = 100 - dados.percentual_ferroviario_porto - dados.percentual_hidroviario_porto
            
            impacto_fabrica_porto = 0
            if percentual_rodoviario_porto > 0:
                fator_rodoviario = self.dados_aux.EMISSOES_TRANSPORTE.get(dados.tipo_veiculo_porto, 0.098)
                impacto_fabrica_porto += dados.quantidade_exportado * dados.distancia_fabrica_porto * (percentual_rodoviario_porto/100) * fator_rodoviario
            
            if dados.percentual_ferroviario_porto > 0:
                fator_ferroviario = self.dados_aux.EMISSOES_TRANSPORTE.get('ferroviario', 0.033)
                impacto_fabrica_porto += dados.quantidade_exportado * dados.distancia_fabrica_porto * (dados.percentual_ferroviario_porto/100) * fator_ferroviario
            
            if dados.percentual_hidroviario_porto > 0:
                fator_hidroviario = self.dados_aux.EMISSOES_TRANSPORTE.get('balsa', 0.035)
                impacto_fabrica_porto += dados.quantidade_exportado * dados.distancia_fabrica_porto * (dados.percentual_hidroviario_porto/100) * fator_hidroviario
            
            # Trecho porto-destino (marítimo)
            fator_navio = self.dados_aux.EMISSOES_TRANSPORTE.get('navio', 0.0095)
            impacto_porto_destino = dados.quantidade_exportado * dados.distancia_porto_destino * fator_navio
            
            # Total exportação
            impacto_exportacao_total = impacto_fabrica_porto + impacto_porto_destino
            
            # Converter para kg CO2eq/MJ
            mj_exportado = dados.quantidade_exportado * 1000 * pci_biocombustivel
            impacto_exportacao = impacto_exportacao_total / mj_exportado if mj_exportado > 0 else 0
        
        # Impacto total da distribuição
        impacto_total = impacto_domestico + impacto_exportacao
        
        return impacto_total
    
    def _calcular_fase_uso(self) -> float:
        """Calcula impacto da fase de uso (kg CO2eq/MJ)"""
        biomassa_id = self.dados.biomassa.tipo
        biomassa_nome = self.dados_aux.MAPEAMENTO_BIOMASSA.get(biomassa_id, biomassa_id)
        pci_biocombustivel = self.dados_aux.PCI_BIOMASSA.get(biomassa_id, 17.0)
        
        # Fator de emissão da combustão (kg CO2eq/kg biocombustível)
        fator_emissao_kg = self.dados_aux.EMISSOES_COMBUSTAO_BIOMASSA.get(biomassa_nome, 0.112)
        
        # Converter para kg CO2eq/MJ
        impacto_uso = fator_emissao_kg / pci_biocombustivel
        
        return impacto_uso
    
    def _calcular_nota_eficiencia(self, intensidade_total: float) -> float:
        """Calcula nota de eficiência energético-ambiental"""
        referencia_fossil = self.dados_aux.COMBUSTIVEIS_FOSSEIS['media_ponderada']
        nota = referencia_fossil - intensidade_total
        return nota
    
    def _calcular_cbios(self, intensidade_total: float) -> int:
        """Calcula número de CBIOs elegíveis"""
        referencia_fossil = self.dados_aux.COMBUSTIVEIS_FOSSEIS['media_ponderada']
        
        if intensidade_total >= referencia_fossil:
            return 0
        
        # Nota positiva (redução de emissões)
        nota = referencia_fossil - intensidade_total
        
        # Fator de conversão baseado na fórmula da planilha
        biomassa_id = self.dados.biomassa.tipo
        pci_biocombustivel = self.dados_aux.PCI_BIOMASSA.get(biomassa_id, 17.0)
        
        # Fator simplificado baseado nos cálculos da planilha
        # Na planilha: CBIOs = ROUNDDOWN(VLOOKUP(...))
        # Usamos: CBIOs = Volume * Nota * PCI * Fator
        fator_cbio = 10.0  # Fator aproximado
        
        cbios = nota * pci_biocombustivel * self.dados.volume_producao * fator_cbio
        
        return int(math.floor(max(cbios, 0)))

# ============================================================================
# FUNÇÕES DE INTERFACE COMPATÍVEIS COM A APLICAÇÃO FLASK
# ============================================================================

def converter_dados_formulario(dados_form):
    """
    Converte dados do formulário HTML para a estrutura de dados da calculadora
    
    Args:
        dados_form: Dicionário com dados do formulário
        
    Returns:
        DadosCalculo: Objeto com dados estruturados
    """
    # Dados da empresa (usar padrão)
    empresa = DadosEmpresa()
    
    # Dados da biomassa
    biomassa = DadosBiomassa(
        tipo=dados_form.get('biomassa', 'casca_amendoim'),
        possui_info_consumo=dados_form.get('possui_info_consumo') == 'Sim',
        entrada_biomassa_especifica=dados_form.get('entrada_especifica_biomassa', 0),
        entrada_amido_milho=dados_form.get('entrada_amido_milho', 0),
        estado_producao=dados_form.get('estado_producao', 'sao_paulo').lower().replace(' ', '_'),
        etapa_ciclo_vida=dados_form.get('etapa_ciclo_vida', 'residuos_galhos_folhas')
    )
    
    # Transporte da biomassa
    transporte_biomassa = DadosTransporteBiomassa(
        distancia=dados_form.get('distancia_transporte_biomassa', 100),
        tipo_veiculo=dados_form.get('tipo_veiculo_transporte', 'caminhao_16_32t')
    )
    
    # Fase industrial
    fase_industrial = DadosFaseIndustrial(
        co_geracao=dados_form.get('co_geracao') == 'Sim',
        quantidade_biomassa_processada=dados_form.get('quantidade_biomassa_processada_kg', 12000000),
        quantidade_biomassa_co_geracao=dados_form.get('biomassa_co_geracao_kg', 0),
        eletricidade_rede_media=dados_form.get('eletricidade_rede_media_kwh', 0),
        eletricidade_rede_alta=dados_form.get('eletricidade_rede_alta_kwh', 0),
        eletricidade_pch=dados_form.get('eletricidade_pch_kwh', 0),
        eletricidade_biomassa=dados_form.get('eletricidade_biomassa_kwh', 0),
        eletricidade_eolica=dados_form.get('eletricidade_eolica_kwh', 0),
        eletricidade_solar=dados_form.get('eletricidade_solar_kwh', 0),
        diesel=dados_form.get('diesel_consumo', 0),
        gas_natural=dados_form.get('gas_natural_consumo', 0),
        glp=dados_form.get('glp_consumo', 0),
        gasolina_a=dados_form.get('gasolina_a_consumo', 0),
        etanol_anidro=dados_form.get('etanol_anidro_consumo', 0),
        etanol_hidratado=dados_form.get('etanol_hidratado_consumo', 0),
        cavaco_madeira=dados_form.get('cavaco_madeira_consumo', 0),
        lenha=dados_form.get('lenha_consumo', 0),
        agua=dados_form.get('agua_litros', 0),
        oleo_lubrificante=dados_form.get('oleo_lubrificante_kg', 0),
        areia_silica=dados_form.get('areia_silica_kg', 0)
    )
    
    # Distribuição
    distribuicao = DadosDistribuicao(
        quantidade_domestico=dados_form.get('quantidade_biocombustivel_distribuicao_ton', 12000),
        distancia_domestico=dados_form.get('distancia_mercado_domestico_km', 100),
        percentual_ferroviario=dados_form.get('percentual_ferroviario', 0),
        percentual_hidroviario=dados_form.get('percentual_hidroviario', 0),
        tipo_veiculo_rodoviario=dados_form.get('tipo_veiculo_rodoviario', 'caminhao_16_32t'),
        quantidade_exportado=dados_form.get('quantidade_biocombustivel_exportado_ton', 0) if dados_form.get('exportacao') == 'Sim' else 0,
        distancia_fabrica_porto=dados_form.get('distancia_fabrica_porto_km', 410),
        percentual_ferroviario_porto=dados_form.get('percentual_ferroviario_porto', 0),
        percentual_hidroviario_porto=dados_form.get('percentual_hidroviario_porto', 0),
        tipo_veiculo_porto=dados_form.get('tipo_veiculo_porto', 'caminhao_16_32t'),
        distancia_porto_destino=dados_form.get('distancia_porto_destino_km', 10015.23)
    )
    
    # Dados completos
    dados_calculo = DadosCalculo(
        empresa=empresa,
        biomassa=biomassa,
        transporte_biomassa=transporte_biomassa,
        fase_industrial=fase_industrial,
        distribuicao=distribuicao,
        volume_producao=dados_form.get('volume_producao_ton_cbios', 12000),
        preco_cbio=78.07
    )
    
    return dados_calculo

def calcular_intensidade_carbono(dados):
    """
    Calcula intensidade de carbono (função principal compatível com app.py)
    
    Args:
        dados: Dicionário com dados do formulário
        
    Returns:
        Dicionário com resultados
    """
    try:
        # Converter dados do formulário
        dados_calculo = converter_dados_formulario(dados)
        
        # Executar cálculo
        calculadora = CalculadoraBiocombustiveis(dados_calculo)
        resultados = calculadora.calcular()
        
        # Retornar no formato esperado pelo app.py
        return {
            'intensidade_total_kg_co2eq_mj': resultados['intensidade_total'],
            'intensidade_total_g_co2eq_mj': resultados['intensidade_total_g'],
            'detalhes': {
                'agricola': resultados['intensidade_agricola'],
                'industrial': resultados['intensidade_industrial'],
                'transporte': resultados['intensidade_transporte'],
                'uso': resultados['intensidade_uso']
            }
        }
    except Exception as e:
        print(f"Erro no cálculo: {e}")
        # Fallback para cálculo simplificado em caso de erro
        return calcular_intensidade_carbono_simplificado(dados)

def calcular_nota_eficiencia(intensidade_biocombustivel, combustivel_fossil='media_ponderada'):
    """
    Calcula nota de eficiência energético-ambiental
    
    Args:
        intensidade_biocombustivel: Intensidade de carbono do biocombustível (kg CO2eq/MJ)
        combustivel_fossil: Tipo de combustível fóssil substituto
        
    Returns:
        Nota de eficiência (kg CO2eq/MJ)
    """
    dados_aux = DadosAuxiliares()
    referencia = dados_aux.COMBUSTIVEIS_FOSSEIS.get(combustivel_fossil, 0.0867)
    nota = referencia - intensidade_biocombustivel
    return max(nota, 0)

def calcular_cbios(intensidade_biocombustivel, volume_ton, biomassa='casca_amendoim'):
    """
    Calcula CBIOs estimados
    
    Args:
        intensidade_biocombustivel: Intensidade de carbono do biocombustível (kg CO2eq/MJ)
        volume_ton: Volume de produção em toneladas/ano
        biomassa: Tipo de biomassa
        
    Returns:
        Número estimado de CBIOs
    """
    dados_aux = DadosAuxiliares()
    referencia = dados_aux.COMBUSTIVEIS_FOSSEIS['media_ponderada']
    
    if intensidade_biocombustivel >= referencia:
        return 0
    
    # Nota positiva
    nota = referencia - intensidade_biocombustivel
    
    # Fator de conversão
    pci = dados_aux.PCI_BIOMASSA.get(biomassa, 17.0)
    fator_cbio = 10.0  # Fator aproximado
    
    cbios = nota * pci * volume_ton * fator_cbio
    return int(math.floor(max(cbios, 0)))

# ============================================================================
# FUNÇÕES DE FALLBACK (para compatibilidade)
# ============================================================================

def calcular_intensidade_carbono_simplificado(dados):
    """
    Cálculo simplificado (fallback em caso de erro no cálculo principal)
    """
    dados_aux = DadosAuxiliares()
    biomassa = dados.get('biomassa', 'casca_amendoim')
    
    # Valores padrão
    fator_base = 0.015
    aproveitamento = dados.get('aproveitamento_biomassa', 1.2)
    distancia_biomassa = dados.get('distancia_transporte_biomassa', 100)
    veiculo_biomassa = dados.get('tipo_veiculo_transporte', 'caminhao_16_32t')
    
    # Cálculos simplificados
    impacto_agricola = fator_base * aproveitamento
    fator_transp = dados_aux.EMISSOES_TRANSPORTE.get(veiculo_biomassa, 0.098)
    pci = dados_aux.PCI_BIOMASSA.get(biomassa, 17.0)
    impacto_transp_biomassa = distancia_biomassa * fator_transp / pci
    
    # Estimativas para outras fases
    impacto_industrial = 0.002
    impacto_distribuicao = 0.001
    impacto_uso = 0.112 / pci
    
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

# ============================================================================
# FUNÇÕES AUXILIARES PARA TESTES E COMPARAÇÃO
# ============================================================================

def exemplo_calculo():
    """Exemplo de uso da calculadora"""
    # Dados de exemplo
    dados_form = {
        'biomassa': 'residuo_pinus',
        'possui_info_consumo': 'Não',
        'estado_producao': 'sao_paulo',
        'etapa_ciclo_vida': 'residuos_galhos_folhas',
        'distancia_transporte_biomassa': 100,
        'tipo_veiculo_transporte': 'caminhao_16_32t',
        'quantidade_biomassa_processada_kg': 12000000,
        'quantidade_biocombustivel_distribuicao_ton': 12000,
        'distancia_mercado_domestico_km': 100,
        'percentual_ferroviario': 0,
        'percentual_hidroviario': 0,
        'tipo_veiculo_rodoviario': 'caminhao_16_32t',
        'exportacao': 'Sim',
        'quantidade_biocombustivel_exportado_ton': 12000,
        'distancia_fabrica_porto_km': 410,
        'distancia_porto_destino_km': 10015.23,
        'volume_producao_ton_cbios': 12000
    }
    
    resultado = calcular_intensidade_carbono(dados_form)
    return resultado

def comparar_biomassas(volume_producao_ton=10000.0):
    """
    Compara diferentes tipos de biomassa
    """
    biomassas = ['residuo_pinus', 'residuo_eucaliptus', 'casca_amendoim']
    
    comparacao = {}
    
    for biomassa in biomassas:
        dados_form = {
            'biomassa': biomassa,
            'quantidade_biomassa_processada_kg': volume_producao_ton * 1000,
            'quantidade_biocombustivel_distribuicao_ton': volume_producao_ton,
            'distancia_mercado_domestico_km': 100,
            'volume_producao_ton_cbios': volume_producao_ton
        }
        
        resultado = calcular_intensidade_carbono(dados_form)
        
        comparacao[biomassa] = {
            'intensidade_carbono': resultado['intensidade_total_kg_co2eq_mj'],
            'intensidade_carbono_g': resultado['intensidade_total_g_co2eq_mj'],
            'nota_eficiencia': calcular_nota_eficiencia(resultado['intensidade_total_kg_co2eq_mj']),
            'cbios': calcular_cbios(resultado['intensidade_total_kg_co2eq_mj'], volume_producao_ton, biomassa)
        }
    
    return comparacao

