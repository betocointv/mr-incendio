# -*- coding: utf-8 -*-
"""Testes da lógica de gamificação (creditos.py) — funções puras."""
from creditos import (BADGES, badge_atual, badges_conquistados,
                      proximo_badge)


def test_badge_atual_progressao():
    assert badge_atual(0) == "🌱 Novo usuário"
    assert badge_atual(100) == BADGES[0]["nome"]      # Iniciante
    assert badge_atual(499) == BADGES[0]["nome"]
    assert badge_atual(500) == BADGES[1]["nome"]      # Projetista
    assert badge_atual(5000) == BADGES[-1]["nome"]    # Mestre CBMERJ


def test_badges_conquistados():
    assert badges_conquistados(0) == []
    assert len(badges_conquistados(500)) == 2
    assert len(badges_conquistados(9999)) == len(BADGES)


def test_proximo_badge():
    prox = proximo_badge(0)
    assert prox["meta"] == 100
    assert prox["faltam"] == 100

    prox = proximo_badge(120)
    assert prox["meta"] == 500
    assert prox["faltam"] == 380

    # Acima do último badge não há próximo
    assert proximo_badge(10000) is None
