# -*- coding: utf-8 -*-
"""Fixtures compartilhadas pelos testes."""
import sys
from pathlib import Path

import pytest

# Garante que a raiz do projeto está no sys.path ao rodar pytest
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import rag  # noqa: E402


@pytest.fixture(scope="session")
def indice():
    """Carrega o índice real (chunks + BM25) uma única vez por sessão."""
    chunks, bm25 = rag.carregar_indice()
    if chunks is None or bm25 is None:
        pytest.skip("Índice não encontrado — rode 'python indexar.py' antes.")
    return chunks, bm25
