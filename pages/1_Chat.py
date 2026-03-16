# -*- coding: utf-8 -*-
"""
Chat principal — consulta às NTs do CBMERJ.
"""

from __future__ import annotations

import html as _html
import os
import pickle
import re
import uuid
from datetime import datetime
from pathlib import Path

import anthropic
import streamlit as st

from auth import sessao_logada, get_usuario_sessao, fazer_logout
from creditos import tem_credito, deduzir_credito, badge_atual
from db import (listar_conversas_db, salvar_conversa_db,
                excluir_conversa_db, init_db)
from ui import aplicar_tema, nav_inferior, header_usuario

st.set_page_config(page_title="Chat – Mr. Incêndio", page_icon="🔥", layout="wide")
init_db()
aplicar_tema()

if not sessao_logada():
    st.warning("Faça login para acessar o chat.")
    st.page_link("app.py", label="← Ir para o login")
    st.stop()

usuario = get_usuario_sessao()
if not usuario:
    fazer_logout()
    st.rerun()

uid     = usuario["id"]
api_key = st.secrets.get("ANTHROPIC_API_KEY", os.environ.get("ANTHROPIC_API_KEY", ""))

ARQUIVO_CHUNKS = Path("dados/chunks.pkl")
ARQUIVO_BM25   = Path("dados/bm25.pkl")
MAX_CONVERSAS  = 5
NUM_CHUNKS     = 25
MODELO         = "claude-haiku-4-5-20251001"

# ── CSS do chat estilizado ────────────────────────────────────────────────────
st.markdown("""
<style>
:root {
  --wine:      #7a2340;
  --wine-dk:   #561629;
  --wine-lt:   #c4607a;
  --wine-glow: rgba(122,35,64,.22);
  --bg0: #08080e; --bg1: #0f0f1e; --bg2: #141428; --bg3: #1a1a30;
  --border: rgba(255,255,255,0.08);
  --text: #f0f0f8; --muted: #9090b8; --dim: #60607a;
}

/* ── Layout ── */
.main .block-container,
[data-testid="stAppViewBlockContainer"] {
  padding-top: 1rem !important;
  padding-bottom: 6rem !important;
  max-width: 860px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--bg1) !important;
  border-right: 1px solid var(--border) !important;
}

/* ── Badge chip ── */
.badge-chip {
  display: inline-block;
  background: linear-gradient(135deg, var(--wine), var(--wine-dk));
  color: white !important;
  font-size: 0.72rem; font-weight: 700;
  padding: 2px 10px; border-radius: 20px;
  letter-spacing: .03em;
}

/* ── Chat message containers ── */
[data-testid="stChatMessage"] {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0.2rem 0 !important;
  gap: 0.65rem !important;
}

/* Esconde avatares padrão */
[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"],
[data-testid="chatAvatarIcon-user"],
[data-testid="chatAvatarIcon-assistant"],
.stChatMessageAvatar { display: none !important; }

/* ── USER bubble — direita, vinho ── */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
  flex-direction: row-reverse !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
  [data-testid="stChatMessageContent"] {
  background: linear-gradient(135deg, var(--wine), var(--wine-dk)) !important;
  border-radius: 18px 4px 18px 18px !important;
  padding: 0.7rem 1rem !important;
  max-width: 70% !important;
  margin-left: auto !important;
  box-shadow: 0 3px 16px var(--wine-glow) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
  [data-testid="stChatMessageContent"] p,
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
  [data-testid="stChatMessageContent"] * {
  color: #fff !important;
}

/* ── ASSISTANT bubble — esquerda, card escuro ── */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
  [data-testid="stChatMessageContent"] {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px 18px 18px 18px !important;
  padding: 0.85rem 1.1rem !important;
  max-width: 85% !important;
  box-shadow: 0 2px 16px rgba(0,0,0,.25) !important;
}

/* ── Citações NT (vinho) ── */
.nt-cite {
  color: #e07090 !important;
  font-weight: 700 !important;
  background: rgba(122,35,64,.18) !important;
  padding: 1px 5px !important;
  border-radius: 4px !important;
  font-size: 0.91em !important;
  white-space: nowrap !important;
}

/* ── Medidas / números (laranja) ── */
.nt-measure {
  color: #f0a050 !important;
  font-weight: 600 !important;
  background: rgba(240,160,80,.1) !important;
  padding: 1px 5px !important;
  border-radius: 4px !important;
  font-size: 0.91em !important;
  white-space: nowrap !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] > div {
  background: var(--bg2) !important;
  border: 1.5px solid rgba(255,255,255,.12) !important;
  border-radius: 14px !important;
  transition: border-color .2s, box-shadow .2s !important;
}
[data-testid="stChatInput"] > div:focus-within {
  border-color: var(--wine) !important;
  box-shadow: 0 0 0 3px var(--wine-glow) !important;
}
[data-testid="stChatInput"] textarea {
  color: var(--text) !important;
  font-size: .95rem !important;
}
[data-testid="stChatInput"] button[kind="primary"],
[data-testid="stChatInputSubmitButton"] {
  background: linear-gradient(135deg, var(--wine), var(--wine-dk)) !important;
  border-radius: 10px !important;
  color: white !important;
  border: none !important;
}

/* ── Loading dots ── */
.nt-load { font-size:.9rem; color:#9090b8; padding:.35rem 0; }
.nt-d { display:inline-block; opacity:0; animation:ntd 1.5s infinite; }
.nt-d:nth-child(2){ animation-delay:.4s; }
.nt-d:nth-child(3){ animation-delay:.8s; }
@keyframes ntd { 0%,60%,100%{opacity:0;} 30%{opacity:1;} }

/* ══════════════ MOBILE ══════════════ */
@media (max-width: 640px) {
  /* Bubbles ocupam mais largura no celular */
  [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
    [data-testid="stChatMessageContent"] {
    max-width: 88% !important;
  }
  [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
    [data-testid="stChatMessageContent"] {
    max-width: 96% !important;
  }
  /* Header do chat: texto menor */
  .main .block-container,
  [data-testid="stAppViewBlockContainer"] {
    padding-left: 0.6rem !important;
    padding-right: 0.6rem !important;
  }
}

/* ── Example prompt buttons ── */
div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
  background: var(--bg2) !important;
  border: 1px solid var(--border) !important;
  color: var(--muted) !important;
  border-radius: 10px !important;
  font-size: .83rem !important;
  transition: all .2s !important;
  text-align: left !important;
  padding: .65rem .85rem !important;
  line-height: 1.4 !important;
  height: auto !important;
  min-height: 3rem !important;
}
div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
  border-color: var(--wine) !important;
  color: var(--text) !important;
  background: var(--bg3) !important;
}
</style>
""", unsafe_allow_html=True)


# ── Funções de busca ──────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="Carregando índice de normas...")
def carregar_indice():
    if not ARQUIVO_CHUNKS.exists() or not ARQUIVO_BM25.exists():
        return None, None
    with open(ARQUIVO_CHUNKS, "rb") as f:
        chunks = pickle.load(f)
    with open(ARQUIVO_BM25, "rb") as f:
        bm25 = pickle.load(f)
    return chunks, bm25


def tokenizar(texto):
    return re.findall(r'\b[a-z\xe1\xe9\xed\xf3\xfa\xe0\xe3\xf5\xe2\xea\xee\xf4\xfb\xe7]+\b',
                      texto.lower())


SINONIMOS = {
    "caminhao":      ["viatura", "veiculo", "autoviatura"],
    "bombeiro":      ["bombeiros", "cbmerj", "corpo"],
    "re":            ["marcha", "recuo", "retrocesso", "retorno", "manobra"],
    "voltar":        ["recuar", "retroceder", "manobra", "retorno"],
    "andar":         ["pavimento", "piso"],
    "escada":        ["escadaria", "saida", "emergencia"],
    "extintor":      ["extintores", "portatil", "protecao"],
    "hidrante":      ["hidrantes", "mangotinho", "mangueira"],
    "sprinkler":     ["chuveiro", "automatico", "aspersao", "chuveiros"],
    "alarme":        ["deteccao", "sensor", "acionador"],
    "saida":         ["emergencia", "evacuacao", "escape"],
    "corredor":      ["passagem", "circulacao", "acesso"],
    "altura":        ["pavimentos", "andares", "metros", "piso"],
    "reserva":       ["reservatorio", "agua", "rti", "volume"],
    "residencial":   ["habitacao", "multifamiliar", "unifamiliar", "residencia",
                      "apartamento", "a-1", "a-2", "a-3", "a-4", "a-5"],
    "comercial":     ["loja", "escritorio", "servicos", "d-1", "d-2", "d-3",
                      "c-1", "c-2", "c-3"],
    "industrial":    ["fabrica", "deposito", "armazem", "i-1", "i-2", "i-3"],
    "obrigatorio":   ["exigido", "obrigatoriedade", "deve", "necessario",
                      "requerido", "exige"],
    "classificacao": ["ocupacao", "risco", "grupo", "divisao", "categoria",
                      "anexo", "tabela"],
    "area":          ["m2", "metros", "quadrados", "metragem", "tamanho"],
    "pavimento":     ["andar", "piso", "nivel", "subsolo", "terreo"],
    "edificio":      ["edificacao", "predio", "construcao", "imóvel", "imovel"],
    "hotel":         ["hospedagem", "pousada", "hostel", "h-1", "h-2", "h-3"],
    "hospital":      ["clinica", "saude", "medico", "e-1", "e-2", "e-3"],
}


def expandir_query(pergunta):
    import unicodedata
    def normalizar(s):
        return ''.join(c for c in unicodedata.normalize('NFD', s)
                       if unicodedata.category(c) != 'Mn')
    tokens = re.findall(r'\b\w+\b', normalizar(pergunta.lower()))
    extras = []
    for t in tokens:
        if t in SINONIMOS:
            extras.extend(SINONIMOS[t])
    return tokenizar(pergunta) + extras


def buscar(pergunta, chunks, bm25):
    tokens = expandir_query(pergunta)
    scores = bm25.get_scores(tokens)
    indices_top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:NUM_CHUNKS]
    selecionados = {i for i in indices_top if scores[i] > 0}

    top_por_nt: dict = {}
    for i, score in enumerate(scores):
        if score <= 0:
            continue
        nt = chunks[i]["nt"]
        if nt not in top_por_nt:
            top_por_nt[nt] = []
        top_por_nt[nt].append((i, score))
    for lista in top_por_nt.values():
        lista.sort(key=lambda x: x[1], reverse=True)
        for i, _ in lista[:4]:
            selecionados.add(i)

    return [chunks[i] for i in sorted(selecionados, key=lambda i: scores[i], reverse=True)]


def montar_contexto(resultados):
    return "\n\n---\n\n".join(
        f"[NT-{r['nt']} – {r['titulo']}]\n{r['texto']}" for r in resultados
    )


def consultar_ia(mensagens, contexto, api_key):
    cliente = anthropic.Anthropic(api_key=api_key)
    system = (
        "Você é um especialista em segurança contra incêndio e pânico, "
        "com profundo conhecimento nas Normas Técnicas do Corpo de Bombeiros "
        "Militar do Estado do Rio de Janeiro (CBMERJ). "
        "Responda de forma direta, objetiva e técnica com base nos trechos fornecidos. "
        "Cite o número da NT e o item quando disponível. "
        "Extraia e apresente valores, dimensões, condições e exceções. "
        "NUNCA oriente o usuário a consultar a NT diretamente. "
        "Mantenha o contexto de toda a conversa ao responder. "
        "Trechos com '?' no lugar de acentos são texto técnico em português — leia normalmente. "
        "Se os trechos não contiverem a resposta, diga objetivamente o que está faltando."
        f"\n\nTRECHOS DAS NTs DO CBMERJ:\n\n{contexto}"
    )
    resposta = cliente.messages.create(
        model=MODELO, max_tokens=1500, system=system, messages=mensagens,
    )
    return (resposta.content[0].text,
            resposta.usage.input_tokens,
            resposta.usage.output_tokens)


def nova_conversa():
    return {
        "id": str(uuid.uuid4()),
        "titulo": "Nova conversa",
        "mensagens": [],
        "criado_em": datetime.now().isoformat()
    }


def destacar_citacoes(texto: str) -> str:
    """Destaca referências a NTs (vinho) e medidas (laranja) no texto da IA."""
    # NT references: NT-23, NT 23, NT23, NT.23
    texto = re.sub(
        r'\b(NT[-\s.]?\d{1,3})\b',
        r'<span class="nt-cite">\1</span>',
        texto
    )
    # Item / seção references: item 5.1.2, subitem 4.3, seção 3.2.1
    texto = re.sub(
        r'\b((?:item|subitem|seção|artigo)\s+\d+(?:\.\d+)+)\b',
        r'<span class="nt-cite">\1</span>',
        texto, flags=re.IGNORECASE
    )
    # Measurements: 1,50 m  /  30 metros  /  500 litros  /  2 kPa
    texto = re.sub(
        r'\b(\d+(?:[,.]\d+)?\s*(?:m²|m2|m³|m3|cm|mm|metros?|m\b|litros?|kPa|bar|kg))\b',
        r'<span class="nt-measure">\1</span>',
        texto, flags=re.IGNORECASE
    )
    return texto


# ── Carregar índice ───────────────────────────────────────────────────────────
chunks, bm25 = carregar_indice()

if "conversa_atual" not in st.session_state:
    st.session_state.conversa_atual = nova_conversa()

badge = badge_atual(usuario["pontos"])

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="margin-bottom:1rem;">
      <div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.6rem;">
        <div style="width:34px;height:34px;border-radius:9px;
                    background:linear-gradient(135deg,#7a2340,#561629);
                    display:flex;align-items:center;justify-content:center;
                    font-size:1rem;flex-shrink:0;">🔥</div>
        <span style="font-size:1rem;font-weight:800;color:#fff;letter-spacing:-.01em;">
          Mr. Incêndio
        </span>
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

    conversas = listar_conversas_db(uid)
    pode_criar = len(conversas) < MAX_CONVERSAS

    if st.button("✏️ Nova conversa", use_container_width=True, disabled=not pode_criar):
        nova = nova_conversa()
        salvar_conversa_db(nova, uid)
        st.session_state.conversa_atual = nova
        st.rerun()
    if not pode_criar:
        st.caption(f"Limite de {MAX_CONVERSAS} conversas atingido.")

    st.divider()

    for conv in conversas:
        ativa = conv["id"] == st.session_state.conversa_atual["id"]
        titulo = conv["titulo"][:26] + ("…" if len(conv["titulo"]) > 26 else "")
        col_btn, col_del = st.columns([5, 1])
        with col_btn:
            label = f"**› {titulo}**" if ativa else titulo
            if st.button(label, key=f"conv_{conv['id']}", use_container_width=True):
                st.session_state.conversa_atual = conv
                st.rerun()
        with col_del:
            if st.button("🗑", key=f"del_{conv['id']}"):
                excluir_conversa_db(conv["id"], uid)
                resto = listar_conversas_db(uid)
                st.session_state.conversa_atual = resto[0] if resto else nova_conversa()
                st.rerun()

    st.divider()
    if chunks:
        st.caption(f"📚 {len(chunks)} trechos indexados")
    if st.button("🚪 Sair", use_container_width=True):
        fazer_logout()
        st.rerun()

# ── Área principal ────────────────────────────────────────────────────────────
header_usuario(usuario["nome"], usuario["creditos"], usuario["pontos"], badge)
nav_inferior("chat", usuario["tipo"])

# Cabeçalho do chat
st.markdown("""
<div style="display:flex;align-items:center;gap:.75rem;
            margin-bottom:1.25rem;padding-bottom:1rem;
            border-bottom:1px solid rgba(255,255,255,0.07);">
  <div style="width:40px;height:40px;border-radius:11px;flex-shrink:0;
              background:linear-gradient(135deg,#7a2340,#561629);
              display:flex;align-items:center;justify-content:center;
              font-size:1.2rem;box-shadow:0 3px 12px rgba(122,35,64,.3);">🔥</div>
  <div>
    <div style="font-size:1.05rem;font-weight:800;color:#fff;letter-spacing:-.01em;">
      Consultor de NTs
    </div>
    <div style="font-size:.78rem;color:#9090b8;margin-top:.1rem;">
      CBMERJ · Normas Técnicas de Segurança contra Incêndio e Pânico
    </div>
  </div>
  <div style="margin-left:auto;display:flex;align-items:center;gap:.4rem;">
    <div style="width:8px;height:8px;border-radius:50%;
                background:#4ade80;box-shadow:0 0 6px rgba(74,222,128,.5);"></div>
    <span style="font-size:.75rem;color:#9090b8;">online</span>
  </div>
</div>
""", unsafe_allow_html=True)

if chunks is None:
    st.error("⚠️ Índice não encontrado. Execute no terminal:")
    st.code("python baixar_normas.py\npython indexar.py")
    st.stop()

conversa  = st.session_state.conversa_atual
mensagens = conversa.get("mensagens", [])

# ── Histórico de mensagens ────────────────────────────────────────────────────
for msg in mensagens:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(destacar_citacoes(msg["content"]), unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# ── Tela de boas-vindas (sem mensagens) ──────────────────────────────────────
if not mensagens:
    st.markdown("""
    <div style="text-align:center;padding:2rem 0 1rem;">
      <div style="font-size:2.5rem;margin-bottom:.6rem;">🔥</div>
      <div style="font-size:1.1rem;font-weight:700;color:#f0f0f8;margin-bottom:.4rem;">
        Olá! Sou o Mr. Incêndio
      </div>
      <div style="font-size:.85rem;color:#9090b8;max-width:460px;
                  margin:0 auto;line-height:1.6;">
        Faça qualquer pergunta sobre as normas técnicas do CBMERJ.<br>
        Vou buscar nas NTs e trazer a resposta precisa para você.
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-size:.8rem;font-weight:600;color:#60607a;
                text-transform:uppercase;letter-spacing:.08em;
                margin-bottom:.6rem;margin-top:.5rem;">
      💡 Sugestões
    </div>
    """, unsafe_allow_html=True)

    exemplos = [
        "Qual a largura mínima de escada de emergência para edifício residencial?",
        "Quantos extintores são necessários por pavimento?",
        "Quais sistemas são obrigatórios para edifício com mais de 12 andares?",
        "Como calcular o número de hidrantes em um galpão industrial?",
        "Qual a reserva técnica de incêndio mínima para edifício comercial?",
        "Quando é obrigatório sprinkler em edifício residencial?",
    ]
    col1, col2 = st.columns(2)
    for i, p in enumerate(exemplos):
        col = col1 if i % 2 == 0 else col2
        if col.button(p, use_container_width=True, key=f"ex_{i}"):
            st.session_state.pergunta_sugerida = p
            st.rerun()

# ── Input ─────────────────────────────────────────────────────────────────────
pergunta_sugerida = st.session_state.pop("pergunta_sugerida", "")
pergunta = st.chat_input("Digite sua dúvida sobre as NTs do CBMERJ...")
if not pergunta and pergunta_sugerida:
    pergunta = pergunta_sugerida

if pergunta:
    if not api_key:
        st.error("⚠️ Chave API não configurada. Contate o administrador.")
        st.stop()

    usuario = get_usuario_sessao()
    if not tem_credito(uid):
        st.error("⚠️ **Créditos insuficientes.** Acesse a aba 📊 Créditos para recarregar.")
        st.stop()

    with st.chat_message("user"):
        st.markdown(pergunta)
    mensagens.append({"role": "user", "content": pergunta})

    with st.chat_message("assistant"):
        _loading = st.empty()
        _loading.markdown(
            '<span class="nt-load">consultando'
            '<span class="nt-d">.</span>'
            '<span class="nt-d">.</span>'
            '<span class="nt-d">.</span>'
            '</span>',
            unsafe_allow_html=True
        )

        resultados = buscar(pergunta, chunks, bm25)

        if not resultados:
            _loading.empty()
            resposta = "Não foram encontrados trechos relevantes nas NTs indexadas para esta pergunta."
            st.markdown(resposta)
            tokens_in, tokens_out = 0, 0
        else:
            contexto = montar_contexto(resultados)
            historico_api = [{"role": m["role"], "content": m["content"]}
                             for m in mensagens]
            try:
                resposta, tokens_in, tokens_out = consultar_ia(
                    historico_api, contexto, api_key
                )
            except anthropic.AuthenticationError:
                _loading.empty()
                st.error("❌ Chave API inválida.")
                st.stop()
            except Exception as e:
                _loading.empty()
                st.error(f"❌ Erro na API: {e}")
                st.stop()

            _loading.empty()
            st.markdown(destacar_citacoes(resposta), unsafe_allow_html=True)

            with st.expander("📄 Ver trechos consultados das NTs"):
                for r in resultados:
                    st.markdown(f"**NT-{r['nt']} – {r['titulo']}**")
                    st.caption(r["texto"][:400] + "…" if len(r["texto"]) > 400 else r["texto"])
                    st.divider()

    deduzir_credito(uid, tokens_in, tokens_out)

    mensagens.append({"role": "assistant", "content": resposta})
    if len(mensagens) == 2:
        conversa["titulo"] = pergunta[:60]
    conversa["mensagens"] = mensagens
    st.session_state.conversa_atual = conversa
    salvar_conversa_db(conversa, uid)
