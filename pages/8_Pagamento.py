# -*- coding: utf-8 -*-
"""
Página de pagamento via PIX — Pagar.me V5.
"""
from __future__ import annotations

import re
import time

import streamlit as st

from auth import sessao_logada, get_usuario_sessao, fazer_logout
from creditos import adicionar_creditos, badge_atual
from db import listar_pacotes, registrar_auditoria, init_db
from pagamento import criar_pix, extrair_pix, ordem_paga
from ui import aplicar_tema, nav_inferior, header_usuario

st.set_page_config(page_title="Pagamento – Mr. Incêndio",
                   page_icon="💳", layout="wide")
init_db()
aplicar_tema()

if not sessao_logada():
    st.warning("Faça login para continuar.")
    st.page_link("app.py", label="← Ir para o login")
    st.stop()

usuario = get_usuario_sessao()
if not usuario:
    fazer_logout()
    st.rerun()

badge = badge_atual(usuario["pontos"])
header_usuario(usuario["nome"], usuario["creditos"], usuario["pontos"], badge)
nav_inferior("planos", usuario["tipo"])

# ── Verifica se há plano selecionado ─────────────────────────────────────────
plano_id = st.session_state.get("plano_pagamento_id")
if not plano_id:
    st.info("Nenhum plano selecionado.")
    if st.button("← Ver planos"):
        st.switch_page("pages/4_Planos.py")
    st.stop()

pacotes = listar_pacotes()
plano = next((p for p in pacotes if p["id"] == plano_id), None)
if not plano:
    st.error("Plano não encontrado.")
    st.stop()

st.markdown(f"### 💳 Pagamento — {plano['nome']}")
st.markdown(f"**{plano['creditos']} créditos** por **R$ {plano['preco_brl']:.2f}**")
st.divider()

# ── Estado do pagamento ───────────────────────────────────────────────────────
order_id  = st.session_state.get("pix_order_id")
pix_code  = st.session_state.get("pix_code", "")
pix_url   = st.session_state.get("pix_url", "")

# ── Se já tem ordem, verifica se foi paga ────────────────────────────────────
if order_id:
    if ordem_paga(order_id):
        adicionar_creditos(usuario["id"], plano["creditos"],
                           f"Compra plano {plano['nome']} — Pagar.me {order_id}")
        registrar_auditoria(usuario["id"], "compra_creditos",
                            f"Plano {plano['nome']} | {plano['creditos']} créditos | R${plano['preco_brl']:.2f} | order={order_id}")
        # Limpa estado
        for k in ("pix_order_id", "pix_code", "pix_url", "plano_pagamento_id"):
            st.session_state.pop(k, None)
        st.success(f"✅ Pagamento confirmado! **{plano['creditos']} créditos** adicionados à sua conta.")
        st.balloons()
        time.sleep(2)
        st.switch_page("pages/1_Chat.py")
        st.stop()

    # Exibe QR code e aguarda
    st.info("⏳ Aguardando pagamento via PIX…")

    col_qr, col_info = st.columns([1, 1])
    with col_qr:
        if pix_url:
            st.image(pix_url, width=240, caption="Escaneie com o app do banco")
        else:
            st.warning("QR Code indisponível — use o código abaixo.")

    with col_info:
        st.markdown("**PIX Copia e Cola:**")
        st.code(pix_code, language=None)
        st.caption("Válido por 1 hora")

    st.divider()
    col_v, col_c = st.columns([1, 1])
    with col_v:
        if st.button("🔄 Verificar pagamento", use_container_width=True, type="primary"):
            st.rerun()
    with col_c:
        if st.button("❌ Cancelar", use_container_width=True):
            for k in ("pix_order_id", "pix_code", "pix_url", "plano_pagamento_id"):
                st.session_state.pop(k, None)
            st.switch_page("pages/4_Planos.py")
    st.stop()

# ── Formulário para gerar o PIX ──────────────────────────────────────────────
st.markdown("#### Preencha seus dados para gerar o PIX")

with st.form("form_pix"):
    cpf = st.text_input("CPF", placeholder="000.000.000-00",
                        help="Necessário para emissão da cobrança PIX")
    submitted = st.form_submit_button("Gerar PIX", use_container_width=True,
                                      type="primary")

if submitted:
    cpf_digits = re.sub(r"\D", "", cpf)
    if len(cpf_digits) != 11:
        st.error("CPF inválido. Digite os 11 dígitos.")
        st.stop()

    with st.spinner("Gerando cobrança PIX…"):
        try:
            valor_centavos = int(round(plano["preco_brl"] * 100))
            ordem = criar_pix(
                nome=usuario["nome"],
                email=usuario["email"],
                cpf=cpf_digits,
                valor_centavos=valor_centavos,
                descricao=f"Mr. Incêndio — Plano {plano['nome']} ({plano['creditos']} créditos)",
                metadata={"usuario_id": str(usuario["id"]),
                          "plano_id": str(plano["id"])},
            )
            qr_code, qr_url = extrair_pix(ordem)
            st.session_state["pix_order_id"] = ordem["id"]
            st.session_state["pix_code"]     = qr_code
            st.session_state["pix_url"]      = qr_url
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao gerar PIX: {e}")
