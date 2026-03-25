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
                marcar_pagamento_processado, order_ja_processada)
from pagamento import criar_pix, extrair_pix, ordem_paga, buscar_ordem_paga_por_valor
from ui import aplicar_tema, nav_inferior, header_usuario

st.set_page_config(page_title="Pagamento – Mr. Incêndio",
                   page_icon="💳", layout="wide")
init_db()
aplicar_tema()

LINKS_PAGARME = {
    1: "https://payment-link-v3.pagar.me/pl_3RQVdn0lPJBwqLBtJs4LYMAEK9eDLbpk",
    2: "https://payment-link-v3.pagar.me/pl_ZNMz72opQv80v2tNpf8P0wJxAb6BgaWD",
    3: "https://payment-link-v3.pagar.me/pl_lrbgqoZGM8dPY8VIjEcyB3wERDVYz9m2",
    4: "https://payment-link-v3.pagar.me/pl_dZkxbr02o6NV5GPURh38B1a9pqMmwLGl",
}

# ── Verifica login ─────────────────────────────────────────────────────────────
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

# ── Verifica se há plano selecionado ──────────────────────────────────────────
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

valor_centavos = int(round(plano["preco_brl"] * 100))

st.markdown(f"### 💳 Pagamento — {plano['nome']}")
st.markdown(f"**{plano['creditos']} créditos** por **R$ {plano['preco_brl']:.2f}**")
st.divider()

# ── Fluxo PIX em andamento ─────────────────────────────────────────────────────
order_id = st.session_state.get("pix_order_id")
if order_id:
    if ordem_paga(order_id):
        adicionar_creditos(usuario["id"], plano["creditos"],
                           f"Compra plano {plano['nome']} — PIX {order_id}")
        registrar_auditoria(usuario["id"], "compra_creditos",
                            f"Plano {plano['nome']} | {plano['creditos']} cred "
                            f"| R${plano['preco_brl']:.2f} | pix")
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
        pix_url = st.session_state.get("pix_url", "")
        if pix_url:
            st.image(pix_url, width=240, caption="Escaneie com o app do banco")
        else:
            st.warning("QR Code indisponível — use o código abaixo.")
    with col_info:
        st.markdown("**PIX Copia e Cola:**")
        st.code(st.session_state.get("pix_code", ""), language=None)
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

# ── Fluxo "Já paguei" via link Pagar.me ───────────────────────────────────────
if st.session_state.get("aguardando_link_pagarme"):
    link = LINKS_PAGARME.get(plano["id"], "")
    st.markdown(f"""
    <div style="border:2px solid #7a2340;border-radius:14px;padding:1.5rem;text-align:center;margin-bottom:1.2rem;">
        <div style="font-size:1.1rem;font-weight:700;margin-bottom:.6rem;">
            Finalize o pagamento no Pagar.me
        </div>
        <div style="font-size:.88rem;color:#9090b8;margin-bottom:1rem;">
            Clique no botão abaixo para abrir o Pagar.me. Após pagar, volte aqui e clique em <b>Já paguei</b>.
        </div>
        <a href="{link}" target="_blank"
           style="background:#7a2340;color:white;padding:.7rem 1.8rem;border-radius:8px;
                  text-decoration:none;font-weight:700;font-size:1rem;">
            🔗 Abrir Pagar.me para pagar
        </a>
    </div>
    """, unsafe_allow_html=True)

    col_ok, col_c = st.columns([1, 1])
    with col_ok:
        if st.button("✅ Já paguei", use_container_width=True, type="primary"):
            with st.spinner("Verificando pagamento no Pagar.me…"):
                order_id_found = buscar_ordem_paga_por_valor(valor_centavos, minutos=60)

            if not order_id_found:
                st.error("Nenhum pagamento confirmado ainda. Aguarde alguns instantes e tente novamente.")
            elif order_ja_processada(order_id_found):
                st.warning("Este pagamento já foi processado anteriormente.")
            else:
                pendentes = buscar_pagamentos_pendentes(usuario["id"])
                pendente  = next((p for p in pendentes if p["plano_id"] == plano["id"]), None)
                if pendente:
                    adicionar_creditos(usuario["id"], plano["creditos"],
                                       f"Compra plano {plano['nome']} — Pagar.me {order_id_found}")
                    registrar_auditoria(usuario["id"], "compra_creditos",
                                        f"Plano {plano['nome']} | {plano['creditos']} cred "
                                        f"| R${plano['preco_brl']:.2f} | link={order_id_found}")
                    marcar_pagamento_processado(pendente["id"], order_id_found)
                    st.session_state.pop("aguardando_link_pagarme", None)
                    st.session_state.pop("plano_pagamento_id", None)
                    st.success(f"✅ **{plano['creditos']} créditos** adicionados com sucesso!")
                    st.balloons()
                    time.sleep(2)
                    st.switch_page("pages/1_Chat.py")
                else:
                    st.error("Registro de compra não encontrado. Contate o suporte.")
    with col_c:
        if st.button("❌ Cancelar", use_container_width=True):
            st.session_state.pop("aguardando_link_pagarme", None)
            st.session_state.pop("plano_pagamento_id", None)
            st.switch_page("pages/4_Planos.py")
    st.stop()

# ── Escolha de método ──────────────────────────────────────────────────────────
st.markdown("#### Escolha a forma de pagamento")

col_card, col_pix = st.columns(2)

with col_card:
    st.markdown("""
    <div style="border:2px solid #7a2340;border-radius:12px;padding:1.4rem;text-align:center;">
        <div style="font-size:1.8rem;">💳</div>
        <div style="font-weight:700;margin-top:.5rem;">Cartão ou PIX</div>
        <div style="font-size:.82rem;color:#9090b8;margin-top:.3rem;">
            Checkout seguro hospedado pelo Pagar.me
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(" ")
    if st.button("Pagar no Pagar.me →", use_container_width=True,
                 type="primary", key="btn_link"):
        criar_pagamento_pendente(usuario["id"], plano["id"])
        st.session_state["aguardando_link_pagarme"] = True
        st.rerun()

with col_pix:
    st.markdown("""
    <div style="border:1px solid rgba(255,255,255,0.12);border-radius:12px;padding:1.4rem;text-align:center;">
        <div style="font-size:1.8rem;">💠</div>
        <div style="font-weight:700;margin-top:.5rem;">PIX direto</div>
        <div style="font-size:.82rem;color:#9090b8;margin-top:.3rem;">
            QR Code gerado na hora, sem sair do app
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(" ")
    if st.button("Gerar QR Code PIX", use_container_width=True, key="btn_pix"):
        st.session_state["mostrar_form_pix"] = True
        st.rerun()

# ── Formulário PIX ─────────────────────────────────────────────────────────────
if st.session_state.get("mostrar_form_pix"):
    st.divider()
    descricao = f"Mr. Incêndio — Plano {plano['nome']} ({plano['creditos']} créditos)"
    with st.form("form_pix"):
        cpf       = st.text_input("CPF", placeholder="000.000.000-00")
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
                st.session_state["pix_order_id"]     = ordem["id"]
                st.session_state["pix_code"]         = qr_code
                st.session_state["pix_url"]          = qr_url
                st.session_state["mostrar_form_pix"] = False
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao gerar PIX: {e}")
