# -*- coding: utf-8 -*-
"""
Pontos, badges e ranking — gamificação completa.
"""

from __future__ import annotations

import streamlit as st
from auth import sessao_logada, get_usuario_sessao, fazer_logout
from creditos import (badge_atual, badges_conquistados, proximo_badge,
                      trocar_pontos, PONTOS_PARA_TROCAR, CREDITOS_POR_TROCA,
                      total_consultas, BADGES)
from db import ranking_pontos, init_db
from ui import aplicar_tema, nav_inferior, header_usuario, tema_cores

st.set_page_config(page_title="Pontos – Mr. Incêndio", page_icon="⭐", layout="wide")
init_db()
aplicar_tema()

if not sessao_logada():
    st.warning("Faça login para acessar.")
    st.page_link("app.py", label="← Ir para o login")
    st.stop()

usuario = get_usuario_sessao()
if not usuario:
    fazer_logout()
    st.rerun()

uid    = usuario["id"]
pontos = usuario["pontos"]
badge  = badge_atual(pontos)
tc     = tema_cores()
proximo = proximo_badge(pontos)
conquistados = badges_conquistados(pontos)
consultas = total_consultas(uid)

header_usuario(usuario["nome"], usuario["creditos"], pontos, badge)
st.markdown("### ⭐ Pontos & Conquistas")
nav_inferior("pontos", usuario["tipo"])

# ── Métricas ──────────────────────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("⭐ Pontos totais", pontos)
with col2:
    st.metric("🔍 Consultas realizadas", consultas)
with col3:
    st.metric("🏅 Badges conquistados", len(conquistados))

st.divider()

# ── Badge atual e progresso ────────────────────────────────────────────────────
st.markdown("#### 🏅 Seu nível atual")

col_badge, col_prog = st.columns([1, 2])
with col_badge:
    st.markdown(f"""
    <div style="text-align:center;padding:1.5rem;background:linear-gradient(135deg,#7a2340,#c0392b);
                border-radius:16px;">
        <div style="font-size:2.5rem;">{badge.split()[0]}</div>
        <div style="font-size:1rem;font-weight:700;color:white;margin-top:0.5rem;">
            {' '.join(badge.split()[1:])}
        </div>
        <div style="font-size:0.75rem;color:rgba(255,255,255,0.8);margin-top:0.3rem;">
            {pontos} pontos
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_prog:
    if proximo:
        pct = pontos / proximo["meta"]
        st.markdown(f"**Próximo nível:** {proximo['nome']}")
        st.markdown(f"Faltam **{proximo['faltam']} pontos** ({proximo['meta'] - pontos} consultas)")
        st.progress(min(pct, 1.0))
        st.caption(f"Cada consulta vale 1 ponto · {proximo['faltam']} consultas para o próximo badge")
    else:
        st.success("🏆 **Parabéns! Você alcançou o nível máximo.**")
        st.markdown("Você é um verdadeiro especialista nas NTs do CBMERJ!")

st.divider()

# ── Todos os badges ────────────────────────────────────────────────────────────
st.markdown("#### 🎯 Todos os badges")

cols = st.columns(len(BADGES) + 1)

# Badge inicial
with cols[0]:
    conquistou = True  # Todo mundo começa aqui
    bg  = tc['surface']  if conquistou else tc['surface2']
    brd = '#7a2340'      if conquistou else tc['border']
    st.markdown(f"""
    <div style="text-align:center;padding:1rem;
                background:{bg};
                border:1px solid {brd};
                border-radius:12px;opacity:{'1' if conquistou else '0.5'}">
        <div style="font-size:1.8rem;">🌱</div>
        <div style="font-size:0.78rem;font-weight:600;margin-top:0.4rem;color:{tc['text']};">Novo usuário</div>
        <div style="font-size:0.68rem;color:{tc['text_muted']};">Ao se cadastrar</div>
        {'<div style="font-size:0.68rem;color:#7a2340;margin-top:0.3rem;">✓ Conquistado</div>' if conquistou else ''}
    </div>
    """, unsafe_allow_html=True)

for col, b in zip(cols[1:], BADGES):
    conquistou = pontos >= b["min"]
    bg  = tc['surface']  if conquistou else tc['surface2']
    brd = '#7a2340'      if conquistou else tc['border']
    with col:
        icone = b["nome"].split()[0]
        nome  = " ".join(b["nome"].split()[1:])
        st.markdown(f"""
        <div style="text-align:center;padding:1rem;
                    background:{bg};
                    border:1px solid {brd};
                    border-radius:12px;opacity:{'1' if conquistou else '0.5'}">
            <div style="font-size:1.8rem;">{icone}</div>
            <div style="font-size:0.78rem;font-weight:600;margin-top:0.4rem;color:{tc['text']};">{nome}</div>
            <div style="font-size:0.68rem;color:{tc['text_muted']};">{b['desc']}</div>
            {'<div style="font-size:0.68rem;color:#7a2340;margin-top:0.3rem;">✓ Conquistado</div>'
              if conquistou else
             f'<div style="font-size:0.68rem;color:{tc["text_dim"]};margin-top:0.3rem;">{b["min"] - pontos} pts faltando</div>'}
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ── Como ganhar pontos ─────────────────────────────────────────────────────────
st.markdown("#### 💡 Como ganhar pontos")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    <div class="card">
        <div class="card-title">Por consulta</div>
        <div class="card-value">+1 ponto</div>
        <div class="card-sub">Cada pergunta feita no chat vale 1 ponto automático</div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="card">
        <div class="card-title">Troca por créditos</div>
        <div class="card-value">{PONTOS_PARA_TROCAR}pts = {CREDITOS_POR_TROCA}cred</div>
        <div class="card-sub">Acumule {PONTOS_PARA_TROCAR} pontos e troque por créditos grátis</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ── Trocar pontos ─────────────────────────────────────────────────────────────
st.markdown("#### 🔄 Trocar pontos por créditos")
pode_trocar = pontos >= PONTOS_PARA_TROCAR
col_tr, col_msg = st.columns([1, 2])
with col_tr:
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
with col_msg:
    if not pode_trocar:
        faltam = PONTOS_PARA_TROCAR - pontos
        st.info(f"Faltam **{faltam} pontos** para realizar a troca.")

st.divider()

# ── Ranking ────────────────────────────────────────────────────────────────────
st.markdown("#### 🏆 Ranking de pontos")
ranking = ranking_pontos(10)

if ranking:
    medalhas = ["🥇", "🥈", "🥉"] + ["🔸"] * 7
    dados = []
    for i, r in enumerate(ranking):
        destaque = r["nome"] == usuario["nome"]
        dados.append({
            "Pos.":  f"{medalhas[i]} {i+1}º",
            "Nome":  f"**{r['nome']}**" if destaque else r["nome"],
            "Pontos": r["pontos"],
        })
    st.dataframe(dados, use_container_width=True, hide_index=True)
else:
    st.info("Nenhum dado de ranking ainda.")

st.divider()
col_s, _ = st.columns([1, 3])
with col_s:
    if st.button("🚪 Sair"):
        fazer_logout()
        st.rerun()
