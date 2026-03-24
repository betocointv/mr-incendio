"""
Mr. Incêndio — Página de acesso (login / cadastro).
"""
import streamlit as st
from auth import login, registrar, sessao_logada, iniciar_sessao, solicitar_reset, confirmar_reset
from ui import aplicar_tema

st.set_page_config(page_title="Acesso · Mr. Incêndio", page_icon="🔥", layout="wide")
aplicar_tema()

if sessao_logada():
    st.switch_page("pages/1_Chat.py")

# Detecta modo de recuperação via query param ?token=...
_token_reset = st.query_params.get("token", "")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebarNav"],
[data-testid="stSidebar"],
#MainMenu, footer, header,
[data-testid="stToolbar"] { display:none !important; }

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family:'Inter',sans-serif; box-sizing:border-box; }

:root {
  --wine:    #7a2340;
  --wine-dk: #561629;
  --wine-lt: #c4607a;
  --bg0: #08080e; --bg1: #0f0f1e; --bg2: #141428; --bg3: #1a1a30;
  --border: rgba(255,255,255,0.08);
  --text: #f0f0f8; --muted: #9090b8; --dim: #60607a;
}

body, .stApp {
  background:
    radial-gradient(ellipse 60% 40% at 50% 100%, rgba(122,35,64,.2) 0%, transparent 65%),
    var(--bg0) !important;
}

/* Block container: centralizado, offset para a nav fixa */
.main .block-container,
.stMain .block-container,
[data-testid="stMain"] .block-container,
[data-testid="stAppViewBlockContainer"] {
  max-width: 560px !important;
  padding-top: 6rem !important;
  padding-bottom: 4rem !important;
  padding-left: 1rem !important;
  padding-right: 1rem !important;
}

/* ── NAV ── */
.lp-nav a { color: inherit !important; text-decoration: none !important; }
.lp-nav {
  position:fixed; top:0; left:0; right:0; z-index:9999;
  display:flex; align-items:center; justify-content:space-between;
  padding:0 3rem; height:64px;
  background:rgba(9,9,15,0.92); backdrop-filter:blur(16px);
  border-bottom:1px solid var(--border);
}
a.lp-logo, a.lp-logo:link, a.lp-logo:visited,
a.lp-logo:hover, a.lp-logo:active {
  font-size:1.15rem; font-weight:800; color:#fff !important;
  display:flex; align-items:center; gap:.5rem;
  text-decoration:none !important; letter-spacing:-.02em;
}
.lp-logo-dot {
  width:30px; height:30px; border-radius:8px;
  background:linear-gradient(135deg,var(--wine),var(--wine-dk));
  display:flex; align-items:center; justify-content:center;
  font-size:.95rem; flex-shrink:0;
}
.lp-links { display:flex; align-items:center; gap:2rem; }
.lp-links a, .lp-links a:link, .lp-links a:visited {
  color:var(--muted) !important; text-decoration:none !important;
  font-size:.88rem; font-weight:500; transition:color .2s;
}
.lp-links a:hover { color:#fff !important; }
.lp-nav-btns { display:flex; gap:.65rem; align-items:center; }
a.btn-ghost, a.btn-ghost:link, a.btn-ghost:visited {
  color:#ddd !important; text-decoration:none !important; font-size:.85rem; font-weight:600;
  padding:.38rem 1rem; border:1.5px solid rgba(255,255,255,0.18);
  border-radius:8px; transition:all .2s; display:inline-block;
}
a.btn-ghost:hover { border-color:rgba(255,255,255,.5); color:#fff !important; }
a.btn-wine, a.btn-wine:link, a.btn-wine:visited {
  background:linear-gradient(135deg,var(--wine),var(--wine-dk));
  color:white !important; text-decoration:none !important; font-size:.85rem; font-weight:700;
  padding:.4rem 1.1rem; border-radius:8px; display:inline-block;
}
a.btn-wine:hover { opacity:.88; color:white !important; }

/* ── Cabeçalho da página ── */
.access-header {
  text-align:center; margin-bottom:2rem;
}
.access-header h2 {
  font-size:1.6rem; font-weight:800; color:#fff;
  margin:.4rem 0 .4rem; letter-spacing:-.02em;
}
.access-header p { color:var(--muted); font-size:.88rem; margin:0; }
.access-icon {
  width:50px; height:50px; border-radius:14px;
  background:linear-gradient(135deg,var(--wine),var(--wine-dk));
  display:flex; align-items:center; justify-content:center;
  font-size:1.5rem; margin:0 auto 1rem;
}

/* ── Card em volta dos tabs ── */
[data-testid="stTabs"] {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 20px !important;
  padding: 2rem 1.5rem !important;
}
[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: var(--bg3) !important;
  border-radius: 10px !important;
  margin-bottom: 1.5rem !important;
}

/* ── Link voltar + footer ── */
a.back-link, a.back-link:link, a.back-link:visited {
  display:block; text-align:center; margin-top:1.5rem;
  color:var(--muted) !important; font-size:.83rem; text-decoration:none !important;
}
a.back-link:hover { color:#fff !important; }
.lp-footer {
  text-align:center; padding:1.5rem 2rem;
  background:var(--bg0); color:var(--dim);
  font-size:.8rem; border-top:1px solid var(--border);
  margin-top:3rem;
}
.lp-footer a { color:var(--wine-lt); text-decoration:none; }

/* ── Esconde tooltip "Press Enter to submit form" ── */
[data-testid="InputInstructions"] { display: none !important; }
small[data-testid="InputInstructions"] { display: none !important; }

/* ── Link "Esqueci minha senha" ── */
a.forgot-link, a.forgot-link:link, a.forgot-link:visited {
  display:block; text-align:right; margin-top:.5rem;
  color:var(--muted) !important; font-size:.8rem;
  text-decoration:none !important; cursor:pointer;
}
a.forgot-link:hover { color:var(--wine-lt) !important; }

/* ── Box de recuperação de senha ── */
.recovery-box {
  background:var(--bg2); border:1px solid var(--border);
  border-radius:20px; padding:2rem 1.5rem;
}
.recovery-box h3 { color:#fff; font-size:1.2rem; font-weight:700; margin:0 0 .4rem; }
.recovery-box p  { color:var(--muted); font-size:.86rem; margin:0 0 1.5rem; }

/* ══════════════ MOBILE ══════════════ */
@media (max-width: 767px) {
  .lp-nav { padding: 0 1rem; height: 56px; }
  .lp-links { display: none; }
  .lp-nav-btns .btn-ghost { display: none; }
  .lp-nav-btns .btn-wine { font-size: .78rem; padding: .32rem .8rem; }
  .lp-logo { font-size: 1rem; }
  .main .block-container,
  .stMain .block-container,
  [data-testid="stMain"] .block-container,
  [data-testid="stAppViewBlockContainer"] {
    padding-top: 5rem !important;
  }
  [data-testid="stTabs"] {
    padding: 1.2rem 1rem !important;
  }
  .access-header h2 { font-size: 1.3rem; }
}
</style>
""", unsafe_allow_html=True)

# ── NAV ───────────────────────────────────────────────────────────────────────
st.markdown("""
<nav class="lp-nav">
  <a class="lp-logo" href="/">
    <div class="lp-logo-dot">🔥</div>
    Mr. Incêndio
  </a>
  <div class="lp-links">
    <a href="/">Início</a>
    <a href="/">Como funciona</a>
    <a href="/">Vantagens</a>
    <a href="/">Planos</a>
    <a href="/">Contato</a>
  </div>
  <div class="lp-nav-btns">
    <a class="btn-ghost" href="/" target="_self">Voltar</a>
    <a class="btn-wine"  href="/Acesso" target="_self">Entrar</a>
  </div>
</nav>
""", unsafe_allow_html=True)

# ── CABEÇALHO ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="access-header">
  <div class="access-icon">🔥</div>
  <h2>Comece agora</h2>
  <p>10 créditos grátis ao criar sua conta</p>
</div>
""", unsafe_allow_html=True)

# ── MODO RECUPERAÇÃO (link do e-mail) ─────────────────────────────────────────
if _token_reset:
    st.markdown("""
    <div class="recovery-box">
      <h3>🔑 Criar nova senha</h3>
      <p>Digite e confirme sua nova senha abaixo.</p>
    </div>
    """, unsafe_allow_html=True)
    with st.form("form_nova_senha"):
        nova  = st.text_input("Nova senha", type="password")
        nova2 = st.text_input("Confirmar nova senha", type="password")
        salvar = st.form_submit_button("Salvar nova senha", use_container_width=True)
    if salvar:
        if nova != nova2:
            st.error("As senhas não coincidem.")
        else:
            ok, msg = confirmar_reset(_token_reset, nova)
            if ok:
                st.success(msg)
                st.query_params.clear()
                st.info("Faça login abaixo com sua nova senha.")
                st.rerun()
            else:
                st.error(msg)
    st.stop()

# ── TABS / FORMULÁRIOS ────────────────────────────────────────────────────────
aba_login, aba_cadastro = st.tabs(["Entrar", "Criar conta"])

with aba_login:
    with st.form("form_login"):
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar", use_container_width=True)

    # Link "Esqueci minha senha"
    st.markdown(
        '<a class="forgot-link" href="?recuperar=1">Esqueci minha senha</a>',
        unsafe_allow_html=True
    )

    if entrar:
        if not email or not senha:
            st.error("Preencha e-mail e senha.")
        else:
            resultado = login(email, senha)
            if isinstance(resultado, dict) and resultado.get("bloqueado"):
                st.error(f"🔒 Conta bloqueada por tentativas excessivas. "
                         f"Tente novamente em {resultado['minutos']} minuto(s).")
            elif resultado:
                iniciar_sessao(resultado)
                st.switch_page("pages/1_Chat.py")
            else:
                st.error("E-mail ou senha incorretos.")

    # Formulário de recuperação (modo ?recuperar=1)
    if st.query_params.get("recuperar"):
        st.divider()
        st.markdown("**Recuperar senha**")
        with st.form("form_recuperar"):
            email_rec = st.text_input("Digite seu e-mail cadastrado", key="email_rec")
            enviar = st.form_submit_button("Enviar instruções", use_container_width=True)
        if enviar:
            if not email_rec:
                st.error("Informe seu e-mail.")
            else:
                ok, msg = solicitar_reset(email_rec)
                st.success(msg)

with aba_cadastro:
    # Seletor cascata de tipo de conta — fica FORA do form para reagir imediatamente
    tipo_conta = st.selectbox(
        "Tipo de conta",
        ["👤  Pessoal — projetista autônomo", "🏢  Empresa — equipe e CNPJ"],
        key="tipo_conta_sel",
        label_visibility="visible",
    )
    eh_empresa = "Empresa" in tipo_conta

    if eh_empresa:
        with st.form("form_empresa"):
            st.markdown("**Dados da empresa**")
            e_emp_nome = st.text_input("Razão social",                            key="e_emp_nome")
            e_cnpj     = st.text_input("CNPJ", placeholder="00.000.000/0001-00",  key="e_cnpj")
            st.markdown("**Responsável pela conta**")
            e_nome     = st.text_input("Nome completo",                           key="e_nome")
            e_email    = st.text_input("E-mail",                                  key="e_email")
            e_tel      = st.text_input("Telefone", placeholder="(21) 99999-9999", key="e_tel")
            e_senha    = st.text_input("Senha (mín. 6 caracteres)", type="password", key="e_senha")
            e_senha2   = st.text_input("Confirmar senha",           type="password", key="e_senha2")
            e_termos   = st.checkbox("Li e aceito os [Termos de Uso](/Termos)", key="e_termos")
            e_criar    = st.form_submit_button("Criar conta empresarial", use_container_width=True)
        if e_criar:
            if not e_termos:
                st.error("Você precisa aceitar os Termos de Uso para continuar.")
            elif e_senha != e_senha2:
                st.error("As senhas não coincidem.")
            else:
                ok, msg = registrar(nome=e_nome, email=e_email, senha=e_senha,
                                    tipo="empresa_admin", empresa_nome=e_emp_nome,
                                    cnpj=e_cnpj, telefone=e_tel)
                if ok:
                    st.success(msg)
                    st.info("Agora faça login na aba **Entrar**.")
                else:
                    st.error(msg)
    else:
        with st.form("form_pessoal"):
            p_nome   = st.text_input("Nome completo",                           key="p_nome")
            p_email  = st.text_input("E-mail",                                  key="p_email")
            p_tel    = st.text_input("Telefone", placeholder="(21) 99999-9999", key="p_tel")
            p_cpf    = st.text_input("CPF",      placeholder="000.000.000-00",  key="p_cpf")
            p_senha  = st.text_input("Senha (mín. 6 caracteres)", type="password", key="p_senha")
            p_senha2 = st.text_input("Confirmar senha",           type="password", key="p_senha2")
            p_termos = st.checkbox("Li e aceito os [Termos de Uso](/Termos)", key="p_termos")
            p_criar  = st.form_submit_button("Criar conta grátis", use_container_width=True)
        if p_criar:
            if not p_termos:
                st.error("Você precisa aceitar os Termos de Uso para continuar.")
            elif p_senha != p_senha2:
                st.error("As senhas não coincidem.")
            else:
                ok, msg = registrar(nome=p_nome, email=p_email, senha=p_senha,
                                    tipo="pessoal", telefone=p_tel, cpf=p_cpf)
                if ok:
                    st.success(msg)
                    st.info("Agora faça login na aba **Entrar**.")
                else:
                    st.error(msg)

# ── RODAPÉ ────────────────────────────────────────────────────────────────────
st.markdown('<a class="back-link" href="/">← Voltar para o início</a>', unsafe_allow_html=True)
st.markdown("""
<div class="lp-footer">
  🔥 Mr. Incêndio &nbsp;·&nbsp; Consulta inteligente às normas do Corpo de Bombeiros
  &nbsp;·&nbsp; <a href="/Termos">Termos de Uso</a>
  &nbsp;·&nbsp; © 2026
</div>
""", unsafe_allow_html=True)
