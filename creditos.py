"""
Sistema de créditos, pontos e gamificação.
"""

from __future__ import annotations

from typing import Optional
from db import (atualizar_creditos, atualizar_pontos,
                registrar_transacao, buscar_usuario_id)

CUSTO_POR_PERGUNTA  = 1.0
PONTOS_POR_PERGUNTA = 1
PONTOS_PARA_TROCAR  = 50
CREDITOS_POR_TROCA  = 5

BADGES = [
    {"key": "iniciante",    "nome": "🔥 Iniciante",      "min": 10,  "desc": "10 consultas realizadas"},
    {"key": "projetista",   "nome": "📐 Projetista",      "min": 50,  "desc": "50 consultas realizadas"},
    {"key": "especialista", "nome": "🏗️ Especialista",   "min": 200, "desc": "200 consultas realizadas"},
    {"key": "mestre",       "nome": "🚒 Mestre CBMERJ",  "min": 500, "desc": "500 consultas realizadas"},
]


def tem_credito(usuario_id: int) -> bool:
    u = buscar_usuario_id(usuario_id)
    if not u:
        return False
    if u["tipo"] == "funcionario" and u["empresa_id"]:
        from db import conexao
        with conexao() as conn:
            row = conn.execute(
                "SELECT creditos FROM usuarios WHERE tipo='empresa_admin' AND empresa_id=?",
                (u["empresa_id"],)
            ).fetchone()
        return bool(row and row["creditos"] >= CUSTO_POR_PERGUNTA)
    return u["creditos"] >= CUSTO_POR_PERGUNTA


def deduzir_credito(usuario_id: int, tokens_input: int = 0, tokens_output: int = 0):
    u = buscar_usuario_id(usuario_id)
    if not u:
        return

    custo_usd = (tokens_input / 1_000_000 * 0.80) + (tokens_output / 1_000_000 * 4.00)

    alvo_id = usuario_id
    if u["tipo"] == "funcionario" and u["empresa_id"]:
        from db import conexao
        with conexao() as conn:
            admin = conn.execute(
                "SELECT id FROM usuarios WHERE tipo='empresa_admin' AND empresa_id=?",
                (u["empresa_id"],)
            ).fetchone()
        if admin:
            alvo_id = admin["id"]

    atualizar_creditos(alvo_id, -CUSTO_POR_PERGUNTA)
    registrar_transacao(
        usuario_id=usuario_id,
        tipo="uso",
        creditos=-CUSTO_POR_PERGUNTA,
        tokens_input=tokens_input,
        tokens_output=tokens_output,
        custo_usd=custo_usd,
        descricao="Consulta às NTs",
    )
    atualizar_pontos(usuario_id, PONTOS_POR_PERGUNTA)


def adicionar_creditos(usuario_id: int, quantidade: float,
                       descricao: str = "Compra de créditos"):
    atualizar_creditos(usuario_id, quantidade)
    registrar_transacao(
        usuario_id=usuario_id,
        tipo="compra",
        creditos=quantidade,
        descricao=descricao,
    )


def trocar_pontos(usuario_id: int) -> tuple:
    u = buscar_usuario_id(usuario_id)
    if not u:
        return False, "Usuário não encontrado."
    if u["pontos"] < PONTOS_PARA_TROCAR:
        return False, f"Você precisa de {PONTOS_PARA_TROCAR} pontos. Você tem {u['pontos']}."

    atualizar_pontos(usuario_id, -PONTOS_PARA_TROCAR)
    atualizar_creditos(usuario_id, CREDITOS_POR_TROCA)
    registrar_transacao(
        usuario_id=usuario_id,
        tipo="troca_pontos",
        creditos=CREDITOS_POR_TROCA,
        descricao=f"Troca de {PONTOS_PARA_TROCAR} pontos por {CREDITOS_POR_TROCA} créditos",
    )
    return True, f"✅ Troca realizada! +{CREDITOS_POR_TROCA} créditos adicionados."


def badge_atual(pontos: int) -> str:
    badge = "🌱 Novo usuário"
    for b in BADGES:
        if pontos >= b["min"]:
            badge = b["nome"]
    return badge


def badges_conquistados(pontos: int) -> list:
    return [b for b in BADGES if pontos >= b["min"]]


def proximo_badge(pontos: int) -> Optional[dict]:
    for b in BADGES:
        if pontos < b["min"]:
            return {"nome": b["nome"], "faltam": b["min"] - pontos, "meta": b["min"]}
    return None


def total_consultas(usuario_id: int) -> int:
    from db import conexao
    with conexao() as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM transacoes WHERE usuario_id=? AND tipo='uso'",
            (usuario_id,)
        ).fetchone()
    return row[0] if row else 0
