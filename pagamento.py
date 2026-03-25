"""
Integração Pagar.me V5 — PIX e Cartão para o Mr. Incêndio.
"""
from __future__ import annotations

import base64
import os
import re

import requests
import streamlit as st

PAGARME_BASE = "https://api.pagar.me/core/v5"


def _secret_key() -> str:
    return st.secrets.get("PAGARME_SECRET_KEY",
                          os.environ.get("PAGARME_SECRET_KEY", ""))


def _headers() -> dict:
    sk = _secret_key()
    cred = base64.b64encode(f"{sk}:".encode()).decode()
    return {"Authorization": f"Basic {cred}",
            "Content-Type": "application/json"}


# ── PIX direto (QR code no app) ───────────────────────────────────────────────

def criar_pix(nome: str, email: str, cpf: str,
              valor_centavos: int, descricao: str,
              metadata: dict | None = None) -> dict:
    """Cria ordem PIX no Pagar.me V5. Retorna o dict da ordem."""
    cpf_limpo = "".join(c for c in cpf if c.isdigit())
    payload = {
        "items": [{
            "amount": valor_centavos,
            "description": descricao,
            "quantity": 1,
            "code": "creditos_mr_incendio",
        }],
        "customer": {
            "name": nome,
            "email": email,
            "type": "individual",
            "document": cpf_limpo,
            "document_type": "cpf",
        },
        "payments": [{
            "payment_method": "pix",
            "pix": {"expires_in": 3600},
        }],
        "metadata": {"site": "mr_incendio", **(metadata or {})},
    }
    r = requests.post(f"{PAGARME_BASE}/orders",
                      json=payload, headers=_headers(), timeout=15)
    r.raise_for_status()
    return r.json()


def extrair_pix(ordem: dict) -> tuple[str, str]:
    """Retorna (qr_code_string, qr_code_url)."""
    try:
        tx = ordem["charges"][0]["last_transaction"]
        return tx.get("qr_code", ""), tx.get("qr_code_url", "")
    except (KeyError, IndexError):
        return "", ""


# ── Cartão — tokenização + ordem ─────────────────────────────────────────────

def _public_key() -> str:
    return st.secrets.get("PAGARME_PUBLIC_KEY",
                          os.environ.get("PAGARME_PUBLIC_KEY", ""))


def tokenizar_cartao(numero: str, titular: str,
                     mes: int, ano: int, cvv: str) -> str:
    """Tokeniza cartão via Pagar.me V5. Retorna o card_token."""
    pub = _public_key()
    payload = {
        "type": "card",
        "card": {
            "number": re.sub(r"\D", "", numero),
            "holder_name": titular.upper(),
            "exp_month": mes,
            "exp_year": ano,
            "cvv": cvv,
        },
    }
    r = requests.post(f"{PAGARME_BASE}/tokens?appId={pub}",
                      json=payload, timeout=10)
    r.raise_for_status()
    return r.json()["id"]


def criar_cartao(nome: str, email: str, cpf: str,
                 card_token: str, valor_centavos: int,
                 descricao: str, metadata: dict | None = None) -> dict:
    """Cria ordem de cartão no Pagar.me V5."""
    cpf_limpo = re.sub(r"\D", "", cpf)
    payload = {
        "items": [{
            "amount": valor_centavos,
            "description": descricao,
            "quantity": 1,
            "code": "creditos_mr_incendio",
        }],
        "customer": {
            "name": nome,
            "email": email,
            "type": "individual",
            "document": cpf_limpo,
            "document_type": "cpf",
        },
        "payments": [{
            "payment_method": "credit_card",
            "credit_card": {
                "card_token": card_token,
                "installments": 1,
                "statement_descriptor": "MR INCENDIO",
            },
        }],
        "metadata": {"site": "mr_incendio", **(metadata or {})},
    }
    r = requests.post(f"{PAGARME_BASE}/orders",
                      json=payload, headers=_headers(), timeout=15)
    r.raise_for_status()
    return r.json()


# ── Consultas ─────────────────────────────────────────────────────────────────

def consultar_ordem(order_id: str) -> dict:
    r = requests.get(f"{PAGARME_BASE}/orders/{order_id}",
                     headers=_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def ordem_paga(order_id: str) -> bool:
    try:
        return consultar_ordem(order_id).get("status") == "paid"
    except Exception:
        return False


def buscar_ordem_paga_por_valor(valor_centavos: int, minutos: int = 60) -> str | None:
    """
    Busca nas últimas N ordens pagas uma com o valor exato.
    Retorna o order_id encontrado ou None.
    """
    from datetime import datetime, timedelta, timezone
    try:
        r = requests.get(f"{PAGARME_BASE}/orders",
                         params={"size": 20, "status": "paid"},
                         headers=_headers(), timeout=10)
        r.raise_for_status()
        data = r.json()
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutos)
        for order in data.get("data", []):
            criado_str = order.get("created_at", "")
            try:
                criado = datetime.fromisoformat(criado_str.replace("Z", "+00:00"))
            except Exception:
                continue
            if criado < cutoff:
                continue
            # Soma os charges para verificar o valor total
            total = sum(
                ch.get("amount", 0)
                for ch in order.get("charges", [])
            )
            if total == valor_centavos:
                return order["id"]
    except Exception:
        pass
    return None
