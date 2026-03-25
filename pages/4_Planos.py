# -*- coding: utf-8 -*-
"""
Créditos & Planos — saldo, histórico, pacotes e informações de preço.
Acessível sem login (exibe seção de saldo apenas para logados).
"""

from __future__ import annotations

import streamlit as st
from db import listar_pacotes, listar_transacoes, init_db
from ui import aplicar_tema, tema_cores, nav_inferior, header_usuario
from auth import sessao_logada, get_usuario_sessao, fazer_logout
from creditos import (badge_atual, proximo_badge, trocar_pontos,
                      PONTOS_PARA_TROCAR, CREDITOS_POR_TROCA)

st.set_page_config(page_title="Créditos – Mr. Incêndio", page_icon="💳", layout="wide")
init_db()
aplicar_tema()

tc = tema_cores()

# ── Sidebar (apenas logados) ───────────────────────────────────────────────────
usuario = None
if sessao_logada():
    usuario = get_usuario_sessao()
    if not usuario:
        fazer_logout()
        st.rerun()

    badge = badge_atual(usuario["pontos"])
    with st.sidebar:
        import html as _html
        st.markdown(f"""
        <div style="margin-bottom:1rem;">
          <div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.6rem;">
            <div style="width:34px;height:34px;border-radius:9px;
                        background:linear-gradient(135deg,#7a2340,#561629);
                        display:flex;align-items:center;justify-content:center;
                        font-size:1rem;flex-shrink:0;">🔥</div>
            <span style="font-size:1rem;font-weight:800;color:#fff;">Mr. Incêndio</span>
          </div>
          <div style="font-size:.88rem;font-weight:600;color:#f0f0f8;margin-bottom:.3rem;">
            {_html.escape(usuario["nome"])}
          </div>
          <span class="badge-chip">{badge}</span>
          <div style="margin-top:.5rem;font-size:.82rem;color:#9090b8;">
            💳 <strong style="color:#f0f0f8;">{usuario["creditos"]:.0f}</strong>&nbsp;&nbsp;
            ⭐ <strong style="color:#f0f0f8;">{usuario["pontos"]}</strong>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
        if st.button("🚪 Sair", use_container_width=True):
            fazer_logout()
            st.rerun()

# ── Seção de saldo (apenas logados) ───────────────────────────────────────────
if usuario:
    uid = usuario["id"]
    header_usuario(usuario["nome"], usuario["creditos"], usuario["pontos"],
                   badge_atual(usuario["pontos"]))

    st.markdown("### 💳 Meus Créditos")

    col1, col2, col3 = st.columns(3)
    proximo = proximo_badge(usuario["pontos"])
    with col1:
        st.metric("💳 Saldo de Créditos", f"{usuario['creditos']:.0f}")
    with col2:
        st.metric("⭐ Pontos acumulados", usuario["pontos"])
    with col3:
        st.metric("🏅 Badge atual", badge_atual(usuario["pontos"]))

    if proximo:
        progresso = usuario["pontos"] / proximo["meta"]
        st.markdown(f"**Próximo badge:** {proximo['nome']} — faltam **{proximo['faltam']} consultas**")
        st.progress(min(progresso, 1.0))
    else:
        st.success("🏆 Você atingiu o nível máximo — Mestre CBMERJ!")

    st.divider()

    # ── Trocar pontos ──────────────────────────────────────────────────────────
    st.markdown("#### 🔄 Trocar pontos por créditos")
    st.caption(f"**{PONTOS_PARA_TROCAR} pontos = {CREDITOS_POR_TROCA} créditos** | "
               f"Você tem **{usuario['pontos']} pontos**")

    col_t, col_info = st.columns([1, 2])
    with col_t:
        pode_trocar = usuario["pontos"] >= PONTOS_PARA_TROCAR
        if st.button(
            f"Trocar {PONTOS_PARA_TROCAR} pts → {CREDITOS_POR_TROCA} cred.",
            use_container_width=True,
            disabled=not pode_trocar
        ):
            ok, msg = trocar_pontos(uid)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    with col_info:
        if not pode_trocar:
            faltam = PONTOS_PARA_TROCAR - usuario["pontos"]
            st.info(f"Faltam **{faltam} pontos** para poder trocar. "
                    f"Faça mais consultas para acumular pontos!")

    st.divider()

    # ── Histórico de transações ────────────────────────────────────────────────
    st.markdown("#### 📋 Histórico de transações")
    transacoes = listar_transacoes(uid, 30)

    if not transacoes:
        st.info("Nenhuma transação ainda. Faça sua primeira consulta!")
    else:
        LABELS = {
            "uso":               "🔍 Consulta",
            "compra":            "💰 Compra",
            "bonus_boas_vindas": "🎁 Boas-vindas",
            "troca_pontos":      "🔄 Troca de pontos",
        }
        dados = []
        for t in transacoes:
            sinal = "+" if t["creditos"] >= 0 else ""
            dados.append({
                "Data":      t["criado_em"][:16].replace("T", " "),
                "Tipo":      LABELS.get(t["tipo"], t["tipo"]),
                "Créditos":  f"{sinal}{t['creditos']:.0f}",
                "Descrição": t["descricao"] or "",
            })
        st.dataframe(dados, use_container_width=True, hide_index=True)

    st.divider()

# ── Cabeçalho público (apenas não logados) ────────────────────────────────────
elif not usuario:
    st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;">
    <div style="font-size:0.85rem;color:#7a2340;font-weight:600;
                letter-spacing:0.1em;text-transform:uppercase;">
        PLANOS & PREÇOS
    </div>
    <div style="font-size:2rem;font-weight:700;margin-top:0.5rem;">
        Escolha o plano ideal para você
    </div>
    <div style="font-size:0.95rem;color:#8888bb;margin-top:0.5rem;">
        Sem mensalidade. Pague apenas pelo que usar. Sem surpresas.
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ⚙️ Como funciona")
    col1, col2, col3, col4 = st.columns(4)
    passos = [
        ("1️⃣", "Crie sua conta", "Cadastro gratuito em segundos. Ganhe 10 créditos de boas-vindas."),
        ("2️⃣", "Compre créditos", "A partir de R$ 29,90. Quanto mais, mais barato por crédito."),
        ("3️⃣", "Consulte as NTs", "1 pergunta = 1 crédito. Respostas diretas com base nas normas oficiais."),
        ("4️⃣", "Ganhe pontos", "Cada consulta vale pontos. Troque por créditos grátis."),
    ]
    for col, (num, titulo, desc) in zip([col1, col2, col3, col4], passos):
        with col:
            st.markdown(
                f'<div class="card" style="text-align:center;">'
                f'<div style="font-size:1.8rem;">{num}</div>'
                f'<div style="font-weight:600;margin:0.5rem 0 0.3rem;">{titulo}</div>'
                f'<div class="card-sub">{desc}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
    st.markdown("---")

# ── Pacotes de créditos ────────────────────────────────────────────────────────
st.markdown("#### 💰 Pacotes de créditos")
pacotes = listar_pacotes()

cols = st.columns(min(len(pacotes), 4))
for col, p in zip(cols, pacotes):
    destaque = p["desconto_pct"] >= 30
    borda = "#7a2340" if destaque else tc['border']

    html_popular = (
        '<div style="position:absolute;top:-12px;left:50%;transform:translateX(-50%);'
        'background:#7a2340;color:white;font-size:0.7rem;font-weight:700;'
        'padding:2px 12px;border-radius:20px;">MAIS POPULAR</div>'
        if destaque else ""
    )
    preco_original = p["preco_brl"] / (1 - p["desconto_pct"] / 100) if p["desconto_pct"] else 0
    html_riscado = (
        f'<div style="font-size:0.8rem;color:{tc["text_dim"]};text-decoration:line-through;">'
        f'R$ {preco_original:.2f}</div>'
        if p["desconto_pct"] else ""
    )
    html_desconto = (
        f'<div style="font-size:0.75rem;color:#7a2340;font-weight:600;">'
        f'{p["desconto_pct"]}% de desconto</div>'
        if p["desconto_pct"] else ""
    )
    custo_100 = p['preco_brl'] / p['creditos'] * 100 if p['creditos'] else 0

    # Plano Empresarial: só disponível para empresa_admin
    tipo_usuario = usuario.get("tipo", "") if usuario else ""
    exclusivo_empresa = p["desconto_pct"] >= 40
    bloqueado = exclusivo_empresa and tipo_usuario not in ("empresa_admin", "admin")

    if bloqueado:
        borda = tc["border"]
        html_lock = (
            '<div style="position:absolute;top:-12px;left:50%;transform:translateX(-50%);'
            'background:#555;color:white;font-size:0.7rem;font-weight:700;'
            'padding:2px 12px;border-radius:20px;">🏢 APENAS EMPRESAS</div>'
        )
    else:
        html_lock = ""

    with col:
        opacidade = "opacity:0.55;" if bloqueado else ""
        html_card = (
            f'<div style="border:2px solid {borda};border-radius:16px;padding:1.5rem;text-align:center;'
            f'background:{tc["surface"]};position:relative;{opacidade}">'
            f'{html_popular}{html_lock}'
            f'<div style="font-size:1.1rem;font-weight:700;margin-bottom:0.5rem;color:{tc["text"]};">{p["nome"]}</div>'
            f'<div style="font-size:2.5rem;font-weight:800;color:#7a2340;">{p["creditos"]}</div>'
            f'<div style="font-size:0.85rem;color:{tc["text_muted"]};margin-bottom:0.8rem;">créditos</div>'
            f'{html_riscado}'
            f'<div style="font-size:1.4rem;font-weight:700;color:{tc["text"]};">R$ {p["preco_brl"]:.2f}</div>'
            f'{html_desconto}'
            f'<div style="font-size:0.72rem;color:{tc["text_muted"]};margin-top:0.5rem;">'
            f'R$ {custo_100:.1f} por 100 créditos</div>'
            f'</div>'
        )
        st.markdown(html_card, unsafe_allow_html=True)
        st.markdown(" ")
        if bloqueado:
            st.button("🔒 Exclusivo para Empresas", key=f"plano_{p['id']}",
                      use_container_width=True, disabled=True)
        elif st.button("Quero este plano", key=f"plano_{p['id']}", use_container_width=True):
            if not usuario:
                st.session_state.plano_selecionado = p["id"]
                st.switch_page("pages/0_Acesso.py")
            else:
                st.session_state["plano_pagamento_id"] = p["id"]
                st.switch_page("pages/8_Pagamento.py")


st.markdown("---")

# ── Comparação de perfis ───────────────────────────────────────────────────────
st.markdown("#### 👤 Para quem é cada plano?")
col1, col2 = st.columns(2)
with col1:
    st.markdown(
        f'<div class="card">'
        f'<div style="font-size:1.1rem;font-weight:700;margin-bottom:0.8rem;">👷 Projetista Autônomo</div>'
        f'<ul style="color:{tc["text_muted"]};font-size:0.88rem;padding-left:1.2rem;line-height:1.8;">'
        f'<li>Conta individual</li>'
        f'<li>Paga por uso — sem mensalidade</li>'
        f'<li>Ideal para consultas pontuais</li>'
        f'<li>Ganhe pontos a cada consulta</li>'
        f'<li>Recomendado: Básico (R$ 29,90) ou Profissional (R$ 69,90)</li>'
        f'</ul></div>',
        unsafe_allow_html=True
    )
with col2:
    st.markdown(
        f'<div class="card">'
        f'<div style="font-size:1.1rem;font-weight:700;margin-bottom:0.8rem;">🏢 Empresa</div>'
        f'<ul style="color:{tc["text_muted"]};font-size:0.88rem;padding-left:1.2rem;line-height:1.8;">'
        f'<li>Conta administrativa + equipe</li>'
        f'<li>Créditos compartilhados entre funcionários</li>'
        f'<li>Visibilidade de consumo por colaborador</li>'
        f'<li>Adicione e remova membros facilmente</li>'
        f'<li>Recomendado: Premium (R$ 149,90) ou Empresarial (R$ 199,90)</li>'
        f'</ul></div>',
        unsafe_allow_html=True
    )

st.markdown("---")

# ── Gamificação ────────────────────────────────────────────────────────────────
st.markdown("#### 🎮 Sistema de pontos e badges")
col1, col2, col3 = st.columns(3)
gamif = [
    ("⭐", "Ganhe pontos", "1 ponto por consulta realizada"),
    ("🏅", "Conquiste badges", "Iniciante → Projetista → Especialista → Mestre CBMERJ"),
    ("🔄", "Troque por créditos", "50 pontos = 5 créditos grátis"),
]
for col, (icon, titulo, desc) in zip([col1, col2, col3], gamif):
    with col:
        st.markdown(
            f'<div class="card" style="text-align:center;">'
            f'<div style="font-size:1.5rem;">{icon}</div>'
            f'<div style="font-weight:600;margin:0.4rem 0;">{titulo}</div>'
            f'<div class="card-sub">{desc}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown("---")

# ── FAQ ────────────────────────────────────────────────────────────────────────
st.markdown("#### ❓ Perguntas frequentes")
with st.expander("O que é um crédito?"):
    st.write("Um crédito equivale a uma consulta ao sistema. "
             "Você faz uma pergunta e o sistema responde com base nas NTs do CBMERJ. "
             "Cada resposta consome 1 crédito do seu saldo.")
with st.expander("Os créditos expiram?"):
    st.write("Não. Os créditos não têm prazo de validade. "
             "Você pode comprar e usar quando quiser.")
with st.expander("Posso testar antes de comprar?"):
    st.write("Sim! Ao criar sua conta gratuitamente, você recebe "
             "10 créditos de boas-vindas para testar o sistema sem custo.")
with st.expander("Como funciona para empresas?"):
    st.write("O administrador da empresa cria a conta corporativa, "
             "compra créditos para o pool da empresa e adiciona os colaboradores. "
             "Todos os funcionários compartilham o mesmo saldo de créditos, "
             "e o administrador consegue ver o consumo individual de cada um.")
with st.expander("Quais normas estão disponíveis?"):
    st.write("O sistema inclui todas as Notas Técnicas (NTs) do CBMERJ, "
             "grupos 1 a 5, além do COSCIP. "
             "São mais de 50 documentos técnicos indexados e pesquisáveis.")

st.markdown("---")

# ── CTA final (apenas não logados) ────────────────────────────────────────────
if not usuario:
    st.markdown("""
<div style="text-align:center;padding:2rem 0;">
    <div style="font-size:1.4rem;font-weight:700;">Pronto para começar?</div>
    <div style="font-size:0.9rem;color:#8888bb;margin-top:0.3rem;">
        Crie sua conta gratuitamente e ganhe 10 créditos de boas-vindas.
    </div>
</div>
""", unsafe_allow_html=True)
    col_c, col_l, _ = st.columns([1, 1, 2])
    with col_c:
        if st.button("🚀 Criar conta grátis", use_container_width=True):
            st.switch_page("pages/0_Acesso.py")
    with col_l:
        if st.button("🔑 Já tenho conta", use_container_width=True):
            st.switch_page("pages/0_Acesso.py")

st.markdown(" ")

# ── Navegação inferior ─────────────────────────────────────────────────────────
if usuario:
    nav_inferior("planos", usuario.get("tipo", "pessoal"))
