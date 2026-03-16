"""
Gestão de equipe — exclusivo para empresa_admin.
"""

import html
import streamlit as st
from auth import sessao_logada, get_usuario_sessao, fazer_logout
from db import (listar_usuarios, desativar_usuario, atualizar_tipo_usuario,
                vincular_usuario_empresa, buscar_empresa, buscar_usuario_email,
                consumo_por_usuario, registrar_auditoria, init_db)
from ui import aplicar_tema, nav_inferior, header_usuario
from creditos import badge_atual

st.set_page_config(page_title="Empresa – Mr. Incêndio", page_icon="🏢", layout="wide")
init_db()
aplicar_tema()

if not sessao_logada():
    st.warning("Faça login para acessar.")
    st.page_link("app.py", label="← Ir para o login")
    st.stop()

usuario = get_usuario_sessao()

if usuario["tipo"] not in ("empresa_admin", "admin"):
    st.error("Acesso restrito para administradores de empresa.")
    st.stop()

empresa = buscar_empresa(usuario["empresa_id"]) if usuario["empresa_id"] is not None else None

header_usuario(usuario["nome"], usuario["creditos"], usuario["pontos"], badge_atual(usuario["pontos"]))
st.markdown(f"### 🏢 {empresa['nome'] if empresa else 'Gestão da Empresa'}")
if empresa:
    st.caption(f"Pool de créditos da empresa: **{usuario['creditos']:.0f}**")
nav_inferior("empresa", usuario["tipo"])


st.divider()

# ── Adicionar funcionário ────────────────────────────────────────────────────
st.subheader("➕ Adicionar funcionário")
st.caption("Busque pelo e-mail de quem já tem conta no sistema.")

email_busca = st.text_input("E-mail do usuário", placeholder="nome@email.com",
                             key="busca_email_func")
if st.button("🔍 Buscar", use_container_width=False):
    if not email_busca.strip():
        st.warning("Digite um e-mail para buscar.")
    else:
        encontrado = buscar_usuario_email(email_busca.strip().lower())
        if not encontrado:
            st.error("Nenhum usuário encontrado com esse e-mail.")
        elif encontrado["empresa_id"] is not None:
            st.warning("Este usuário já pertence a uma empresa.")
        elif encontrado["tipo"] in ("admin",):
            st.error("Este usuário não pode ser adicionado como funcionário.")
        else:
            st.session_state.func_encontrado = dict(encontrado)

if st.session_state.get("func_encontrado"):
    f = st.session_state.func_encontrado
    st.success(f"✅ Usuário encontrado: **{f['nome']}** ({f['email']})")
    if st.button("➕ Adicionar à empresa", type="primary", use_container_width=False):
        vincular_usuario_empresa(f["id"], usuario["empresa_id"])
        registrar_auditoria(usuario["id"], "adicionar_funcionario",
                            f"Adicionou {f['email']} à empresa {usuario['empresa_id']}")
        st.session_state.pop("func_encontrado", None)
        st.success(f"**{f['nome']}** adicionado à equipe!")
        st.rerun()
    if st.button("Cancelar", use_container_width=False):
        st.session_state.pop("func_encontrado", None)
        st.rerun()

st.divider()

# ── Consumo por funcionário ──────────────────────────────────────────────────
st.subheader("📊 Consumo da equipe")
consumo = consumo_por_usuario(usuario["empresa_id"])
if not consumo:
    st.info("Nenhum funcionário ainda.")
else:
    tc2 = __import__("ui").tema_cores()
    cols_c = st.columns(min(len(consumo), 3))
    for i, c in enumerate(consumo):
        perguntas = c["perguntas"] or 0
        creditos_usados = c["creditos_usados"] or 0
        with cols_c[i % 3]:
            nome_safe  = html.escape(c["nome"])
            email_safe = html.escape(c["email"])
            st.markdown(
                f'<div style="border:1px solid {tc2["border"]};border-radius:12px;'
                f'padding:1rem;background:{tc2["surface"]};margin-bottom:0.8rem;">'
                f'<div style="font-weight:700;color:{tc2["text"]};margin-bottom:0.2rem;">{nome_safe}</div>'
                f'<div style="font-size:0.78rem;color:{tc2["text_dim"]};margin-bottom:0.6rem;">{email_safe}</div>'
                f'<div style="display:flex;gap:1rem;">'
                f'<div><div style="font-size:1.3rem;font-weight:800;color:#7a2340;">{perguntas}</div>'
                f'<div style="font-size:0.72rem;color:{tc2["text_muted"]};">consultas</div></div>'
                f'<div><div style="font-size:1.3rem;font-weight:800;color:{tc2["text"]};">{creditos_usados:.0f}</div>'
                f'<div style="font-size:0.72rem;color:{tc2["text_muted"]};">créditos</div></div>'
                f'</div></div>',
                unsafe_allow_html=True
            )

st.divider()

# ── Lista de funcionários ────────────────────────────────────────────────────
st.subheader("👥 Funcionários")

todos = listar_usuarios(usuario["empresa_id"])
funcionarios = [f for f in todos if f["tipo"] in ("funcionario", "empresa_admin")
                and f["id"] != usuario["id"]]

busca = st.text_input("🔍 Buscar por nome ou e-mail", placeholder="Digite para filtrar...",
                      key="busca_lista_func")
if busca.strip():
    termo = busca.strip().lower()
    funcionarios = [f for f in funcionarios
                    if termo in f["nome"].lower() or termo in f["email"].lower()]

POR_PAGINA = 10
total_pags = max(1, -(-len(funcionarios) // POR_PAGINA))  # ceil division

if "emp_pagina" not in st.session_state:
    st.session_state.emp_pagina = 1
# reseta para pág 1 ao buscar
if busca.strip():
    st.session_state.emp_pagina = 1
pag = st.session_state.emp_pagina
inicio = (pag - 1) * POR_PAGINA
pagina = funcionarios[inicio: inicio + POR_PAGINA]

# mapa de consumo para exibir perguntas
consumo_map = {c["email"]: c for c in consumo_por_usuario(usuario["empresa_id"])}
tc = __import__("ui").tema_cores()

if not funcionarios:
    st.info("Nenhum funcionário ainda.")
else:
    # cabeçalho
    h1, h2, h3, h4, h5 = st.columns([3, 3, 1.5, 1.5, 0.5])
    for col, label in zip([h1, h2, h3, h4, h5],
                          ["Nome", "E-mail", "Consultas", "Perfil", ""]):
        col.markdown(f"<small style='color:#888;font-weight:600;'>{label}</small>",
                     unsafe_allow_html=True)
    st.divider()

    for f in pagina:
        c1, c2, c3, c4, c5 = st.columns([3, 3, 1.5, 1.5, 0.5])
        cons = consumo_map.get(f["email"], {})
        perfil_label = "Admin" if f["tipo"] == "empresa_admin" else "Funcionário"
        perfil_cor = "#7a2340" if f["tipo"] == "empresa_admin" else tc["text_muted"]

        c1.markdown(f"**{f['nome']}**")
        c2.markdown(f"<span style='font-size:0.85rem;color:{tc['text_muted']};'>{html.escape(f['email'])}</span>",
                    unsafe_allow_html=True)
        c3.markdown(f"{cons.get('perguntas', 0) or 0}")
        c4.markdown(f"<span style='font-size:0.8rem;color:{perfil_cor};font-weight:600;'>"
                    f"{perfil_label}</span>", unsafe_allow_html=True)

        with c5:
            with st.popover("⋮"):
                st.markdown(f"**{f['nome']}**")
                st.divider()

                # Permissões
                novo_tipo = "funcionario" if f["tipo"] == "empresa_admin" else "empresa_admin"
                novo_label = ("↓ Rebaixar para Funcionário" if f["tipo"] == "empresa_admin"
                              else "↑ Promover a Admin")
                if st.button(novo_label, key=f"perm_{f['id']}", use_container_width=True):
                    atualizar_tipo_usuario(f["id"], novo_tipo)
                    registrar_auditoria(usuario["id"], "alterar_perfil",
                                        f"Alterou {f['email']} para {novo_tipo}")
                    st.rerun()

                # Excluir
                if st.button("🗑️ Excluir", key=f"del_{f['id']}", use_container_width=True,
                             type="primary"):
                    st.session_state[f"confirmar_del_{f['id']}"] = True
                    st.rerun()

            # confirmação fora do popover
            if st.session_state.get(f"confirmar_del_{f['id']}"):
                st.warning(f"Remover **{f['nome']}**?")
                col_s, col_n = st.columns(2)
                with col_s:
                    if st.button("✅ Sim", key=f"sim_{f['id']}", use_container_width=True):
                        desativar_usuario(f["id"])
                        registrar_auditoria(usuario["id"], "remover_funcionario",
                                            f"Removeu {f['email']} da empresa")
                        st.session_state.pop(f"confirmar_del_{f['id']}", None)
                        st.rerun()
                with col_n:
                    if st.button("❌ Não", key=f"nao_{f['id']}", use_container_width=True):
                        st.session_state.pop(f"confirmar_del_{f['id']}", None)
                        st.rerun()

    # Paginação
    if total_pags > 1:
        st.markdown("")
        p1, p2, p3 = st.columns([1, 2, 1])
        with p1:
            if st.button("← Anterior", disabled=pag <= 1, use_container_width=True):
                st.session_state.emp_pagina -= 1
                st.rerun()
        with p2:
            st.markdown(f"<div style='text-align:center;padding-top:0.4rem;'>"
                        f"Página {pag} de {total_pags}</div>", unsafe_allow_html=True)
        with p3:
            if st.button("Próxima →", disabled=pag >= total_pags, use_container_width=True):
                st.session_state.emp_pagina += 1
                st.rerun()

st.divider()
col1, _ = st.columns([1, 3])
with col1:
    if st.button("🚪 Sair"):
        fazer_logout()
        st.rerun()
