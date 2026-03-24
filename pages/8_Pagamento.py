# -*- coding: utf-8 -*-
"""
Página de pagamento — PIX (QR code) ou Checkout Pagar.me (cartão + PIX).
"""
from __future__ import annotations

import re
import time

import streamlit as st

from auth import sessao_logada, get_usuario_sessao, fazer_logout
from creditos import adicionar_creditos, badge_atual
from db import (listar_pacotes, registrar_auditoria, init_db,
                criar_pagamento_pendente, buscar_pagamentos_pendentes,
                marcar_pagamento_processado)
from pagamento import criar_pix, extrair_pix, ordem_paga
from ui import aplicar_tema, nav_inferior, header_usuario

st.set_page_config(page_title="Pagamento – Mr. Incêndio",
                   page_icon="💳", layout="wide")
init_db()
aplicar_tema()

# Links de pagamento Pagar.me por plano_id
LINKS_PAGARME = {
    1: "https://payment-link-v3.pagar.me/pl_3RQVdn0lPJBwqLBtJs4LYMAEK9eDLbpk",
    2: "https://payment-link-v3.pagar.me/pl_ZNMz72opQv80v2tNpf8P0wJxAb6BgaWD",
    3: "https://payment-link-v3.pagar.me/pl_lrbgqoZGM8dPY8VIjEcyB3wERDVYz9m2",
    4: "https://payment-link-v3.pagar.me/pl_dZkxbr02o6NV5GPURh38B1a9pqMmwLGl",
}

# ── Retorno do Pagar.me após pagamento ────────────────────────────────────────
plano_id_return = st.query_params.get("plano_id", "")
pago_flag       = st.query_params.get("pago", "")

if pago_flag == "1" and plano_id_return:
    if sessao_logada():
        usuario = get_usuario_sessao()
        if usuario:
            pacotes  = listar_pacotes()
            plano    = next((p for p in pacotes if p["id"] == int(plano_id_return)), None)
            pendentes = buscar_pagamentos_pendentes(usuario["id"])
            pendente  = next((p for p in pendentes if p["plano_id"] == int(plano_id_return)), None)

            if plano and pendente:
                adicionar_creditos(usuario["id"], plano["creditos"],
                                   f"Compra plano {plano['nome']} — Pagar.me link")
                registrar_auditoria(usuario["id"], "compra_creditos",
                                    f"Plano {plano['nome']} | {plano['creditos']} cred "
                                    f"| R${plano['preco_brl']:.2f} | link")
                marcar_pagamento_processado(pendente["id"])
                st.success(f"✅ Pagamento confirmado! **{plano['creditos']} créditos** adicionados.")
                st.balloons()
                time.sleep(2)
                st.switch_page("pages/1_Chat.py")
                st.stop()
            elif plano:
                # Pagamento chegou mas não tem pendente (ex: link aberto diretamente)
                st.warning("Pagamento recebido, mas não encontramos sua solicitação. "
                           "Contate o suporte se os créditos não foram adicionados.")
    else:
        # Sessão perdida — pede login
        st.session_state["plano_pago_pendente"] = int(plano_id_return)
        aplicar_tema()
        st.info("🎉 Pagamento confirmado! Faça login para receber seus créditos.")
        if st.button("🔑 Fazer login", type="primary"):
            st.switch_page("pages/0_Acesso.py")
        st.stop()

# ── Verifica login ────────────────────────────────────────────────────────────
if not sessao_logada():
    st.warning("Faça login para continuar.")
    st.page_link("pages/0_Acesso.py", label="← Ir para o login")
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
plano   = next((p for p in pacotes if p["id"] == plano_id), None)
if not plano:
    st.error("Plano não encontrado.")
    st.stop()

st.markdown(f"### 💳 Pagamento — {plano['nome']}")
st.markdown(f"**{plano['creditos']} créditos** por **R$ {plano['preco_brl']:.2f}**")
st.divider()

# ── Fluxo PIX em andamento ────────────────────────────────────────────────────
order_id = st.session_state.get("pix_order_id")
pix_code = st.session_state.get("pix_code", "")
pix_url  = st.session_state.get("pix_url", "")

if order_id:
    if ordem_paga(order_id):
        adicionar_creditos(usuario["id"], plano["creditos"],
                           f"Compra plano {plano['nome']} — PIX {order_id}")
        registrar_auditoria(usuario["id"], "compra_creditos",
                            f"Plano {plano['nome']} | {plano['creditos']} cred "
                            f"| R${plano['preco_brl']:.2f} | order={order_id}")
        for k in ("pix_order_id", "pix_code", "pix_url", "plano_pagamento_id"):
            st.session_state.pop(k, None)
        st.success(f"✅ Pagamento confirmado! **{plano['creditos']} créditos** adicionados.")
        st.balloons()
        time.sleep(2)
        st.switch_page("pages/1_Chat.py")
        st.stop()

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

# ── Escolha de método ─────────────────────────────────────────────────────────
st.markdown("#### Escolha a forma de pagamento")

col_card, col_pix = st.columns(2)

with col_card:
    st.markdown("""
    <div style="border:2px solid #7a2340;border-radius:12px;padding:1.2rem;text-align:center;">
        <div style="font-size:1.5rem;">💳</div>
        <div style="font-weight:700;margin-top:.4rem;">Cartão de crédito</div>
        <div style="font-size:.82rem;color:#9090b8;margin-top:.3rem;">Checkout seguro Pagar.me</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(" ")
    if st.button("Pagar com Cartão →", use_container_width=True, type="primary",
                 key="btn_cartao"):
        criar_pagamento_pendente(usuario["id"], plano["id"])
        link = LINKS_PAGARME.get(plano["id"], "")
        st.markdown(
            f'<meta http-equiv="refresh" content="0; url={link}">',
            unsafe_allow_html=True,
        )
        st.info(f"Redirecionando… [Clique aqui se não redirecionar]({link})")

with col_pix:
    st.markdown("""
    <div style="border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:1.2rem;text-align:center;">
        <div style="font-size:1.5rem;">💠</div>
        <div style="font-weight:700;margin-top:.4rem;">PIX</div>
        <div style="font-size:.82rem;color:#9090b8;margin-top:.3rem;">QR Code gerado na hora</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(" ")
    if st.button("Gerar QR Code PIX", use_container_width=True, key="btn_pix"):
        st.session_state["mostrar_form_pix"] = True
        st.rerun()

# ── Formulário PIX ────────────────────────────────────────────────────────────
if st.session_state.get("mostrar_form_pix"):
    st.divider()
    valor_centavos = int(round(plano["preco_brl"] * 100))
    descricao      = f"Mr. Incêndio — Plano {plano['nome']} ({plano['creditos']} créditos)"

    with st.form("form_pix"):
        cpf = st.text_input("CPF", placeholder="000.000.000-00")
        submitted = st.form_submit_button("Gerar PIX", use_container_width=True,
                                          type="primary")
    if submitted:
        cpf_digits = re.sub(r"\D", "", cpf)
        if len(cpf_digits) != 11:
            st.error("CPF inválido.")
            st.stop()
        with st.spinner("Gerando cobrança PIX…"):
            try:
                ordem = criar_pix(
                    nome=usuario["nome"], email=usuario["email"],
                    cpf=cpf_digits, valor_centavos=valor_centavos,
                    descricao=descricao,
                    metadata={"usuario_id": str(usuario["id"]),
                               "plano_id": str(plano["id"])},
                )
                qr_code, qr_url = extrair_pix(ordem)
                st.session_state["pix_order_id"]    = ordem["id"]
                st.session_state["pix_code"]        = qr_code
                st.session_state["pix_url"]         = qr_url
                st.session_state["mostrar_form_pix"] = False
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao gerar PIX: {e}")
