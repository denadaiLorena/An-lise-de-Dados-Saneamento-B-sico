"""Tema global do dashboard (claro/escuro)."""

from __future__ import annotations

import streamlit as st


THEME_LIGHT = {
    "bg": "linear-gradient(135deg, #f8fafc 0%, #eff6ff 50%, #f8fafc 100%)",
    "sidebar_bg": "linear-gradient(180deg, #ffffff, #f8fafc)",
    "sidebar_border": "rgba(148,163,184,0.25)",
    "title": "#0f172a",
    "text": "#334155",
    "muted": "#475569",
    "surface": "rgba(255,255,255,0.9)",
    "surface_border": "rgba(148,163,184,0.28)",
    "tab_bg": "rgba(226,232,240,0.65)",
    "tab_text": "#475569",
    "tab_active_bg": "rgba(59,130,246,0.16)",
    "tab_active_text": "#1d4ed8",
}

THEME_DARK = {
    "bg": "linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)",
    "sidebar_bg": "linear-gradient(180deg, #1e293b, #0f172a)",
    "sidebar_border": "rgba(148,163,184,0.1)",
    "title": "#f1f5f9",
    "text": "#cbd5e1",
    "muted": "#94a3b8",
    "surface": "rgba(30,41,59,0.8)",
    "surface_border": "rgba(148,163,184,0.2)",
    "tab_bg": "rgba(30,41,59,0.6)",
    "tab_text": "#94a3b8",
    "tab_active_bg": "rgba(59,130,246,0.2)",
    "tab_active_text": "#60a5fa",
}


def get_theme_mode() -> str:
    return st.session_state.get("theme_mode", "Claro")


def apply_theme(show_toggle: bool = True) -> str:
    if "theme_mode" not in st.session_state:
        st.session_state["theme_mode"] = "Claro"

    if show_toggle:
        st.sidebar.radio(
            "Tema",
            options=["Claro", "Escuro"],
            key="theme_mode",
            horizontal=True,
        )

    mode = get_theme_mode()
    tokens = THEME_LIGHT if mode == "Claro" else THEME_DARK

    st.markdown(
        f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    .stApp {{
        background: {tokens['bg']};
        font-family: 'Inter', sans-serif;
    }}

    [data-testid="stSidebar"] {{
        background: {tokens['sidebar_bg']} !important;
        border-right: 1px solid {tokens['sidebar_border']} !important;
    }}

    [data-testid="stSidebar"] * {{
        font-family: 'Inter', sans-serif !important;
    }}

    h1, h2, h3, h4, h5 {{
        color: {tokens['title']} !important;
        font-family: 'Inter', sans-serif !important;
    }}

    p, li, span {{
        color: {tokens['text']};
        font-family: 'Inter', sans-serif;
    }}

    .stSelectbox > div > div,
    .stMultiSelect > div > div {{
        background: {tokens['surface']} !important;
        border: 1px solid {tokens['surface_border']} !important;
        color: {tokens['title']} !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        background: {tokens['tab_bg']} !important;
        border-radius: 10px !important;
        padding: 4px !important;
        gap: 4px !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        color: {tokens['tab_text']} !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
    }}

    .stTabs [aria-selected="true"] {{
        background: {tokens['tab_active_bg']} !important;
        color: {tokens['tab_active_text']} !important;
    }}

    [data-testid="stMetric"] {{
        background: {tokens['surface']} !important;
        border: 1px solid {tokens['surface_border']} !important;
        border-radius: 10px !important;
    }}

    [data-testid="stMetricValue"] {{
        color: {tokens['title']} !important;
    }}

    [data-testid="stMetricLabel"] {{
        color: {tokens['muted']} !important;
    }}

    [data-testid="stSidebarNav"] a {{
        color: {tokens['muted']} !important;
    }}

    [data-testid="stSidebarNav"] a:hover,
    [data-testid="stSidebarNav"] a[aria-selected="true"] {{
        background: rgba(59,130,246,0.15) !important;
        color: {tokens['tab_active_text']} !important;
    }}

    footer {{ visibility: hidden; }}
</style>
        """,
        unsafe_allow_html=True,
    )

    return mode
