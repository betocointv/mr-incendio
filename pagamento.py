"""
Integração Pagar.me V5 — PIX e Cartão para o Mr. Incêndio.
"""
from __future__ import annotations

import base64
import os

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


# ── Checkout hospedado (PIX + Cartão — página do Pagar.me) ───────────────────

def criar_checkout(nome: str, email: str, cpf: str,
                   valor_centavos: int, descricao: str,
                   success_url: str,
                   metadata: dict | None = None) -> dict:
    """Cria payment link hospedado com PIX e cartão. Retorna dict com url."""
    cpf_limpo = "".join(c for c in cpf if c.isdigit())
    payload = {
        "name": descricao,
        "items": [{
            "amount": valor_centavos,
            "description": descricao,
            "quantity": 1,
            "code": "creditos_mr_incendio",
        }],
        "payment_settings": {
            "accepted_payment_methods": ["pix", "credit_card"],
            "credit_card_settings": {
                "installments": [{"number": 1, "total": valor_centavos}]
            },
        },
        "customer_settings": {
            "customer": {
                "name": nome,
                "email": email,
                "type": "individual",
                "document": cpf_limpo,
                "document_type": "CPF",
            }
        },
        "success_url": success_url,
        "metadata": {"site": "mr_incendio", **(metadata or {})},
    }
    r = requests.post(f"{PAGARME_BASE}/payment_links",
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


def consultar_checkout(checkout_id: str) -> dict:
    r = requests.get(f"{PAGARME_BASE}/payment_links/{checkout_id}",
                     headers=_headers(), timeout=10)
    r.raise_for_status()
    return r.json()


def checkout_pago(checkout_id: str) -> bool:
    try:
        data = consultar_checkout(checkout_id)
        return data.get("status") in ("paid", "overpaid")
    except Exception:
        return False
