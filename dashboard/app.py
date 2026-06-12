"""
app.py — Ponto de entrada do Dashboard de Saneamento do ES
Execute com: streamlit run app.py
"""

import sys
from pathlib import Path

# Garante que o diretório do dashboard esteja no sys.path
DASHBOARD_DIR = Path(__file__).parent
sys.path.insert(0, str(DASHBOARD_DIR))

import streamlit as st
import streamlit.components.v1 as components
from utils.theme import apply_theme, get_theme_mode

# ─── Configuração Global ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Saneamento e Saúde no ES — Dashboard Analítico",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": (
            "Dashboard desenvolvido para análise do saneamento básico no Espírito Santo. "
            "Combina dados do SNIS, DATASUS e algoritmos de Machine Learning para "
            "identificar e classificar zonas de vulnerabilidade social."
        )
    },
)

# ─── Tema Global ─────────────────────────────────────────────────────────────
apply_theme(show_toggle=True)
is_dark = get_theme_mode() == "Escuro"

home_panel_bg = (
    "linear-gradient(135deg, rgba(30,41,59,0.9) 0%, rgba(15,23,42,0.88) 55%, rgba(30,41,59,0.9) 100%)"
    if is_dark
    else "linear-gradient(135deg, rgba(219,234,254,0.9) 0%, rgba(255,255,255,0.95) 55%, rgba(224,242,254,0.9) 100%)"
)
home_panel_border = "rgba(96,165,250,0.32)" if is_dark else "rgba(59,130,246,0.24)"
title_color = "#f1f5f9" if is_dark else "#0f172a"
subtitle_color = "#94a3b8" if is_dark else "#334155"
body_color = "#cbd5e1" if is_dark else "#475569"
card_bg = (
    "linear-gradient(135deg, rgba(30,41,59,0.9), rgba(15,23,42,0.86))"
    if is_dark
    else "linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,250,252,0.92))"
)
card_border = "rgba(148,163,184,0.16)" if is_dark else "rgba(148,163,184,0.24)"

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:1rem 0 0.5rem;">
        <div style="font-size:3rem;">💧</div>
        <div style="
            font-family:'Inter',sans-serif;
            font-size:1.1rem;
            font-weight:700;
            color:""" + title_color + """;
            line-height:1.3;
        ">Saneamento ES</div>
        <div style="color:""" + subtitle_color + """; font-size:0.78rem; margin-top:4px;">
            Dashboard Analítico
        </div>
    </div>
    <hr style="border:none;border-top:1px solid rgba(148,163,184,0.1);margin:0.5rem 0 1rem;">
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="color:""" + body_color + """; font-size:0.8rem; padding:0 0.5rem 0.5rem;">
        <b style="color:#3b82f6;">📌 Navegação</b><br>
        Use o menu lateral para acessar as seções do dashboard.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <hr style="border:none;border-top:1px solid rgba(148,163,184,0.1);margin:1rem 0 0.5rem;">
    <div style="color:#475569; font-size:0.72rem; text-align:center; padding:0.5rem;">
        Dados: SNIS + DATASUS<br>
        Algoritmo: K-Means Clustering<br>
        <span style="color:#334155;">Espírito Santo, Brasil</span>
    </div>
    """, unsafe_allow_html=True)

# ─── Página Principal (Home) ──────────────────────────────────────────────────
st.markdown("""
<div style="
    background: """ + home_panel_bg + """;
    border: 1px solid """ + home_panel_border + """;
    border-radius: 20px;
    padding: 3rem 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
">
    <div style="font-size:4rem; margin-bottom:1rem;">💧</div>
    <h1 style="
        font-family:'Inter',sans-serif;
        font-size:2.4rem;
        font-weight:800;
        color:""" + title_color + """;
        margin:0 0 1rem 0;
        line-height:1.2;
    ">Saneamento Básico e Saúde Pública</h1>
    <h2 style="
        font-family:'Inter',sans-serif;
        font-size:1.2rem;
        font-weight:400;
        color:""" + subtitle_color + """;
        margin:0 0 1.5rem 0;
    ">Dashboard Analítico — Espírito Santo, Brasil</h2>
    <p style="
        color:""" + body_color + """;
        max-width:600px;
        margin:0 auto;
        line-height:1.8;
        font-size:0.95rem;
    ">
        Transformamos dados brutos do SNIS e DATASUS em inteligência acionável.
        Este dashboard revela como a falta de saneamento impacta diretamente a saúde
        da população e classifica os municípios por nível de risco social.
    </p>
</div>
""", unsafe_allow_html=True)

# ─── Cards de Seções ──────────────────────────────────────────────────────────
st.markdown("### 🗺️ O que você encontra aqui")

secoes = [
    ("🏠", "Visão Geral", "KPIs principais, distribuição do risco social e ranking de municípios.", "#3b82f6"),
    ("🗺️", "Mapa Interativo", "Mapa geográfico do ES com municípios coloridos por zona de vulnerabilidade.", "#10b981"),
    ("📈", "Correlação", "Heatmap de Spearman e análise da relação entre saneamento e internações.", "#8b5cf6"),
    ("🔬", "Análise Estatística", "Testes de normalidade (Shapiro-Wilk) e hipótese (Kruskal-Wallis) com boxplots.", "#f59e0b"),
    ("🤖", "Clusterização", "Visualização dos clusters K-Means e perfil de cada zona de vulnerabilidade.", "#ef4444"),
    ("🔍", "Perfil do Município", "Ficha completa de qualquer município: histórico, gauge de risco e comparações.", "#06b6d4"),
    ("📊", "Análises Avançadas", "Ranking, linha do tempo, investimento × risco e tendências estaduais.", "#f97316"),
]

cols_row1 = st.columns(4)
cols_row2 = st.columns(3)
cols = cols_row1 + cols_row2

for (icone, titulo, descricao, cor), col in zip(secoes, cols):
    with col:
        st.markdown(f"""
        <div style="
            background: {card_bg};
            border: 1px solid {card_border};
            border-top: 3px solid {cor};
            border-radius: 14px;
            padding: 1.3rem;
            margin-bottom: 1rem;
            transition: transform 0.2s ease;
            cursor: default;
        ">
            <div style="font-size:2rem; margin-bottom:0.5rem;">{icone}</div>
            <div style="
                font-family:'Inter',sans-serif;
                font-size:0.95rem;
                font-weight:700;
                color:{title_color};
                margin-bottom:0.4rem;
            ">{titulo}</div>
            <div style="
                color:{body_color};
                font-size:0.78rem;
                line-height:1.5;
            ">{descricao}</div>
        </div>
        """, unsafe_allow_html=True)

# ─── Problema Social ──────────────────────────────────────────────────────────
st.markdown("---")
social_impact_html = """
<div style="max-width:900px; margin:0 auto;">
    <h2 style="
        font-family:'Inter',sans-serif;
        color:""" + title_color + """;
        font-size:1.5rem;
        margin-bottom:1rem;
    ">🌍 Por que isso importa?</h2>

    <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:1.5rem; margin-bottom:2rem;">
        <div style="
            background:rgba(239,68,68,0.1);
            border:1px solid rgba(239,68,68,0.2);
            border-radius:12px;
            padding:1.2rem;
        ">
            <div style="font-size:2rem; margin-bottom:0.4rem;">🏥</div>
            <div style="color:#b91c1c; font-weight:700; font-size:1rem;">Internações Evitáveis</div>
            <div style="color:""" + body_color + """; font-size:0.82rem; margin-top:0.3rem; line-height:1.5;">
                Doenças como diarreia, cólera e hepatite A são causadas pela falta de água
                tratada e esgoto coletado — e são 100% evitáveis com saneamento adequado.
            </div>
        </div>
        <div style="
            background:rgba(234,179,8,0.1);
            border:1px solid rgba(234,179,8,0.2);
            border-radius:12px;
            padding:1.2rem;
        ">
            <div style="font-size:2rem; margin-bottom:0.4rem;">💸</div>
            <div style="color:#a16207; font-weight:700; font-size:1rem;">Custo Social</div>
            <div style="color:""" + body_color + """; font-size:0.82rem; margin-top:0.3rem; line-height:1.5;">
                Cada R$ 1 investido em saneamento poupa R$ 4 em saúde pública.
                A falta de saneamento onera o sistema de saúde e reduz a produtividade.
            </div>
        </div>
        <div style="
            background:rgba(34,197,94,0.1);
            border:1px solid rgba(34,197,94,0.2);
            border-radius:12px;
            padding:1.2rem;
        ">
            <div style="font-size:2rem; margin-bottom:0.4rem;">🎯</div>
            <div style="color:#166534; font-weight:700; font-size:1rem;">Decisão Baseada em Dados</div>
            <div style="color:""" + body_color + """; font-size:0.82rem; margin-top:0.3rem; line-height:1.5;">
                Este dashboard identifica os municípios mais críticos para priorização
                de investimentos, maximizando o impacto social de cada real gasto.
            </div>
        </div>
    </div>
</div>
"""
components.html(social_impact_html, height=390, scrolling=False)

# ─── Metodologia ─────────────────────────────────────────────────────────────
with st.expander("🔬 Metodologia e Fontes de Dados"):
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown("""
        **📦 Fontes de Dados**
        - **SNIS** (Sistema Nacional de Informações sobre Saneamento): indicadores de água e esgoto
        - **DATASUS/TabNet**: internações hospitalares por doenças de veiculação hídrica
        - **IBGE**: dados populacionais dos municípios

        **📅 Período**
        - Dados históricos a partir de 2006
        - Análise de corte transversal no ano mais recente disponível
        """)
    with col_m2:
        st.markdown("""
        **🤖 Metodologia**
        - **Limpeza de dados**: Interpolação e tratamento de valores ausentes
        - **Índice de Risco Social**: Combinação ponderada de déficits de saneamento e morbidade
        - **Clusterização**: K-Means com normalização StandardScaler
        - **Validação**: Silhouette Score e Método do Cotovelo

        **📐 Testes Estatísticos**
        - Shapiro-Wilk (normalidade)
        - Spearman (correlação)
        - Kruskal-Wallis (hipótese)
        """)

st.markdown("""
<div style="
    text-align:center;
    color:#334155;
    font-size:0.75rem;
    margin-top:2rem;
    padding-top:1rem;
    border-top:1px solid rgba(148,163,184,0.08);
">
    Dashboard de Saneamento Básico — Espírito Santo · Dados: SNIS + DATASUS
</div>
""", unsafe_allow_html=True)
