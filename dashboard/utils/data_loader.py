"""
utils/data_loader.py
Carregamento e pré-processamento dos dados para o dashboard.
Usa @st.cache_data para evitar recarregamentos desnecessários.
"""

import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path

# Caminho base dos dados
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"


@st.cache_data
def carregar_dados_diamante() -> pd.DataFrame:
    """Carrega a base diamante com todos os indicadores de saneamento e risco."""
    path = DATA_DIR / "base_diamante_es_vfinal.parquet"
    df = pd.read_parquet(path)
    df = _garantir_colunas(df)
    return df


@st.cache_data
def carregar_dados_zonas() -> pd.DataFrame:
    """Carrega a base final com classificação de zonas de vulnerabilidade."""
    path = DATA_DIR / "base_final_com_zonas.parquet"
    df = pd.read_parquet(path)
    df = _garantir_colunas(df)
    return df


def _garantir_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """Garante tipos corretos e colunas derivadas essenciais."""
    df = df.copy()

    # Padronizar id_municipio como string 7 dígitos
    if "id_municipio" in df.columns:
        df["id_municipio"] = df["id_municipio"].astype(str).str.strip()

    # Garantir coluna de nome do município
    if "nome_municipio" not in df.columns and "municipio" in df.columns:
        df["nome_municipio"] = df["municipio"]
    elif "nome_municipio" not in df.columns:
        df["nome_municipio"] = df["id_municipio"]
    # nome_municipio já existe nos dados reais — não reprocessar

    # Garantir zona_vulnerabilidade com fallback
    if "zona_vulnerabilidade" not in df.columns:
        df["zona_vulnerabilidade"] = _classificar_zona(df)

    # Garantir RISCO_SOCIAL_FINAL
    if "RISCO_SOCIAL_FINAL" not in df.columns and "indice_combinado" in df.columns:
        df["RISCO_SOCIAL_FINAL"] = df["indice_combinado"]

    # Garantir vazio_sanitario
    if "vazio_sanitario" not in df.columns:
        cols = ["def_agua", "def_esgoto"]
        existing = [c for c in cols if c in df.columns]
        if existing:
            df["vazio_sanitario"] = df[existing].mean(axis=1)

    return df


def _classificar_zona(df: pd.DataFrame) -> pd.Series:
    """Classifica municípios em zonas baseado no RISCO_SOCIAL_FINAL."""
    if "RISCO_SOCIAL_FINAL" not in df.columns:
        return pd.Series("Sem Dados", index=df.index)

    risco = df["RISCO_SOCIAL_FINAL"]
    q25, q50, q75 = risco.quantile([0.25, 0.50, 0.75]).values

    conditions = [
        risco <= q25,
        (risco > q25) & (risco <= q50),
        (risco > q50) & (risco <= q75),
        risco > q75,
    ]
    choices = [
        "Zona Verde - Baixo Risco",
        "Zona Amarela - Risco Moderado",
        "Zona Laranja - Risco Elevado",
        "Zona Vermelha - Risco Crítico",
    ]
    return np.select(conditions, choices, default="Zona Amarela - Risco Moderado")


# ─── Paleta de cores por zona ────────────────────────────────────────────────

ZONA_CORES = {
    "Zona Verde - Baixo Risco": "#22c55e",
    "Zona Amarela - Risco Moderado": "#eab308",
    "Zona Laranja - Risco Elevado": "#f97316",
    "Zona Vermelha - Risco Critico": "#ef4444",
    # alias com acento (compatibilidade)
    "Zona Vermelha - Risco Crítico": "#ef4444",
}

ZONA_CORES_FOLIUM = {
    "Zona Verde - Baixo Risco": "green",
    "Zona Amarela - Risco Moderado": "orange",
    "Zona Laranja - Risco Elevado": "darkred",
    "Zona Vermelha - Risco Critico": "red",
    "Zona Vermelha - Risco Crítico": "red",
}


def obter_cor_zona(zona: str) -> str:
    """Retorna cor hex para uma zona."""
    return ZONA_CORES.get(zona, "#94a3b8")


# ─── Nomes amigáveis das colunas ─────────────────────────────────────────────

NOMES_COLUNAS = {
    "RISCO_SOCIAL_FINAL": "Índice de Risco Social",
    "vazio_sanitario": "Vazio Sanitário (%)",
    "Taxa_Morbidade_100k_Hab": "Taxa de Morbidade (por 100k hab)",
    "indice_atendimento_total_agua": "Atendimento de Água (%)",
    "indice_atendimento_esgoto_agua": "Atendimento de Esgoto (%)",
    "indice_tratamento_esgoto": "Tratamento de Esgoto (%)",
    "indice_perda_distribuicao_agua": "Perda na Distribuição de Água (%)",
    "investimento_total_consolidado": "Investimento Total (R$)",
    "eficiencia_arrecadacao": "Eficiência de Arrecadação (%)",
    "internacoes_agua": "Internações por Doenças da Água",
    "internacoes_esgoto": "Internações por Doenças do Esgoto",
    "populacao_ref": "População de Referência",
    "def_agua": "Déficit de Água (%)",
    "def_esgoto": "Déficit de Esgoto (%)",
    "nome_municipio": "Município",
    "zona_vulnerabilidade": "Zona de Vulnerabilidade",
    "ano": "Ano",
}


def nome_amigavel(col: str) -> str:
    """Retorna nome amigável de uma coluna."""
    return NOMES_COLUNAS.get(col, col.replace("_", " ").title())


# ─── Dados georreferenciados (coordenadas aproximadas dos municípios do ES) ──

COORDS_ES = {
    "3200102": (-20.7679, -40.7489),  # Afonso Cláudio
    "3200136": (-18.8575, -40.2317),  # Água Doce do Norte
    "3200169": (-18.5512, -40.9882),  # Águia Branca
    "3200201": (-19.7028, -40.6058),  # Alegre
    "3200300": (-20.1353, -41.0539),  # Alfredo Chaves
    "3200359": (-20.0483, -40.7378),  # Alto Rio Novo
    "3200409": (-20.7817, -41.3389),  # Anchieta
    "3200508": (-19.5567, -40.6067),  # Apiacá
    "3200607": (-19.5789, -40.5156),  # Aracruz
    "3200706": (-20.2881, -40.8808),  # Atilio Vivacqua
    "3200805": (-18.5725, -40.3483),  # Baixo Guandu
    "3200904": (-19.9344, -40.3550),  # Barra de São Francisco
    "3201001": (-19.9803, -40.3575),  # Boa Esperança
    "3201100": (-19.7264, -40.8383),  # Bom Jesus do Norte
    "3201159": (-20.0600, -41.2583),  # Brejetuba
    "3201209": (-20.3222, -40.3133),  # Cachoeiro de Itapemirim
    "3201308": (-19.5317, -40.8431),  # Cariacica
    "3201407": (-20.4628, -40.7764),  # Castelo
    "3201506": (-18.7542, -40.5567),  # Colatina
    "3201605": (-18.8917, -40.8628),  # Conceição da Barra
    "3201704": (-19.2339, -40.6578),  # Conceição do Castelo
    "3201803": (-20.5636, -40.9300),  # Divino de São Lourenço
    "3201902": (-18.4819, -40.0464),  # Domingos Martins
    "3202009": (-20.1800, -40.2617),  # Dores do Rio Preto
    "3202108": (-20.2481, -40.5531),  # Ecoporanga
    "3202207": (-18.3861, -40.0633),  # Fundão
    "3202256": (-20.6033, -41.0167),  # Governador Lindemberg
    "3202306": (-20.3597, -40.4597),  # Guaçuí
    "3202405": (-20.1319, -40.0281),  # Guarapari
    "3202454": (-19.8581, -41.0703),  # Ibatiba
    "3202504": (-20.0403, -41.0011),  # Ibiraçu
    "3202553": (-19.8303, -40.8683),  # Ibitirama
    "3202603": (-19.9903, -40.8378),  # Iconha
    "3202652": (-20.0833, -40.8583),  # Irupi
    "3202702": (-19.3819, -40.1169),  # Itaguaçu
    "3202801": (-19.7067, -40.8467),  # Itapemirim
    "3202900": (-18.9864, -40.2978),  # Itarana
    "3203007": (-19.6133, -40.8767),  # Iúna
    "3203056": (-18.3633, -39.8767),  # Jaguaré
    "3203106": (-20.5800, -41.1000),  # Jerônimo Monteiro
    "3203130": (-18.6953, -40.4022),  # João Neiva
    "3203163": (-18.5531, -40.0789),  # Laranja da Terra
    "3203205": (-19.3961, -40.0742),  # Linhares
    "3203304": (-18.7867, -40.2650),  # Mantenópolis
    "3203320": (-19.8833, -41.1167),  # Marataízes
    "3203346": (-20.2667, -40.5833),  # Marechal Floriano
    "3203353": (-20.4000, -41.0833),  # Marilândia
    "3203403": (-18.5933, -39.7533),  # Mimoso do Sul
    "3203502": (-19.7583, -40.2167),  # Montanha
    "3203601": (-18.1383, -40.3650),  # Mucurici
    "3203700": (-20.6167, -41.4667),  # Muniz Freire
    "3203809": (-18.9650, -40.5467),  # Muqui
    "3203908": (-20.3233, -40.4133),  # Nova Venécia
    "3204005": (-18.7183, -39.8583),  # Novo Brasil
    "3204054": (-20.0833, -41.1000),  # Pancas
    "3204104": (-20.3700, -41.1533),  # Pedro Canário
    "3204203": (-18.3617, -40.5683),  # Pinheiros
    "3204302": (-20.5750, -41.4083),  # Piúma
    "3204351": (-19.6183, -41.0317),  # Ponto Belo
    "3204401": (-20.7200, -41.1800),  # Presidente Kennedy
    "3204500": (-20.1833, -41.1167),  # Rio Bananal
    "3204559": (-19.8183, -41.0633),  # Rio Novo do Sul
    "3204609": (-19.7033, -40.3483),  # Santa Leopoldina
    "3204658": (-19.9167, -41.1000),  # Santa Maria de Jetibá
    "3204708": (-20.2183, -40.1500),  # Santa Teresa
    "3204807": (-20.0983, -40.8183),  # São Domingos do Norte
    "3204906": (-19.3183, -40.8000),  # São Gabriel da Palha
    "3205002": (-19.4633, -40.2400),  # São José do Calçado
    "3205101": (-20.5183, -41.1333),  # São Mateus
    "3205150": (-20.7633, -41.5533),  # São Roque do Canaã
    "3205200": (-20.3117, -40.2983),  # Serra
    "3205259": (-19.5033, -40.6467),  # Sooretama
    "3205309": (-20.4683, -40.7133),  # Vargem Alta
    "3205358": (-20.3533, -40.9183),  # Venda Nova do Imigrante
    "3205408": (-20.3183, -40.2917),  # Viana
    "3205457": (-18.3567, -40.1067),  # Vila Pavão
    "3205473": (-19.4333, -40.1717),  # Vila Valério
    "3205507": (-20.3283, -40.2967),  # Vila Velha
    "3205606": (-20.3194, -40.3381),  # Vitória
}
