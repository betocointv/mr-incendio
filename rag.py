# -*- coding: utf-8 -*-
"""
Núcleo de busca (RAG) — recuperação dos trechos das NTs via BM25.

Módulo puro, sem Streamlit: pode ser importado por páginas da UI e por testes.
Fluxo: pergunta -> expandir_query (sinônimos) -> BM25.get_scores ->
seleção dos melhores trechos (globais + top por NT) -> montar_contexto.
"""
from __future__ import annotations

import pickle
import re
import unicodedata
from pathlib import Path
from typing import Optional

# ── Parâmetros de recuperação ─────────────────────────────────────────────────
NUM_CHUNKS = 25          # nº de trechos globais por score
TOP_POR_NT = 4           # trechos extras garantidos por NT relevante

ARQUIVO_CHUNKS = Path("dados/chunks.pkl")
ARQUIVO_BM25   = Path("dados/bm25.pkl")

_LETRAS = r'a-z\xe1\xe9\xed\xf3\xfa\xe0\xe3\xf5\xe2\xea\xee\xf4\xfb\xe7'


# ── Expansão de query com sinônimos de domínio ────────────────────────────────
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


def tokenizar(texto: str) -> list[str]:
    """Quebra o texto em tokens, preservando letras acentuadas."""
    return re.findall(rf'\b[{_LETRAS}]+\b', texto.lower())


def _sem_acento(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


def expandir_query(pergunta: str) -> list[str]:
    """Tokens da pergunta + sinônimos de domínio (casados sem acento)."""
    tokens = re.findall(r'\b\w+\b', _sem_acento(pergunta.lower()))
    extras: list[str] = []
    for t in tokens:
        if t in SINONIMOS:
            extras.extend(SINONIMOS[t])
    return tokenizar(pergunta) + extras


def buscar(pergunta: str, chunks: list, bm25) -> list:
    """
    Recupera os trechos mais relevantes para a pergunta.
    Combina os melhores globais com os melhores de cada NT relevante,
    para não perder uma norma inteira por causa de um único trecho dominante.
    """
    tokens = expandir_query(pergunta)
    scores = bm25.get_scores(tokens)

    indices_top = sorted(range(len(scores)),
                         key=lambda i: scores[i], reverse=True)[:NUM_CHUNKS]
    selecionados = {i for i in indices_top if scores[i] > 0}

    top_por_nt: dict = {}
    for i, score in enumerate(scores):
        if score <= 0:
            continue
        top_por_nt.setdefault(chunks[i]["nt"], []).append((i, score))
    for lista in top_por_nt.values():
        lista.sort(key=lambda x: x[1], reverse=True)
        for i, _ in lista[:TOP_POR_NT]:
            selecionados.add(i)

    return [chunks[i] for i in
            sorted(selecionados, key=lambda i: scores[i], reverse=True)]


def montar_contexto(resultados: list) -> str:
    """Formata os trechos recuperados como contexto para o LLM."""
    return "\n\n---\n\n".join(
        f"[NT-{r['nt']} – {r['titulo']}]\n{r['texto']}" for r in resultados
    )


def carregar_indice(chunks_path: Path = ARQUIVO_CHUNKS,
                    bm25_path: Path = ARQUIVO_BM25):
    """Carrega (chunks, bm25) dos pickles. Retorna (None, None) se faltarem."""
    chunks_path = Path(chunks_path)
    bm25_path = Path(bm25_path)
    if not chunks_path.exists() or not bm25_path.exists():
        return None, None
    with open(chunks_path, "rb") as f:
        chunks = pickle.load(f)
    with open(bm25_path, "rb") as f:
        bm25 = pickle.load(f)
    return chunks, bm25
