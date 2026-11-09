# -*- coding: utf-8 -*-
"""
Teste de referência do RAG: 15 perguntas reais, cada uma com a NT correta.

Verifica se a BUSCA (BM25 + sinônimos) recupera o trecho da norma certa —
SEM chamar a IA. É um teste de recall: a NT esperada deve aparecer entre os
primeiros NTs recuperados, garantindo que o trecho certo chega ao contexto.
"""
import rag

# Até qual posição (entre os NTs distintos recuperados, ordenados por score)
# aceitamos a NT correta. Margem folgada mas significativa.
TOP_NT = 6

# (pergunta, NT esperada) — mapeamento verificado contra o índice real.
PERGUNTAS_REFERENCIA = [
    ("Qual a capacidade extintora mínima dos extintores portáteis?",      "2-01"),
    ("Qual a vazão mínima de um hidrante e mangotinho?",                   "2-02"),
    ("Quando é obrigatório sistema de chuveiros automáticos sprinkler?",   "2-03-P1"),
    ("Como dimensionar o conjunto de pressurização e bombas de incêndio?", "2-04"),
    ("Quais as cores da sinalização de segurança contra incêndio?",        "2-05"),
    ("Qual a autonomia mínima da iluminação de emergência?",               "2-06"),
    ("Onde instalar acionador manual do sistema de detecção e alarme?",    "2-07"),
    ("Qual a largura mínima das saídas de emergência e escadas?",          "2-08"),
    ("Como funciona a pressurização de escada de emergência?",             "2-09"),
    ("O que deve conter o plano de emergência PECIP?",                     "2-10"),
    ("Qual o número mínimo de brigadistas de incêndio por pavimento?",     "2-11"),
    ("Quando é exigido SPDA para descargas atmosféricas?",                 "2-12"),
    ("Como dimensionar o controle de fumaça por exaustão?",                "2-14"),
    ("Como é feita a classificação das edificações quanto ao risco?",      "1-04"),
    ("Qual a central de gás GLP predial e distância do medidor?",          "3-02"),
]


def _nts_distintos(resultados):
    """NTs distintas na ordem em que aparecem (já ordenadas por score)."""
    ordem = []
    for r in resultados:
        if r["nt"] not in ordem:
            ordem.append(r["nt"])
    return ordem


def test_quantidade_de_perguntas():
    assert len(PERGUNTAS_REFERENCIA) == 15


def test_recall_por_pergunta(indice):
    """Cada pergunta deve recuperar a NT esperada entre as TOP_NT primeiras."""
    chunks, bm25 = indice
    falhas = []
    for pergunta, nt_esperada in PERGUNTAS_REFERENCIA:
        resultados = rag.buscar(pergunta, chunks, bm25)
        assert resultados, f"Nenhum trecho recuperado para: {pergunta!r}"
        ordem = _nts_distintos(resultados)
        pos = ordem.index(nt_esperada) + 1 if nt_esperada in ordem else None
        if pos is None or pos > TOP_NT:
            falhas.append((pergunta, nt_esperada, pos, ordem[:TOP_NT]))

    assert not falhas, "NT esperada fora do top {}:\n{}".format(
        TOP_NT,
        "\n".join(f"  - {p!r} esperava {nt} (pos={pos}); top={top}"
                  for p, nt, pos, top in falhas),
    )


def test_recall_agregado(indice):
    """Pelo menos 13 das 15 perguntas devem acertar (robustez do índice)."""
    chunks, bm25 = indice
    acertos = 0
    for pergunta, nt_esperada in PERGUNTAS_REFERENCIA:
        ordem = _nts_distintos(rag.buscar(pergunta, chunks, bm25))
        if nt_esperada in ordem[:TOP_NT]:
            acertos += 1
    assert acertos >= 13, f"Só {acertos}/15 acertaram (mínimo 13)."


# ── Testes unitários da lógica de busca ───────────────────────────────────────

def test_expandir_query_adiciona_sinonimos():
    tokens = rag.expandir_query("preciso de extintor")
    assert "extintor" in tokens
    assert "extintores" in tokens   # sinônimo injetado
    assert "protecao" in tokens


def test_expandir_query_ignora_acentos_no_match():
    # "classificação" (com acento) deve casar a chave "classificacao"
    tokens = rag.expandir_query("classificação de risco")
    assert "ocupacao" in tokens


def test_montar_contexto_formata_trechos():
    fake = [{"nt": "2-01", "titulo": "Extintores", "texto": "trecho a"},
            {"nt": "2-02", "titulo": "Hidrantes", "texto": "trecho b"}]
    ctx = rag.montar_contexto(fake)
    assert "[NT-2-01 – Extintores]" in ctx
    assert "trecho b" in ctx
    assert "---" in ctx   # separador entre trechos


def test_buscar_sem_resultado_para_ruido(indice):
    chunks, bm25 = indice
    # Palavra inexistente no domínio não deve casar nada relevante
    resultados = rag.buscar("xyzzy qwerty zzzznadaxyz", chunks, bm25)
    assert resultados == []
