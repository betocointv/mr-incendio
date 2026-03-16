"""
Autenticação — hash de senhas, login, registro, rate limiting.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import streamlit as st

# ── Constantes ────────────────────────────────────────────────────────────────
MAX_TENTATIVAS    = 5   # tentativas antes do bloqueio
BLOQUEIO_MINUTOS  = 15  # tempo de bloqueio em minutos


# ── Helpers de validação ──────────────────────────────────────────────────────

def _email_valido(email: str) -> bool:
    """Valida formato de e-mail via regex."""
    return bool(re.match(
        r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$',
        email
    ))


def _senha_forte(senha: str) -> tuple[bool, str]:
    """Retorna (válida, mensagem_erro). Exige ≥8 chars, letra e número."""
    if len(senha) < 8:
        return False, "A senha deve ter pelo menos 8 caracteres."
    if not re.search(r'[A-Za-z]', senha):
        return False, "A senha deve conter pelo menos uma letra."
    if not re.search(r'[0-9]', senha):
        return False, "A senha deve conter pelo menos um número."
    return True, ""


def _cpf_valido(cpf: str) -> bool:
    """Valida CPF com algoritmo de dígitos verificadores."""
    d = re.sub(r'\D', '', cpf)
    if len(d) != 11 or len(set(d)) == 1:
        return False
    # Primeiro dígito verificador
    s = sum(int(d[i]) * (10 - i) for i in range(9))
    r = (s * 10) % 11
    if r == 10: r = 0
    if r != int(d[9]): return False
    # Segundo dígito verificador
    s = sum(int(d[i]) * (11 - i) for i in range(10))
    r = (s * 10) % 11
    if r == 10: r = 0
    return r == int(d[10])


def _cnpj_valido(cnpj: str) -> bool:
    """Valida CNPJ com algoritmo de dígitos verificadores."""
    d = re.sub(r'\D', '', cnpj)
    if len(d) != 14 or len(set(d)) == 1:
        return False
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    s  = sum(int(d[i]) * pesos1[i] for i in range(12))
    r  = s % 11
    d1 = 0 if r < 2 else 11 - r
    if d1 != int(d[12]): return False
    s  = sum(int(d[i]) * pesos2[i] for i in range(13))
    r  = s % 11
    d2 = 0 if r < 2 else 11 - r
    return d2 == int(d[13])


# ── Hash de senha ─────────────────────────────────────────────────────────────

def hash_senha(senha: str) -> str:
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def verificar_senha(senha: str, hash_salvo: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode(), hash_salvo.encode())
    except Exception:
        return False


# ── Login com rate limiting ───────────────────────────────────────────────────

def login(email: str, senha: str) -> Optional[dict]:
    """
    Tenta fazer login. Retorna:
      - dict do usuário em caso de sucesso
      - {"bloqueado": True, "minutos": N} se conta está bloqueada
      - None se credenciais inválidas
    """
    from db import (buscar_usuario_email, registrar_tentativa_login,
                    resetar_tentativas_login, bloquear_usuario_login)

    usuario = buscar_usuario_email(email.strip().lower())
    if not usuario:
        return None  # não revela se e-mail existe

    # Verifica bloqueio por tentativas excessivas
    bloqueado_ate = usuario["bloqueado_ate"] or ""
    if bloqueado_ate:
        try:
            ate = datetime.fromisoformat(bloqueado_ate)
            if datetime.now() < ate:
                minutos = max(1, int((ate - datetime.now()).total_seconds() / 60) + 1)
                return {"bloqueado": True, "minutos": minutos}
            else:
                # Bloqueio expirado — reseta automaticamente
                resetar_tentativas_login(usuario["id"])
        except Exception:
            pass

    if not verificar_senha(senha, usuario["senha_hash"]):
        tentativas = registrar_tentativa_login(usuario["id"])
        if tentativas >= MAX_TENTATIVAS:
            bloquear_usuario_login(usuario["id"], BLOQUEIO_MINUTOS)
            return {"bloqueado": True, "minutos": BLOQUEIO_MINUTOS}
        return None

    # Login bem-sucedido — reseta contagem de tentativas
    resetar_tentativas_login(usuario["id"])
    return dict(usuario)


# ── Registro ──────────────────────────────────────────────────────────────────

def registrar(nome: str, email: str, senha: str, tipo: str,
              empresa_nome: str = "", cnpj: str = "",
              telefone: str = "", cpf: str = "") -> tuple:
    """
    Registra novo usuário. Retorna (sucesso: bool, mensagem: str).
    Para tipo 'empresa_admin', cria também a empresa.
    """
    from db import criar_usuario, criar_empresa, buscar_usuario_email

    email = email.strip().lower()
    nome  = nome.strip()

    # Validações básicas
    if not nome:
        return False, "Informe seu nome completo."
    if len(nome) < 3:
        return False, "O nome deve ter pelo menos 3 caracteres."
    if not email:
        return False, "Informe seu e-mail."
    if not _email_valido(email):
        return False, "E-mail inválido. Verifique o formato."
    if buscar_usuario_email(email):
        return False, "Este e-mail já está cadastrado."

    # Senha forte
    ok_senha, msg_senha = _senha_forte(senha)
    if not ok_senha:
        return False, msg_senha

    if not telefone.strip():
        return False, "Informe seu telefone."

    senha_hash = hash_senha(senha)
    empresa_id = None

    if tipo == "empresa_admin":
        if not empresa_nome.strip():
            return False, "Informe o nome da empresa."
        if not _cnpj_valido(cnpj):
            return False, "CNPJ inválido. Verifique os dígitos verificadores."
        empresa_id = criar_empresa(empresa_nome.strip(), cnpj.strip())
    else:
        if not _cpf_valido(cpf):
            return False, "CPF inválido. Verifique os dígitos verificadores."

    criar_usuario(nome, email, senha_hash, tipo, empresa_id,
                  telefone=telefone.strip(), cpf=cpf.strip())
    return True, "Conta criada com sucesso! 🎉 Você ganhou 10 créditos de boas-vindas."


# ── Sessão ────────────────────────────────────────────────────────────────────

def sessao_logada() -> bool:
    return bool(st.session_state.get("usuario_id"))


def get_usuario_sessao() -> Optional[dict]:
    from db import buscar_usuario_id
    uid = st.session_state.get("usuario_id")
    if not uid:
        return None
    row = buscar_usuario_id(uid)
    if not row:
        return None
    return dict(row)


def fazer_logout():
    keys = ["usuario_id", "usuario_nome", "usuario_tipo", "empresa_id",
            "conversa_atual", "pergunta_sugerida"]
    for k in keys:
        st.session_state.pop(k, None)


# ── Recuperação de senha ───────────────────────────────────────────────────────

def solicitar_reset(email: str) -> tuple[bool, str]:
    """
    Inicia fluxo de recuperação. Gera token, salva no DB e envia e-mail.
    Sempre retorna mensagem genérica para não revelar se o e-mail existe.
    """
    import secrets as _sec
    from db import buscar_usuario_email, criar_token_reset
    from email_utils import enviar_email_reset

    MSG_GENERICA = ("Se este e-mail estiver cadastrado, você receberá as "
                    "instruções de recuperação em breve.")

    usuario = buscar_usuario_email(email.strip().lower())
    if not usuario:
        return True, MSG_GENERICA

    token = _sec.token_urlsafe(32)
    criar_token_reset(usuario["id"], token, expira_minutos=30)
    enviar_email_reset(usuario["email"], usuario["nome"], token)

    return True, MSG_GENERICA


def confirmar_reset(token: str, nova_senha: str) -> tuple[bool, str]:
    """Valida token e atualiza senha. Retorna (sucesso, mensagem)."""
    from db import buscar_token_reset, invalidar_token_reset, atualizar_senha

    row = buscar_token_reset(token)
    if not row:
        return False, "Link de recuperação inválido ou expirado. Solicite um novo."

    ok_senha, msg_senha = _senha_forte(nova_senha)
    if not ok_senha:
        return False, msg_senha

    atualizar_senha(row["usuario_id"], hash_senha(nova_senha))
    invalidar_token_reset(token)
    return True, "Senha alterada com sucesso! Faça login com sua nova senha."
