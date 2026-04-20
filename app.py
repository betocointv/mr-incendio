"""
Mr. Incêndio — Landing page.
"""
import streamlit as st
from db import init_db, listar_pacotes
from auth import sessao_logada
from ui import aplicar_tema

st.set_page_config(page_title="Mr. Incêndio", page_icon="🔥", layout="wide")
aplicar_tema()
init_db()

if sessao_logada():
    st.switch_page("pages/1_Chat.py")

pacotes = listar_pacotes()
_modal  = st.query_params.get("modal", "")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Reset Streamlit chrome */
[data-testid="stSidebarNav"],
[data-testid="stSidebar"],
#MainMenu, footer, header,
[data-testid="stToolbar"] { display:none !important; }
.main .block-container,
.stMain .block-container,
[data-testid="stMain"] .block-container,
[data-testid="stAppViewBlockContainer"] {
  padding-top:0 !important; padding-bottom:0 !important;
  max-width:100% !important; padding-left:0 !important; padding-right:0 !important;
}

/* ── Typography ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family:'Inter',sans-serif; box-sizing:border-box; }

/* ── Tokens ── */
:root {
  --wine:    #7a2340;
  --wine-dk: #561629;
  --wine-lt: #c4607a;
  --bg0: #08080e;
  --bg1: #0f0f1e;
  --bg2: #141428;
  --bg3: #1a1a30;
  --border: rgba(255,255,255,0.08);
  --border-wine: rgba(122,35,64,0.45);
  --text:   #f0f0f8;
  --muted:  #9090b8;
  --dim:    #60607a;
}

body, .stApp { background: var(--bg0) !important; }

/* ── Kill Streamlit global link override inside our nav ── */
.lp-nav a { color: inherit !important; text-decoration: none !important; }

/* ── NAV ── */
.lp-nav {
  position:fixed; top:0; left:0; right:0; z-index:9999;
  display:flex; align-items:center; justify-content:space-between;
  padding:0 3rem; height:64px;
  background:rgba(9,9,15,0.85);
  backdrop-filter:blur(16px);
  border-bottom:1px solid var(--border);
  transition:background .3s;
}
a.lp-logo, a.lp-logo:link, a.lp-logo:visited, a.lp-logo:hover, a.lp-logo:active,
.lp-logo, .lp-logo:link, .lp-logo:visited, .lp-logo:hover, .lp-logo:active {
  font-size:1.15rem; font-weight:800; color:#fff !important;
  display:flex; align-items:center; gap:.5rem; text-decoration:none !important; letter-spacing:-.02em;
}
.lp-logo-dot {
  width:30px; height:30px; border-radius:8px;
  background:linear-gradient(135deg,var(--wine),var(--wine-dk));
  display:flex; align-items:center; justify-content:center;
  font-size:.95rem; flex-shrink:0;
}
.lp-links { display:flex; align-items:center; gap:2.5rem; }
.lp-links a, .lp-links a:link, .lp-links a:visited {
  color:var(--muted) !important; text-decoration:none !important; font-size:.88rem; font-weight:500;
  transition:color .2s;
}
.lp-links a:hover, .lp-links a:active { color:#fff !important; text-decoration:none !important; }
.lp-nav-btns { display:flex; gap:.65rem; align-items:center; }
a.btn-ghost, a.btn-ghost:link, a.btn-ghost:visited,
.btn-ghost, .btn-ghost:link, .btn-ghost:visited {
  color:#ddd !important; text-decoration:none !important; font-size:.85rem; font-weight:600;
  padding:.38rem 1rem; border:1.5px solid rgba(255,255,255,0.18);
  border-radius:8px; transition:all .2s; display:inline-block;
}
a.btn-ghost:hover, a.btn-ghost:active, .btn-ghost:hover { border-color:rgba(255,255,255,.5); color:#fff !important; }
a.btn-wine, a.btn-wine:link, a.btn-wine:visited,
.btn-wine, .btn-wine:link, .btn-wine:visited {
  background:linear-gradient(135deg,var(--wine),var(--wine-dk));
  color:white !important; text-decoration:none !important; font-size:.85rem; font-weight:700;
  padding:.4rem 1.1rem; border-radius:8px; transition:all .2s; display:inline-block;
}
a.btn-wine:hover, a.btn-wine:active, .btn-wine:hover { opacity:.88; transform:translateY(-1px); color:white !important; }

/* ── HERO ── */
.hero {
  min-height:100vh; padding-top:64px;
  display:flex; flex-direction:column; align-items:center;
  justify-content:center; text-align:center;
  position:relative; overflow:hidden;
  background:
    radial-gradient(ellipse 80% 60% at 50% -10%, rgba(122,35,64,.55) 0%, transparent 65%),
    var(--bg0);
}
/* dot grid */
.hero::before {
  content:""; position:absolute; inset:0; opacity:.35;
  background-image: radial-gradient(circle, rgba(122,35,64,.5) 1px, transparent 1px);
  background-size: 32px 32px;
  pointer-events:none;
}
.hero-inner { position:relative; z-index:1; padding:3rem 1.5rem 0; max-width:820px; }
.hero-badge {
  display:inline-flex; align-items:center; gap:.5rem;
  background:rgba(122,35,64,.18); border:1px solid var(--border-wine);
  color:#e8b4c0; font-size:.75rem; font-weight:600; padding:.3rem .9rem;
  border-radius:20px; margin-bottom:1.8rem; letter-spacing:.4px;
}
.hero h1 {
  font-size:clamp(2.4rem,5.5vw,4rem); font-weight:800; color:#fff;
  line-height:1.12; margin:0 0 1.3rem; letter-spacing:-.03em;
}
.hero h1 em { font-style:normal; color:var(--wine-lt); }
.hero-sub {
  font-size:clamp(1rem,1.8vw,1.15rem); color:var(--muted);
  max-width:720px; margin:0 auto 2.5rem; line-height:1.7;
  text-align:center !important; width:100%;
}
.hero-actions {
  display:flex; gap:.85rem; justify-content:center; flex-wrap:wrap; margin-bottom:3.5rem;
}
.cta-primary {
  background:linear-gradient(135deg,var(--wine),var(--wine-dk));
  color:white !important; font-size:.95rem; font-weight:700;
  padding:.8rem 2rem; border-radius:10px; text-decoration:none;
  display:inline-flex; align-items:center; gap:.45rem; transition:all .25s;
  box-shadow:0 4px 20px rgba(122,35,64,.4);
}
.cta-primary:hover { transform:translateY(-2px); box-shadow:0 8px 30px rgba(122,35,64,.55); }
.cta-secondary {
  color:#ccc !important; font-size:.95rem; font-weight:600;
  padding:.8rem 2rem; border-radius:10px; border:1.5px solid rgba(255,255,255,.18);
  text-decoration:none; display:inline-flex; align-items:center; gap:.45rem; transition:all .25s;
}
.cta-secondary:hover { border-color:rgba(255,255,255,.5); color:#fff !important; }

/* Stats bar */
.hero-stats {
  display:flex; gap:0; justify-content:center;
  border:1px solid var(--border); border-radius:16px;
  background:rgba(255,255,255,.03); backdrop-filter:blur(8px);
  overflow:hidden; margin:0 auto; flex-wrap:nowrap;
}
.stat-item {
  padding:.85rem 1.6rem; text-align:center; border-right:1px solid var(--border); white-space:nowrap;
}
.stat-item:last-child { border-right:none; }
.stat-num { font-size:1.6rem; font-weight:800; color:#fff; line-height:1; }
.stat-lbl { font-size:.72rem; color:var(--dim); margin-top:.3rem; font-weight:500; }

/* Mockup chat */
.hero-mockup {
  margin-top:3.5rem; position:relative; z-index:1;
  width:100%; max-width:780px; margin-left:auto; margin-right:auto;
}
.mockup-window {
  background:var(--bg2); border:1px solid rgba(255,255,255,.1);
  border-radius:16px 16px 0 0; overflow:hidden;
  box-shadow:0 -8px 60px rgba(122,35,64,.2), 0 0 0 1px rgba(255,255,255,.05);
}
.mockup-bar {
  background:var(--bg3); padding:.65rem 1rem;
  display:flex; align-items:center; gap:.5rem;
  border-bottom:1px solid rgba(255,255,255,.06);
}
.mockup-dot { width:10px; height:10px; border-radius:50%; }
.mockup-body { padding:1.2rem 1.4rem; display:flex; flex-direction:column; gap:.9rem; }
.msg-user {
  align-self:flex-end; background:linear-gradient(135deg,var(--wine),var(--wine-dk));
  color:white; padding:.6rem 1rem; border-radius:12px 12px 2px 12px;
  font-size:.83rem; max-width:75%;
}
.msg-ai {
  align-self:flex-start; background:var(--bg3); border:1px solid rgba(255,255,255,.07);
  color:var(--text); padding:.7rem 1rem; border-radius:12px 12px 12px 2px;
  font-size:.83rem; max-width:85%; line-height:1.55;
}
.msg-ai strong { color:var(--wine-lt); }
.mockup-input {
  background:var(--bg3); border:1px solid rgba(255,255,255,.09); border-radius:0 0 16px 16px;
  padding:.75rem 1rem; display:flex; align-items:center; justify-content:space-between;
}
.mockup-input span { font-size:.8rem; color:var(--dim); }
.mockup-send {
  background:linear-gradient(135deg,var(--wine),var(--wine-dk));
  border-radius:8px; padding:.3rem .7rem; font-size:.75rem; color:white; font-weight:600;
}

/* ── SECTION shared ── */
.section { padding:6rem 2rem; }
.section-inner { max-width:1120px; margin:0 auto; }
.section-alt { background:var(--bg1); border-top:1px solid var(--border); border-bottom:1px solid var(--border); }
.sec-tag {
  font-size:.72rem; font-weight:700; color:var(--wine-lt);
  letter-spacing:1.8px; text-transform:uppercase; margin-bottom:.75rem;
}
.sec-title {
  font-size:clamp(1.8rem,3vw,2.6rem); font-weight:800; color:#fff;
  margin:0 0 1rem; line-height:1.18; letter-spacing:-.02em;
}
.sec-desc { font-size:1rem; color:var(--muted); max-width:520px; line-height:1.7; }
.sec-center { text-align:center; }
.sec-center .sec-desc { margin:0 auto; }

/* ── Feature cards ── */
.feat-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:1.2rem; margin-top:3rem; }
.feat-card {
  background:var(--bg2); border:1px solid var(--border);
  border-radius:14px; padding:1.6rem; display:flex; flex-direction:column; gap:.75rem;
  transition:border-color .2s, transform .2s;
}
.feat-card:hover { border-color:var(--border-wine); transform:translateY(-3px); }
.feat-icon {
  width:44px; height:44px; border-radius:10px;
  background:rgba(122,35,64,.15); border:1px solid var(--border-wine);
  display:flex; align-items:center; justify-content:center; font-size:1.3rem;
}
.feat-card h3 { font-size:.98rem; font-weight:700; color:#fff; margin:0; }
.feat-card p  { font-size:.85rem; color:var(--muted); margin:0; line-height:1.6; }

/* ── Steps ── */
.steps-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:1.5rem; margin-top:3rem; }
.step-card { text-align:center; padding:1.8rem 1.2rem; }
.step-num {
  width:42px; height:42px; border-radius:50%;
  background:linear-gradient(135deg,var(--wine),var(--wine-dk));
  color:white; font-weight:800; font-size:1rem;
  display:inline-flex; align-items:center; justify-content:center; margin-bottom:1rem;
}
.step-card h3 { font-size:.98rem; font-weight:700; color:#fff; margin:0 0 .5rem; }
.step-card p  { font-size:.85rem; color:var(--muted); margin:0; line-height:1.6; }
.step-connector {
  display:flex; align-items:flex-start; justify-content:center;
  position:relative;
}
.step-connector::after {
  content:""; position:absolute; top:21px; left:calc(50% + 30px); right:calc(-50% + 30px);
  height:1px; background:linear-gradient(90deg,var(--wine-dk),transparent);
}

/* ── VS comparison ── */
.vs-grid { display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; margin-top:3rem; }
@media(max-width:640px) { .vs-grid { grid-template-columns:1fr; } }
.vs-col { border-radius:14px; padding:2rem; }
.vs-bad  { background:var(--bg2); border:1px solid var(--border); }
.vs-good { background:rgba(122,35,64,.1); border:1px solid var(--border-wine); }
.vs-col h3 { font-size:1rem; font-weight:700; margin:0 0 1.4rem; }
.vs-list { list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:.8rem; }
.vs-list li { font-size:.86rem; color:var(--muted); display:flex; align-items:flex-start; gap:.65rem; line-height:1.55; }
.vs-list li span { flex-shrink:0; }

/* ── Empresa ── */
.emp-grid { display:grid; grid-template-columns:1fr 1fr; gap:4rem; align-items:center; }
@media(max-width:768px) { .emp-grid { grid-template-columns:1fr; } }
.emp-list { list-style:none; padding:0; margin:1.8rem 0 2rem; display:flex; flex-direction:column; gap:.85rem; }
.emp-list li { display:flex; align-items:flex-start; gap:.75rem; font-size:.92rem; color:#c8c8e0; }
.emp-list li span { color:var(--wine-lt); flex-shrink:0; font-size:1rem; margin-top:.05rem; }
.emp-card {
  background:var(--bg2); border:1px solid var(--border-wine);
  border-radius:18px; padding:2.2rem;
}
.emp-card-title { font-size:.75rem; font-weight:700; color:var(--dim); letter-spacing:1.2px; text-transform:uppercase; margin-bottom:1.2rem; }
.emp-item {
  background:var(--bg3); border:1px solid var(--border);
  border-radius:10px; padding:.7rem 1rem; font-size:.88rem; color:#c0c0d8;
  display:flex; align-items:center; gap:.65rem; margin-bottom:.65rem;
}

/* ── Planos ── */
.plans-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr)); gap:1.2rem; margin-top:3rem; }
.plan-card {
  background:var(--bg2); border:1.5px solid var(--border);
  border-radius:16px; padding:1.8rem 1.5rem; text-align:center; position:relative;
  transition:all .2s;
}
.plan-card:hover { transform:translateY(-3px); }
.plan-card.hi { border-color:var(--border-wine); background:rgba(122,35,64,.09); }
.plan-badge {
  position:absolute; top:-12px; left:50%; transform:translateX(-50%);
  background:linear-gradient(135deg,var(--wine),var(--wine-dk));
  color:white; font-size:.68rem; font-weight:700; padding:2px 12px; border-radius:20px; white-space:nowrap;
}
.plan-name   { font-size:.92rem; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:.8px; margin-bottom:.75rem; }
.plan-cred   { font-size:2.6rem; font-weight:800; color:#fff; line-height:1; }
.plan-cred-l { font-size:.75rem; color:var(--dim); margin-bottom:.9rem; }
.plan-price  { font-size:1.6rem; font-weight:800; color:var(--wine-lt); }
.plan-orig   { font-size:.78rem; color:var(--dim); text-decoration:line-through; }
.plan-pct    { font-size:.78rem; color:var(--wine-lt); font-weight:600; margin-top:.25rem; }
.plan-unit   { font-size:.75rem; color:var(--dim); margin-top:.5rem; }
.plan-btn {
  display:block; margin-top:1.2rem; padding:.65rem 1rem;
  background:linear-gradient(135deg,var(--wine),var(--wine-dk));
  color:#fff !important; font-size:.85rem; font-weight:700;
  border-radius:10px; text-decoration:none !important;
  transition:opacity .2s;
}
.plan-btn:hover { opacity:.85; }

/* ── Estados expansão ── */
.states-row { display:flex; gap:.85rem; justify-content:center; flex-wrap:wrap; margin-top:2rem; }
.state-pill {
  padding:.4rem 1.2rem; border-radius:30px; font-size:.85rem; font-weight:600;
}
.state-active { background:rgba(122,35,64,.18); border:1px solid var(--border-wine); color:#e8b4c0; }
.state-soon   { background:var(--bg2); border:1px solid var(--border); color:var(--dim); }

/* ── FAQ ── */
.faq-list { margin-top:2.5rem; display:flex; flex-direction:column; gap:0; }
.faq-item { border-bottom:1px solid var(--border); padding:1.4rem 0; }
.faq-q { font-size:.96rem; font-weight:600; color:#e0e0f0; margin-bottom:.5rem; }
.faq-a { font-size:.86rem; color:var(--muted); line-height:1.7; }

/* ── Contato ── */
.contact-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:1.2rem; margin-top:3rem; }
.contact-card {
  background:var(--bg2); border:1px solid var(--border);
  border-radius:14px; padding:1.6rem; text-align:center;
  display:flex; flex-direction:column; align-items:center; gap:.5rem;
}
.contact-icon { font-size:1.7rem; }
.contact-lbl  { font-size:.72rem; font-weight:600; color:var(--dim); text-transform:uppercase; letter-spacing:.8px; }
.contact-val  { font-size:.92rem; color:var(--text); font-weight:500; }

/* ── Auth section ── */
.auth-wrap {
  padding:6rem 1.5rem 8rem;
  background:
    radial-gradient(ellipse 60% 40% at 50% 100%, rgba(122,35,64,.18) 0%, transparent 65%),
    var(--bg1);
  border-top:1px solid var(--border);
}
.auth-card {
  max-width:500px; margin:0 auto;
  background:var(--bg2); border:1px solid var(--border);
  border-radius:20px; padding:2.5rem 2rem;
}

/* ── Footer ── */
.lp-footer {
  text-align:center; padding:1.5rem 2rem;
  background:var(--bg0); color:var(--dim);
  font-size:.8rem; border-top:1px solid var(--border);
}
.lp-footer a { color:var(--wine-lt); text-decoration:none; }

/* ── Streamlit tabs fix inside dark card ── */
.auth-card .stTabs [data-baseweb="tab-list"] {
  background:var(--bg3) !important;
}

/* ══════════════ MOBILE ══════════════ */
@media (max-width: 767px) {
  /* Nav: reduz padding, esconde links do meio, compacta botões */
  .lp-nav { padding: 0 1rem; height: 56px; }
  .lp-links { display: none; }
  .lp-nav-btns .btn-ghost { display: none; }
  .lp-nav-btns .btn-wine { font-size: .78rem; padding: .32rem .8rem; }
  .lp-logo { font-size: 1rem; }

  /* Hero: padding menor */
  .hero { padding-top: 56px; }
  .hero-inner { padding: 2rem 1rem 0; }
  .hero h1 { font-size: 2rem; }
  .hero-sub { font-size: .9rem; margin-bottom: 1.8rem; }
  .hero-actions { gap: .55rem; margin-bottom: 2rem; }
  .cta-primary, .cta-secondary { font-size: .85rem; padding: .65rem 1.3rem; }

  /* Stats: 2x2 grid */
  .hero-stats { flex-wrap: wrap; }
  .stat-item {
    flex: 1 1 calc(50% - 1px);
    padding: .7rem 1rem;
    border-right: none !important;
    border-bottom: 1px solid var(--border);
  }
  .stat-item:nth-child(odd)  { border-right: 1px solid var(--border) !important; }
  .stat-item:nth-child(3),
  .stat-item:nth-child(4)    { border-bottom: none; }

  /* Mockup: fonte menor */
  .hero-mockup { margin-top: 2rem; }
  .mockup-body { padding: .8rem .9rem; gap: .7rem; }
  .msg-user, .msg-ai { font-size: .78rem; padding: .5rem .8rem; }

  /* Sections: menos padding vertical */
  .section { padding: 3rem 1.2rem; }
  .sec-title { font-size: 1.6rem; }

  /* Steps: 2 colunas em mobile */
  .steps-grid { grid-template-columns: 1fr 1fr; gap: 1rem; }
  .step-card { padding: 1.2rem .8rem; }

  /* Features: 1 coluna */
  .feat-grid { grid-template-columns: 1fr; }

  /* Planos: 2 colunas */
  .plans-grid { grid-template-columns: 1fr 1fr; gap: .8rem; }
  .plan-card { padding: 1.4rem 1rem; }
  .plan-cred { font-size: 2rem; }

  /* Empresa */
  .emp-card { padding: 1.4rem; }

  /* FAQ */
  .faq-q { font-size: .9rem; }

  /* Contato: 1 coluna */
  .contact-grid { grid-template-columns: 1fr; }

  /* Footer */
  .lp-footer { padding: 1.2rem 1rem; font-size: .75rem; }
}

@media (max-width: 420px) {
  /* Planos: 1 coluna em telas muito pequenas */
  .plans-grid { grid-template-columns: 1fr; }
  .steps-grid { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)

# ── NAV ───────────────────────────────────────────────────────────────────────
st.markdown("""
<script>
function lpScroll(id) {
  var el = document.getElementById(id);
  if (!el) return false;
  var NAV_H = 72;
  // Streamlit's scroll container
  var sc = document.querySelector('[data-testid="stAppViewContainer"]')
        || document.querySelector('.main')
        || document.documentElement;
  var elTop = el.getBoundingClientRect().top;
  var scTop = sc === document.documentElement ? window.pageYOffset : sc.scrollTop;
  var target = scTop + elTop - NAV_H;
  if (sc === document.documentElement) {
    window.scrollTo({top: target, behavior: 'smooth'});
  } else {
    sc.scrollTo({top: target, behavior: 'smooth'});
  }
  return false;
}
</script>
<nav class="lp-nav">
  <a class="lp-logo" href="#" onclick="lpScroll('inicio');return false;">
    <div class="lp-logo-dot">🔥</div>
    Mr. Incêndio
  </a>
  <div class="lp-links">
    <a href="#inicio"    onclick="return lpScroll('inicio');">Início</a>
    <a href="#como"      onclick="return lpScroll('como');">Como funciona</a>
    <a href="#vantagens" onclick="return lpScroll('vantagens');">Vantagens</a>
    <a href="#planos"    onclick="return lpScroll('planos');">Planos</a>
    <a href="#contato"   onclick="return lpScroll('contato');">Contato</a>
  </div>
  <div class="lp-nav-btns">
    <a class="btn-ghost" href="/Acesso" onclick="window.parent.location.href='/Acesso';return false;">Entrar</a>
    <a class="btn-wine"  href="/Acesso" onclick="window.parent.location.href='/Acesso';return false;">Criar conta grátis</a>
  </div>
</nav>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div id="inicio" class="hero">
  <div class="hero-inner">
    <div class="hero-badge">🚒 Corpo de Bombeiros do Estado do Rio de Janeiro</div>
    <h1>Consulte as <em>Normas Técnicas</em><br>do CBMERJ com IA</h1>
    <p class="hero-sub">
      Respostas diretas em segundos — sem abrir PDF, sem interpretar tabelas, sem perder tempo. Só a norma certa do RJ.
    </p>
    <div class="hero-actions">
      <a class="cta-primary"    href="/Acesso" onclick="window.parent.location.href='/Acesso';return false;">🚀 Começar grátis</a>
      <a class="cta-secondary"  href="#como"   onclick="return lpScroll('como');">Como funciona →</a>
    </div>
    <div class="hero-stats">
      <div class="stat-item"><div class="stat-num">3.310</div><div class="stat-lbl">Trechos indexados</div></div>
      <div class="stat-item"><div class="stat-num">100%</div><div class="stat-lbl">NTs oficiais CBMERJ</div></div>
      <div class="stat-item"><div class="stat-num">&lt;5s</div><div class="stat-lbl">Tempo de resposta</div></div>
      <div class="stat-item"><div class="stat-num">10</div><div class="stat-lbl">Créditos grátis</div></div>
    </div>
  </div>
  <div class="hero-mockup">
    <div class="mockup-window">
      <div class="mockup-bar">
        <div class="mockup-dot" style="background:#ff5f57;"></div>
        <div class="mockup-dot" style="background:#febc2e;"></div>
        <div class="mockup-dot" style="background:#28c840;"></div>
        <span style="margin-left:.5rem;font-size:.75rem;color:#555;">Mr. Incêndio — Chat</span>
      </div>
      <div class="mockup-body">
        <div class="msg-user">Quando é obrigatório sprinkler em edifício residencial?</div>
        <div class="msg-ai">
          Conforme a <strong>NT 23 – item 5.1.2</strong>, o sistema de chuveiros automáticos (sprinkler) é obrigatório em edificações residenciais multifamiliares com altura superior a <strong>30 metros</strong> ou área total construída acima de <strong>10.000 m²</strong>, classificadas nos grupos A-2, A-3 ou A-4 do COSCIP. Edificações com subsolo de uso coletivo também ficam sujeitas à exigência independente da altura.
        </div>
      </div>
      <div class="mockup-input">
        <span>Faça sua pergunta sobre as NTs do CBMERJ...</span>
        <div class="mockup-send">Enviar</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── COMO FUNCIONA ─────────────────────────────────────────────────────────────
st.markdown("""
<div id="como" class="section section-alt">
  <div class="section-inner">
    <div style="text-align:center;">
      <div class="sec-tag">Como funciona</div>
      <h2 class="sec-title">Da pergunta à resposta em 4 passos</h2>
    </div>
    <div class="steps-grid" style="margin-top:3rem;">
      <div class="step-card">
        <div class="step-num">1</div>
        <h3>Crie sua conta</h3>
        <p>Cadastro gratuito em menos de 1 minuto. Ganhe 10 créditos de boas-vindas imediatamente.</p>
      </div>
      <div class="step-card">
        <div class="step-num">2</div>
        <h3>Digite sua pergunta</h3>
        <p>Escreva em português natural — "sprinkler em residencial?", "altura mínima de extintor", qualquer dúvida técnica.</p>
      </div>
      <div class="step-card">
        <div class="step-num">3</div>
        <h3>IA busca nas NTs</h3>
        <p>O sistema varre os 3.310 trechos indexados das NTs e COSCIP oficiais do CBMERJ em tempo real.</p>
      </div>
      <div class="step-card">
        <div class="step-num">4</div>
        <h3>Resposta com citação</h3>
        <p>Você recebe a resposta com número da NT e item específico. Sem achismo — só norma oficial.</p>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── VS GOOGLE ─────────────────────────────────────────────────────────────────
st.markdown("""
<div id="vantagens" class="section">
  <div class="section-inner">
    <div class="sec-tag">Por que usar?</div>
    <h2 class="sec-title">Mr. Incêndio vs Google</h2>
    <p class="sec-desc" style="margin-bottom:0;">
      Projetistas perdem horas abrindo PDFs e interpretando tabelas. Veja a diferença real.
    </p>
    <div class="vs-grid">
      <div class="vs-col vs-bad">
        <h3 style="color:#666;">🔍 Google / PDF</h3>
        <ul class="vs-list">
          <li><span>❌</span>Abre dezenas de links e PDFs de 200+ páginas</li>
          <li><span>❌</span>Mistura blogues, fóruns e normas de outros estados</li>
          <li><span>❌</span>Você interpreta tabelas complexas sozinho</li>
          <li><span>❌</span>Sem citação exata — difícil apresentar ao cliente</li>
          <li><span>❌</span>Fácil errar o estado ou a versão da norma</li>
          <li><span>❌</span>30–60 minutos por consulta</li>
        </ul>
      </div>
      <div class="vs-col vs-good">
        <h3 style="color:#e8b4c0;">🔥 Mr. Incêndio</h3>
        <ul class="vs-list">
          <li><span>✅</span>Resposta direta em menos de 5 segundos</li>
          <li><span>✅</span>Apenas NTs e COSCIP oficiais do CBMERJ</li>
          <li><span>✅</span>IA interpreta a tabela e entrega o valor exato</li>
          <li><span>✅</span>Cita NT + item — pronto para usar no projeto</li>
          <li><span>✅</span>Normas corretas do RJ, sempre atualizadas</li>
          <li><span>✅</span>Menos de 1 minuto por consulta</li>
        </ul>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── FEATURES ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section section-alt">
  <div class="section-inner">
    <div style="text-align:center;">
      <div class="sec-tag">Funcionalidades</div>
      <h2 class="sec-title">Tudo que o projetista precisa</h2>
    </div>
    <div class="feat-grid">
      <div class="feat-card">
        <div class="feat-icon">🎯</div>
        <h3>Respostas precisas com citação</h3>
        <p>A IA cita o número da NT e o item específico. Você sabe exatamente onde a informação está.</p>
      </div>
      <div class="feat-card">
        <div class="feat-icon">📚</div>
        <h3>Base oficial CBMERJ completa</h3>
        <p>Todas as NTs dos grupos 1–5 + COSCIP (Decreto 42/2018) indexados. Mais de 3.300 trechos técnicos.</p>
      </div>
      <div class="feat-card">
        <div class="feat-icon">💬</div>
        <h3>Chat com histórico salvo</h3>
        <p>Faça perguntas em sequência, refine a consulta e salve conversas para referência futura no projeto.</p>
      </div>
      <div class="feat-card">
        <div class="feat-icon">⚡</div>
        <h3>Créditos sem validade</h3>
        <p>Compre uma vez e use quando precisar. Sem mensalidade, sem perda de crédito por prazo expirado.</p>
      </div>
      <div class="feat-card">
        <div class="feat-icon">🏆</div>
        <h3>Pontos e recompensas</h3>
        <p>Ganhe 1 ponto por consulta e troque 50 pontos por 5 créditos grátis. Quanto mais usa, mais ganha.</p>
      </div>
      <div class="feat-card">
        <div class="feat-icon">🏢</div>
        <h3>Gestão de equipes</h3>
        <p>Conta empresarial com pool de créditos compartilhado, controle de consumo por colaborador.</p>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── PARA EMPRESAS ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="section">
  <div class="section-inner">
    <div class="emp-grid">
      <div>
        <div class="sec-tag">Para empresas</div>
        <h2 class="sec-title">Eleve a produtividade<br>do seu escritório</h2>
        <p class="sec-desc">
          Uma conta empresarial com CNPJ para toda a equipe, créditos compartilhados
          e visibilidade total do consumo por colaborador.
        </p>
        <ul class="emp-list">
          <li><span>✔</span>Conta administrativa + funcionários vinculados</li>
          <li><span>✔</span>Pool de créditos compartilhado entre a equipe</li>
          <li><span>✔</span>Painel de consumo por colaborador</li>
          <li><span>✔</span>Adicione e remova membros a qualquer momento</li>
          <li><span>✔</span>40% de desconto no pacote Empresarial</li>
          <li><span>✔</span>Cadastro com CNPJ — nota fiscal disponível</li>
        </ul>
        <a class="cta-primary" style="display:inline-flex;width:fit-content;" href="/Acesso" onclick="window.parent.location.href='/Acesso';return false;">
          🏢 Criar conta empresarial
        </a>
      </div>
      <div class="emp-card">
        <div class="emp-card-title">Ideal para</div>
        <div class="emp-item">📐 Escritórios de arquitetura e engenharia</div>
        <div class="emp-item">🔧 Consultorias em segurança contra incêndio</div>
        <div class="emp-item">🏗️ Construtoras e incorporadoras</div>
        <div class="emp-item">🏢 Departamentos de facilities e segurança</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── PLANOS ────────────────────────────────────────────────────────────────────
html_plans = ""
for p in pacotes:
    hi = p["desconto_pct"] >= 20
    badge = '<div class="plan-badge">⭐ MAIS POPULAR</div>' if p["desconto_pct"] == 30 else ""
    riscado = ""
    pct = ""
    if p["desconto_pct"]:
        orig = p["preco_brl"] / (1 - p["desconto_pct"] / 100)
        riscado = f'<div class="plan-orig">R$ {orig:.2f}</div>'
        pct = f'<div class="plan-pct">{p["desconto_pct"]}% OFF</div>'
    cls = "plan-card hi" if hi else "plan-card"
    html_plans += (
        f'<div class="{cls}">'
        f'{badge}'
        f'<div class="plan-name">{p["nome"]}</div>'
        f'<div class="plan-cred">{p["creditos"]}</div>'
        f'<div class="plan-cred-l">créditos</div>'
        f'{riscado}'
        f'<div class="plan-price">R$ {p["preco_brl"]:.2f}</div>'
        f'{pct}'
        f'<div class="plan-unit">R$ {p["preco_brl"]/p["creditos"]*100:.1f} por 100 créditos</div>'
        f'<a class="plan-btn" href="/Acesso" onclick="window.parent.location.href=\'/Acesso\';return false;">Quero este plano</a>'
        f'</div>'
    )

st.markdown(f"""
<div id="planos" class="section section-alt">
  <div class="section-inner">
    <div style="text-align:center;">
      <div class="sec-tag">Preços</div>
      <h2 class="sec-title">Simples e transparente</h2>
      <p class="sec-desc" style="margin:0 auto 3rem;">
        Sem mensalidade. Pague pelo que usar. Créditos sem prazo de validade.
      </p>
    </div>
    <div class="plans-grid">{html_plans}</div>
    <p style="text-align:center;font-size:.83rem;color:var(--dim);margin-top:1.5rem;">
      🎁 Todo cadastro recebe <strong style="color:var(--wine-lt);">10 créditos grátis</strong> · Plano Empresarial exige CNPJ
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── EXPANSÃO ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section" style="text-align:center;">
  <div class="section-inner">
    <div style="font-size:2.5rem;margin-bottom:1rem;">🗺️</div>
    <div class="sec-tag" style="justify-content:center;display:flex;">Expansão</div>
    <h2 class="sec-title" style="text-align:center;">Em breve: outros estados</h2>
    <p class="sec-desc" style="margin:0 auto 2rem;">
      Cada estado tem suas próprias normas de prevenção a incêndio.
      Hoje cobrimos o <strong style="color:var(--wine-lt);">CBMERJ (RJ)</strong> com 100% das NTs.
      SP, MG e ES chegam em breve.
    </p>
    <div class="states-row">
      <div class="state-pill state-active">🔥 RJ — Disponível agora</div>
      <div class="state-pill state-soon">⏳ SP — Em breve</div>
      <div class="state-pill state-soon">⏳ MG — Em breve</div>
      <div class="state-pill state-soon">⏳ ES — Em breve</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── FAQ ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section section-alt">
  <div class="section-inner" style="max-width:760px;">
    <div class="sec-tag">FAQ</div>
    <h2 class="sec-title">Perguntas frequentes</h2>
    <div class="faq-list">
      <div class="faq-item">
        <div class="faq-q">O sistema substitui a consulta direta ao CBMERJ?</div>
        <div class="faq-a">Não. O sistema facilita o acesso e a interpretação das normas técnicas oficiais, com caráter informativo. Para aprovações formais e laudos, consulte sempre um profissional habilitado e o CBMERJ.</div>
      </div>
      <div class="faq-item">
        <div class="faq-q">As normas estão atualizadas?</div>
        <div class="faq-a">O índice é atualizado periodicamente com as NTs e o COSCIP vigentes publicados pelo CBMERJ. O usuário é responsável por verificar a vigência da norma consultada.</div>
      </div>
      <div class="faq-item">
        <div class="faq-q">Os créditos expiram?</div>
        <div class="faq-a">Não. Créditos adquiridos não têm prazo de validade e podem ser usados a qualquer momento enquanto a conta estiver ativa.</div>
      </div>
      <div class="faq-item">
        <div class="faq-q">Posso usar para normas de outros estados?</div>
        <div class="faq-a">Atualmente apenas o CBMERJ (RJ). Normas de SP, MG e ES estão sendo indexadas e serão lançadas em breve. Cada estado tem legislação própria.</div>
      </div>
      <div class="faq-item">
        <div class="faq-q">Como funciona a conta empresarial?</div>
        <div class="faq-a">O administrador cadastra a empresa com CNPJ, adiciona colaboradores e gerencia um pool de créditos compartilhados. É possível ver o consumo por funcionário a qualquer momento.</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── CONTATO ───────────────────────────────────────────────────────────────────
st.markdown("""
<div id="contato" class="section">
  <div class="section-inner">
    <div style="text-align:center;">
      <div class="sec-tag">Contato</div>
      <h2 class="sec-title">Fale com a gente</h2>
      <p class="sec-desc" style="margin:0 auto 0;">Dúvidas, sugestões ou suporte? Estamos aqui.</p>
    </div>
    <div class="contact-grid">
      <div class="contact-card">
        <div class="contact-icon">📧</div>
        <div class="contact-lbl">E-mail</div>
        <div class="contact-val">contato@mrincendio.app</div>
      </div>
      <div class="contact-card">
        <div class="contact-icon">💬</div>
        <div class="contact-lbl">WhatsApp</div>
        <div class="contact-val">(21) 9 9999-9999</div>
      </div>
      <div class="contact-card">
        <div class="contact-icon">🕐</div>
        <div class="contact-lbl">Atendimento</div>
        <div class="contact-val">Seg – Sex, 8h às 18h</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="lp-footer">
  🔥 Mr. Incêndio &nbsp;·&nbsp; Consulta inteligente às normas do Corpo de Bombeiros
  &nbsp;·&nbsp; <a href="/Termos">Termos de Uso</a>
  &nbsp;·&nbsp; © 2026
</div>
""", unsafe_allow_html=True)
