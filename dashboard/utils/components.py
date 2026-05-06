"""
utils/components.py
Componentes de UI reutilizáveis: KPI cards, tooltips, seções, etc.
"""

import streamlit as st


def kpi_card(titulo: str, valor: str, subtitulo: str = "", cor: str = "#60a5fa", icone: str = ""):
    """
    Renderiza um card de KPI estilizado com cor temática.
    """
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(255,255,255,0.96), rgba(248,250,252,0.92));
            border: 1px solid rgba(148,163,184,0.28);
            border-top: 3px solid {cor};
            border-radius: 12px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 0.5rem;
            box-shadow: 0 4px 18px rgba(15,23,42,0.08);
            transition: transform 0.2s ease;
        ">
            <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.4rem;">
                <span style="font-size:1.4rem;">{icone}</span>
                <span style="color:#475569; font-size:0.82rem; font-weight:600; text-transform:uppercase; letter-spacing:0.05em;">
                    {titulo}
                </span>
            </div>
            <div style="font-size:2.1rem; font-weight:700; color:{cor}; line-height:1.1;">
                {valor}
            </div>
            <div style="color:#334155; font-size:0.78rem; margin-top:0.3rem;">{subtitulo}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def secao_com_tooltip(titulo: str, tooltip: str, nivel: int = 2):
    """
    Renderiza um título de seção com ícone de interrogação (tooltip no hover).
    """
    tag = f"h{nivel}"
    st.markdown(
        f"""
        <{tag} style="
            color: #0f172a;
            font-family: 'Inter', sans-serif;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.2rem;
        ">
            {titulo}
            <span
                title="{tooltip}"
                style="
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    width: 20px;
                    height: 20px;
                    background: rgba(96,165,250,0.15);
                    border: 1px solid rgba(96,165,250,0.3);
                    border-radius: 50%;
                    font-size: 0.7rem;
                    color: #60a5fa;
                    cursor: help;
                    font-weight: 700;
                "
            >?</span>
        </{tag}>
        """,
        unsafe_allow_html=True,
    )


def badge_zona(zona: str):
    """Renderiza um badge colorido para a zona de vulnerabilidade."""
    cores = {
        "Zona Verde - Baixo Risco": ("#166534", "#22c55e"),
        "Zona Amarela - Risco Moderado": ("#713f12", "#eab308"),
        "Zona Laranja - Risco Elevado": ("#7c2d12", "#f97316"),
        "Zona Vermelha - Risco Crítico": ("#7f1d1d", "#ef4444"), 
    }
    bg, text = cores.get(zona, ("#1e293b", "#94a3b8"))
    st.markdown(
        f"""
        <span style="
            background: {bg};
            color: {text};
            border: 1px solid {text}40;
            border-radius: 999px;
            padding: 0.3rem 0.9rem;
            font-size: 0.82rem;
            font-weight: 600;
            display: inline-block;
        ">{zona}</span>
        """,
        unsafe_allow_html=True,
    )


def cabecalho_pagina(titulo: str, descricao: str, icone: str = ""):
    """Renderiza o cabeçalho de uma página com título e descrição."""
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, rgba(219,234,254,0.78), rgba(255,255,255,0.95));
            border: 1px solid rgba(148,163,184,0.24);
            border-radius: 16px;
            padding: 1.8rem 2rem;
            margin-bottom: 1.5rem;
        ">
            <div style="font-size:2.5rem; margin-bottom:0.4rem;">{icone}</div>
            <h1 style="
                color: #0f172a;
                font-family: 'Inter', sans-serif;
                font-size: 1.8rem;
                font-weight: 700;
                margin: 0 0 0.5rem 0;
            ">{titulo}</h1>
            <p style="
                color: #334155;
                font-size: 0.95rem;
                line-height: 1.6;
                margin: 0;
                max-width: 700px;
            ">{descricao}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def caixa_explicacao(texto: str, tipo: str = "info"):
    """
    Exibe uma caixa de explicação colorida.
    tipo: 'info', 'aviso', 'sucesso', 'critico'
    """
    configs = {
        "info": ("💡", "rgba(96,165,250,0.1)", "rgba(96,165,250,0.3)", "#93c5fd"),
        "aviso": ("⚠️", "rgba(234,179,8,0.1)", "rgba(234,179,8,0.3)", "#fcd34d"),
        "sucesso": ("✅", "rgba(34,197,94,0.1)", "rgba(34,197,94,0.3)", "#86efac"),
        "critico": ("🔴", "rgba(239,68,68,0.1)", "rgba(239,68,68,0.3)", "#fca5a5"),
    }
    icone, bg, border, cor_texto = configs.get(tipo, configs["info"])
    st.markdown(
        f"""
        <div style="
            background: {bg};
            border-left: 3px solid {border};
            border-radius: 0 8px 8px 0;
            padding: 0.9rem 1.1rem;
            margin: 0.5rem 0;
        ">
            <span style="font-size:1rem;">{icone}</span>
            <span style="color:{cor_texto}; font-size:0.88rem; line-height:1.6;"> {texto}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def separador():
    """Linha separadora estilizada."""
    st.markdown(
        """<hr style="border:none; border-top:1px solid rgba(148,163,184,0.1); margin:1.5rem 0;">""",
        unsafe_allow_html=True,
    )


def metrica_inline(rotulo: str, valor: str, cor: str = "#e2e8f0"):
    """Renderiza uma métrica compacta inline."""
    st.markdown(
        f"""
        <div style="
            display: flex;
            flex-direction: column;
            background: rgba(255,255,255,0.88);
            border: 1px solid rgba(148,163,184,0.28);
            border-radius: 8px;
            padding: 0.7rem 1rem;
        ">
            <span style="color:#475569; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.05em;">{rotulo}</span>
            <span style="color:{cor}; font-size:1.1rem; font-weight:700; margin-top:0.2rem;">{valor}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
