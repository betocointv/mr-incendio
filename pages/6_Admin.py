"""
Painel Admin — exclusivo para administradores do sistema.
"""

import streamlit as st
from auth import sessao_logada, get_usuario_sessao, fazer_logout
from creditos import adicionar_creditos, badge_atual
from datetime import date
from db import (listar_usuarios, stats_plataforma, buscar_usuario_id,
                registrar_auditoria, listar_audit_log, init_db,
                get_datas_normas, set_data_norma)
from ui import aplicar_tema, nav_inferior, header_usuario

st.set_page_config(page_title="Admin – Mr. Incêndio", page_icon="⚙️", layout="wide")
init_db()
aplicar_tema()

if not sessao_logada():
    st.warning("Acesso restrito.")
    st.page_link("app.py", label="← Ir para o login")
    st.stop()

usuario = get_usuario_sessao()
if usuario["tipo"] != "admin":
    st.error("Acesso restrito ao administrador do sistema.")
    st.stop()

header_usuario(usuario["nome"], usuario["creditos"], usuario["pontos"], badge_atual(usuario["pontos"]))
st.markdown("### ⚙️ Painel Administrativo")
nav_inferior("admin", usuario["tipo"])

st.divider()

# ── Estatísticas da plataforma ───────────────────────────────────────────────
stats = stats_plataforma()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("👥 Usuários ativos", stats["usuarios"])
with col2:
    st.metric("🔍 Total de consultas", stats["perguntas"])
with col3:
    st.metric("💰 Créditos vendidos", f"{stats['creditos_vendidos']:.0f}")

st.divider()

# ── Adicionar créditos manualmente ──────────────────────────────────────────
st.subheader("💳 Adicionar créditos para usuário")
todos = listar_usuarios()
todos_validos = [u for u in todos if u["tipo"] != "admin"]

if todos_validos:
    opcoes = {f"{u['nome']} ({u['email']}) — {u['creditos']:.0f} cred.": u["id"]
              for u in todos_validos}
    sel = st.selectbox("Usuário", list(opcoes.keys()))
    qtd = st.number_input("Quantidade de créditos", min_value=1, max_value=10000, value=100)
    obs = st.text_input("Observação", value="Adicionado pelo admin")

    if st.button("✅ Adicionar créditos", type="primary"):
        adicionar_creditos(opcoes[sel], qtd, obs)
        registrar_auditoria(usuario["id"], "adicionar_creditos",
                            f"Adicionou {qtd} créditos para uid={opcoes[sel]}. Obs: {obs}")
        st.success(f"✅ {qtd} créditos adicionados.")
        st.rerun()

st.divider()

# ── Lista de usuários ────────────────────────────────────────────────────────
st.subheader("👥 Todos os usuários")
if todos_validos:
    dados = [{
        "Nome": u["nome"],
        "Email": u["email"],
        "Tipo": u["tipo"],
        "Créditos": f"{u['creditos']:.0f}",
        "Pontos": u["pontos"],
        "Ativo": "✅" if u["ativo"] else "❌",
        "Desde": u["criado_em"][:10],
    } for u in todos_validos]
    st.dataframe(dados, use_container_width=True, hide_index=True)

st.divider()

# ── Log de auditoria ─────────────────────────────────────────────────────────
st.subheader("🔍 Log de auditoria")
logs = listar_audit_log(50)
if logs:
    dados_log = [{
        "Data/Hora": r["criado_em"][:19].replace("T", " "),
        "Usuário":   r["nome"]  or "—",
        "E-mail":    r["email"] or "—",
        "Ação":      r["acao"],
        "Detalhe":   r["detalhe"] or "—",
    } for r in logs]
    st.dataframe(dados_log, use_container_width=True, hide_index=True)
else:
    st.info("Nenhuma ação registrada ainda.")

st.divider()

# ── Atualização das normas ────────────────────────────────────────────────────
st.subheader("📅 Última verificação das normas")
st.caption("Atualize as datas sempre que verificar se há novas versões das NTs ou do COSCIP.")

datas = get_datas_normas()

def _parse_date(d):
    try:
        return date.fromisoformat(d) if d else date.today()
    except Exception:
        return date.today()

col_nt, col_cos = st.columns(2)
with col_nt:
    nova_nt = st.date_input(
        "📋 NTs CBMERJ",
        value=_parse_date(datas.get("normas_tecnicas")),
        format="DD/MM/YYYY",
        key="data_nt",
    )
with col_cos:
    nova_cos = st.date_input(
        "📋 COSCIP",
        value=_parse_date(datas.get("coscip")),
        format="DD/MM/YYYY",
        key="data_cos",
    )

if st.button("✅ Salvar datas de verificação", type="primary"):
    set_data_norma("normas_tecnicas", nova_nt.isoformat())
    set_data_norma("coscip", nova_cos.isoformat())
    registrar_auditoria(
        usuario["id"], "atualizar_normas",
        f"NTs: {nova_nt.strftime('%d/%m/%Y')} | COSCIP: {nova_cos.strftime('%d/%m/%Y')}"
    )
    st.success("✅ Datas salvas com sucesso!")
    st.rerun()

st.divider()
col1, _ = st.columns([1, 3])
with col1:
    if st.button("🚪 Sair"):
        fazer_logout()
        st.rerun()
