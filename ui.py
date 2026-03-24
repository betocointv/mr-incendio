"""
Tema visual moderno, responsivo e mobile-first — modo escuro fixo.
"""

import streamlit as st


# ── Paleta de cores (escuro fixo) ───────────────────────────────────────────
_CORES = {
    "bg":         "#0d0d1a",
    "surface":    "#1a1a35",
    "surface2":   "#13132a",
    "border":     "#2a2a50",
    "border2":    "#2a2a4a",
    "text":       "#f0f0f5",
    "text_muted": "#8888bb",
    "text_dim":   "#6666aa",
    "metric_val": "#ffffff",
}


def _t():
    """Retorna as cores do tema (sempre escuro)."""
    return _CORES


def tema_cores() -> dict:
    """Retorna as cores do tema (versão pública para uso nas páginas)."""
    return _CORES


def aplicar_tema():
    c = _CORES

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background: {c['bg']} !important;
        color: {c['text']} !important;
    }}

    /* Esconde elementos padrão */
    #MainMenu, footer, header {{ visibility: hidden; }}
    .stDeployButton {{ display: none; }}
    [data-testid="stSidebarNav"] {{ display: none; }}

    /* Mantém o botão de expandir a sidebar visível quando ela está recolhida */
    [data-testid="stExpandSidebarButton"],
    [data-testid="stExpandSidebarButton"] * {{
        visibility: visible !important;
        pointer-events: auto !important;
    }}

    /* Container principal */
    .block-container,
    .stMain .block-container,
    [data-testid="stMain"] .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 5.5rem !important;
        max-width: 820px !important;
        margin: 0 auto;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: {c['surface2']} !important;
        border-right: 1px solid {c['border2']};
    }}
    [data-testid="stSidebar"] * {{
        color: {c['text']} !important;
    }}

    /* Cards */
    .card {{
        background: {c['surface']};
        border: 1px solid {c['border']};
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1rem;
    }}
    .card-title {{
        font-size: 0.73rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: {c['text_muted']};
        margin-bottom: 0.3rem;
    }}
    .card-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {c['metric_val']};
        line-height: 1;
    }}
    .card-sub {{
        font-size: 0.8rem;
        color: {c['text_dim']};
        margin-top: 0.3rem;
    }}

    /* Métricas */
    [data-testid="stMetric"] {{
        background: {c['surface']} !important;
        border: 1px solid {c['border']} !important;
        border-radius: 16px !important;
        padding: 1rem 1.2rem !important;
    }}
    [data-testid="stMetricLabel"] {{ color: {c['text_muted']} !important; font-size: 0.78rem !important; }}
    [data-testid="stMetricValue"] {{ color: {c['metric_val']} !important; font-size: 1.8rem !important; font-weight: 700 !important; }}

    /* Botões */
    .stButton > button {{
        background: linear-gradient(135deg, #7a2340, #561629) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        padding: 0.55rem 1.2rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 15px rgba(122,35,64,0.22) !important;
    }}
    .stButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(122,35,64,0.35) !important;
    }}
    .stButton > button:disabled {{
        background: {c['surface']} !important;
        color: {c['text_dim']} !important;
        box-shadow: none !important;
        border: 1px solid {c['border']} !important;
    }}

    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea textarea,
    .stNumberInput > div > div > input {{
        background: {c['surface']} !important;
        border: 1.5px solid {c['border']} !important;
        border-radius: 12px !important;
        color: {c['text']} !important;
        font-size: 0.95rem !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea textarea:focus {{
        border-color: #7a2340 !important;
        box-shadow: 0 0 0 3px rgba(122,35,64,0.12) !important;
    }}
    .stTextInput label, .stTextArea label,
    .stSelectbox label, .stNumberInput label {{
        color: {c['text_muted']} !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }}

    /* Selectbox */
    .stSelectbox > div > div {{
        background: {c['surface']} !important;
        border: 1.5px solid {c['border']} !important;
        border-radius: 12px !important;
        color: {c['text']} !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background: {c['surface2']};
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
        border: 1px solid {c['border']};
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 9px;
        color: {c['text_muted']};
        font-weight: 500;
        padding: 0.4rem 1.2rem;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #7a2340, #561629) !important;
        color: white !important;
    }}

    /* Chat */
    [data-testid="stChatInput"] textarea {{
        background: {c['surface']} !important;
        border: 1.5px solid {c['border']} !important;
        border-radius: 16px !important;
        color: {c['text']} !important;
    }}
    [data-testid="stChatInput"] textarea:focus {{
        border-color: #7a2340 !important;
    }}
    /* Container geral do chat — ocupa toda a largura disponível */
    [data-testid="stChatMessageContainer"] {{
        max-width: 100% !important;
        width: 100% !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }}
    [data-testid="stChatMessage"] {{
        max-width: 100% !important;
        width: 100% !important;
    }}
    [data-testid="stChatMessageContent"] {{
        background: {c['surface']} !important;
        border-radius: 16px !important;
        border: 1px solid {c['border']} !important;
        color: {c['text']} !important;
        max-width: 100% !important;
        padding: 1rem 1.2rem !important;
    }}

    /* Expander */
    .streamlit-expanderHeader {{
        background: {c['surface']} !important;
        border-radius: 10px !important;
        border: 1px solid {c['border']} !important;
        color: {c['text']} !important;
    }}
    .streamlit-expanderContent {{
        background: {c['surface']} !important;
        border: 1px solid {c['border']} !important;
        border-top: none !important;
    }}

    /* Progress bar */
    .stProgress > div > div > div {{
        background: linear-gradient(90deg, #7a2340, #9b3258) !important;
        border-radius: 10px;
    }}
    .stProgress > div > div {{
        background: {c['border']} !important;
        border-radius: 10px;
    }}

    /* Divider */
    hr {{ border-color: {c['border']} !important; }}

    /* Alertas */
    .stAlert {{ border-radius: 12px !important; }}

    /* Dataframe */
    [data-testid="stDataFrame"] {{
        border-radius: 12px !important;
        overflow: hidden !important;
        border: 1px solid {c['border']} !important;
    }}

    /* Empurra o input de chat acima da nav bar fixa */
    [data-testid="stChatInput"] {{
        bottom: 4rem !important;
    }}

    /* Header da página */
    .page-header {{
        display: flex;
        align-items: center;
        gap: 0.7rem;
        margin-bottom: 1.2rem;
    }}

    /* Badges e chips */
    .badge-chip {{
        display: inline-block;
        background: linear-gradient(135deg, #7a2340, #561629);
        color: white;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 0.15rem 0.65rem;
        border-radius: 20px;
    }}
    .cred-chip {{
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        background: {c['surface']};
        border: 1px solid {c['border']};
        color: {c['text']};
        font-size: 0.82rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
    }}

    /* Responsivo */
    @media (max-width: 640px) {{
        .block-container {{
            padding-left: 0.7rem !important;
            padding-right: 0.7rem !important;
            padding-bottom: 5rem !important;
        }}
        .card-value {{ font-size: 1.5rem; }}
        [data-testid="stMetricValue"] {{ font-size: 1.5rem !important; }}

        /* Input do chat sobe mais para não esconder atrás da nav inferior */
        [data-testid="stChatInput"] {{
            bottom: 3.6rem !important;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)



def nav_inferior(pagina_ativa: str, tipo_usuario: str = "pessoal"):
    """Barra de navegação inferior usando st.page_link (preserva sessão Streamlit)."""
    pages = [
        ("chat",   "pages/1_Chat.py",   "🔥", "Chat"),
        ("planos", "pages/4_Planos.py", "💳", "Créditos"),
        ("pontos", "pages/3_Pontos.py", "⭐", "Pontos"),
    ]
    if tipo_usuario in ("empresa_admin", "admin"):
        pages.append(("empresa", "pages/5_Empresa.py", "🏢", "Empresa"))
    if tipo_usuario == "admin":
        pages.append(("admin", "pages/6_Admin.py", "⚙️", "Admin"))

    c = _t()

    # CSS com :has() — selector direto, sem especificar ancestrais
    nav_sel = '[data-testid="stHorizontalBlock"]:has([data-testid="stPageLink"])'
    st.markdown(f"""
    <style>
    /* Nav fixa no rodapé */
    {nav_sel} {{
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 1000001 !important;
        background: {c['surface2']} !important;
        border-top: 1px solid {c['border2']} !important;
        padding: 0.25rem 0.5rem !important;
        margin: 0 !important;
        max-width: 100vw !important;
        width: 100% !important;
    }}
    /* Desktop: offset da sidebar */
    @media (min-width: 768px) {{
        {nav_sel} {{
            padding-left: 300px !important;
        }}
    }}
    /* Mobile: nav inferior centralizada, ícones maiores */
    @media (max-width: 767px) {{
        {nav_sel} {{
            padding-left: 0 !important;
            padding-right: 0 !important;
        }}
        {nav_sel} [data-testid="stPageLink"] a {{
            font-size: 0.55rem !important;
            padding: 0.4rem 0.1rem !important;
        }}
    }}
    /* Colunas internas */
    {nav_sel} [data-testid="stColumn"] {{
        flex: 1 !important;
        min-width: 0 !important;
        padding: 0 !important;
    }}
    {nav_sel} [data-testid="stPageLink"] {{
        margin: 0 !important;
        padding: 0 !important;
    }}
    {nav_sel} [data-testid="stPageLink"] a {{
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        color: {c['text_dim']} !important;
        text-decoration: none !important;
        font-size: 0.6rem !important;
        font-weight: 500 !important;
        padding: 0.3rem 0.2rem !important;
        border-radius: 10px !important;
        transition: all 0.2s !important;
        white-space: nowrap !important;
        width: 100% !important;
    }}
    {nav_sel} [data-testid="stPageLink"] a:hover {{
        color: #7a2340 !important;
        background: rgba(122,35,64,0.1) !important;
    }}
    {nav_sel} [data-testid="stPageLink"] a[aria-current="page"] {{
        color: #7a2340 !important;
        background: rgba(122,35,64,0.1) !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # Propaga token de sessão nos links para manter login após navegação
    token = st.session_state.get("_sess_token") or st.query_params.get("t", "")

    cols = st.columns(len(pages), gap="small")
    for col, (key, path, icon, label) in zip(cols, pages):
        with col:
            if token:
                st.page_link(path, label=f"{icon}  {label}",
                             use_container_width=True, query_params={"t": token})
            else:
                st.page_link(path, label=f"{icon}  {label}", use_container_width=True)


def header_usuario(nome: str, creditos: float, pontos: int, badge: str):
    """Cabeçalho compacto com info do usuário."""
    c = _t()
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:center;
                margin-bottom:1rem;flex-wrap:wrap;gap:0.5rem;">
        <div>
            <div style="font-size:1rem;font-weight:600;color:{c['text']};">
                Olá, {nome} 👋
            </div>
            <div style="margin-top:4px;"><span class="badge-chip">{badge}</span></div>
        </div>
        <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
            <span class="cred-chip">💳 {creditos:.0f}</span>
            <span class="cred-chip">⭐ {pontos}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
