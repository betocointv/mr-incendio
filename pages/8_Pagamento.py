# -*- coding: utf-8 -*-
"""
Página de pagamento — PIX (QR code) ou Cartão (checkout hospedado Pagar.me).
"""
from __future__ import annotations

import re
import time

import streamlit as st

from auth import sessao_logada, get_usuario_sessao, fazer_logout
from creditos import adicionar_creditos, badge_atual
from db import listar_pacotes, registrar_auditoria, init_db
from pagamento import (criar_pix, extrair_pix, ordem_paga,
                       criar_checkout, checkout_pago)
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

# ── URL base do app (para success_url do checkout hospedado) ──────────────────
_app_url = st.secrets.get("APP_URL", "https://mr-incendio.streamlit.app")
_token   = st.session_state.get("_sess_token", "")

# ── Verifica retorno do checkout hospedado (cartão) ───────────────────────────
_chk_id = st.query_params.get("checkout_id", "")
if _chk_id:
    with st.spinner("Verificando pagamento…"):
        if checkout_pago(_chk_id):
            # Recupera plano salvo no session_state ou query param
            _plano_id = (st.session_state.get("plano_pagamento_id")
                         or int(st.query_params.get("plano_id", 0)))
            _pacotes  = listar_pacotes()
            _plano    = next((p for p in _pacotes if p["id"] == _plano_id), None)
            if _plano:
                adicionar_creditos(usuario["id"], _plano["creditos"],
                                   f"Compra plano {_plano['nome']} — checkout {_chk_id}")
                registrar_auditoria(usuario["id"], "compra_creditos",
                                    f"Plano {_plano['nome']} | {_plano['creditos']} cred "
                                    f"| R${_plano['preco_brl']:.2f} | chk={_chk_id}")
                for k in ("plano_pagamento_id", "pix_order_id",
                          "pix_code", "pix_url", "metodo_pagamento"):
                    st.session_state.pop(k, None)
                st.success(f"✅ Pagamento confirmado! **{_plano['creditos']} créditos** adicionados.")
                st.balloons()
                time.sleep(2)
                st.switch_page("pages/1_Chat.py")
                st.stop()
        else:
            st.warning("Pagamento ainda não confirmado. Tente novamente em instantes.")
            try:
                del st.query_params["checkout_id"]
            except Exception:
                pass

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
                           f"Compra plano {plano['nome']} — Pagar.me {order_id}")
        registrar_auditoria(usuario["id"], "compra_creditos",
                            f"Plano {plano['nome']} | {plano['creditos']} cred "
                            f"| R${plano['preco_brl']:.2f} | order={order_id}")
        for k in ("pix_order_id", "pix_code", "pix_url",
                  "plano_pagamento_id", "metodo_pagamento"):
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
            for k in ("pix_order_id", "pix_code", "pix_url",
                      "plano_pagamento_id", "metodo_pagamento"):
                st.session_state.pop(k, None)
            st.switch_page("pages/4_Planos.py")
    st.stop()

# ── Formulário: escolha de método + CPF ──────────────────────────────────────
st.markdown("#### Escolha a forma de pagamento")

metodo = st.radio(
    "Método",
    ["💠 PIX", "💳 Cartão de crédito"],
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown(" ")

with st.form("form_pagamento"):
    cpf = st.text_input("CPF", placeholder="000.000.000-00",
                        help="Necessário para emissão da cobrança")
    label_btn = "Gerar PIX" if "PIX" in metodo else "Ir para pagamento com cartão →"
    submitted = st.form_submit_button(label_btn, use_container_width=True, type="primary")

if submitted:
    cpf_digits = re.sub(r"\D", "", cpf)
    if len(cpf_digits) != 11:
        st.error("CPF inválido. Digite os 11 dígitos.")
        st.stop()

    valor_centavos = int(round(plano["preco_brl"] * 100))
    descricao      = f"Mr. Incêndio — Plano {plano['nome']} ({plano['creditos']} créditos)"

    if "PIX" in metodo:
        with st.spinner("Gerando cobrança PIX…"):
            try:
                ordem = criar_pix(
                    nome=usuario["nome"],
                    email=usuario["email"],
                    cpf=cpf_digits,
                    valor_centavos=valor_centavos,
                    descricao=descricao,
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
    else:
        with st.spinner("Criando sessão de pagamento…"):
            try:
                _success = (f"{_app_url}/Pagamento"
                            f"?t={_token}&plano_id={plano['id']}")
                checkout = criar_checkout(
                    nome=usuario["nome"],
                    email=usuario["email"],
                    cpf=cpf_digits,
                    valor_centavos=valor_centavos,
                    descricao=descricao,
                    success_url=_success,
                    metadata={"usuario_id": str(usuario["id"]),
                               "plano_id": str(plano["id"])},
                )
                payment_url = checkout.get("url") or checkout.get("payment_url", "")
                if not payment_url:
                    st.error("Não foi possível obter o link de pagamento.")
                    st.stop()
                # Redireciona para o checkout do Pagar.me
                st.markdown(
                    f'<meta http-equiv="refresh" content="0; url={payment_url}">',
                    unsafe_allow_html=True,
                )
                st.info(f"Redirecionando para o pagamento… "
                        f"[Clique aqui se não redirecionar]({payment_url})")
            except Exception as e:
                st.error(f"Erro ao criar checkout: {e}")
