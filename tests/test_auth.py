# -*- coding: utf-8 -*-
"""Testes das validações e do hash de senha (auth.py)."""
import pytest

from auth import (_cnpj_valido, _cpf_valido, _email_valido, _senha_forte,
                  hash_senha, verificar_senha)


@pytest.mark.parametrize("email,esperado", [
    ("fulano@exemplo.com", True),
    ("f.ulano+tag@sub.exemplo.com.br", True),
    ("semarroba.com", False),
    ("a@b", False),
    ("", False),
])
def test_email_valido(email, esperado):
    assert _email_valido(email) is esperado


@pytest.mark.parametrize("senha,ok", [
    ("abcd1234", True),
    ("Senha123", True),
    ("curta1", False),      # < 8
    ("somenteletras", False),  # sem número
    ("12345678", False),    # sem letra
])
def test_senha_forte(senha, ok):
    assert _senha_forte(senha)[0] is ok


def test_cpf_valido():
    assert _cpf_valido("111.444.777-35") is True
    assert _cpf_valido("111.444.777-00") is False
    assert _cpf_valido("000.000.000-00") is False  # todos iguais
    assert _cpf_valido("123") is False


def test_cnpj_valido():
    assert _cnpj_valido("11.222.333/0001-81") is True
    assert _cnpj_valido("11.222.333/0001-00") is False
    assert _cnpj_valido("00.000.000/0000-00") is False


def test_hash_senha_roundtrip():
    h = hash_senha("MinhaSenha123")
    assert h != "MinhaSenha123"          # nunca em texto puro
    assert verificar_senha("MinhaSenha123", h) is True
    assert verificar_senha("errada", h) is False


def test_hash_senha_salgado():
    # Dois hashes da mesma senha devem diferir (salt aleatório)
    assert hash_senha("abc12345") != hash_senha("abc12345")
