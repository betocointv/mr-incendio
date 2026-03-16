"""
Envio de e-mails transacionais via SMTP.
Configure em .streamlit/secrets.toml:
  SMTP_HOST = "smtp.gmail.com"
  SMTP_PORT = 587
  SMTP_USER = "seuemail@gmail.com"
  SMTP_PASS = "sua_senha_de_app"
  APP_URL   = "https://seu-app.streamlit.app"
"""

from __future__ import annotations

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional


def _smtp_cfg() -> dict:
    try:
        import streamlit as st
        return {
            "host": st.secrets.get("SMTP_HOST", ""),
            "port": int(st.secrets.get("SMTP_PORT", 587)),
            "user": st.secrets.get("SMTP_USER", ""),
            "pwd":  st.secrets.get("SMTP_PASS", ""),
            "from": st.secrets.get("SMTP_FROM", st.secrets.get("SMTP_USER", "")),
        }
    except Exception:
        return {}


def _app_url() -> str:
    try:
        import streamlit as st
        return st.secrets.get("APP_URL", "").rstrip("/")
    except Exception:
        return ""


def enviar_email_reset(destinatario: str, nome: str, token: str) -> tuple[bool, str]:
    """Envia e-mail de recuperação de senha. Retorna (ok, mensagem_erro)."""
    cfg = _smtp_cfg()
    if not cfg.get("host") or not cfg.get("user"):
        return False, "SMTP não configurado no sistema."

    app_url = _app_url()
    link = f"{app_url}/Acesso?token={token}" if app_url else f"token={token}"

    html = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#08080e;font-family:Inter,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#08080e;padding:40px 20px;">
  <tr><td align="center">
    <table width="560" cellpadding="0" cellspacing="0"
           style="background:#141428;border-radius:16px;border:1px solid rgba(255,255,255,0.08);padding:40px;">
      <tr><td align="center" style="padding-bottom:24px;">
        <div style="width:50px;height:50px;border-radius:14px;
                    background:linear-gradient(135deg,#7a2340,#561629);
                    display:inline-flex;align-items:center;justify-content:center;
                    font-size:1.5rem;line-height:50px;text-align:center;">🔥</div>
        <h2 style="color:#fff;margin:8px 0 0;font-size:1.3rem;letter-spacing:-.02em;">Mr. Incêndio</h2>
      </td></tr>
      <tr><td style="color:#f0f0f8;font-size:.95rem;line-height:1.6;padding-bottom:16px;">
        <p>Olá, <strong>{nome}</strong>!</p>
        <p>Recebemos uma solicitação para redefinir a senha da sua conta.</p>
        <p>Clique no botão abaixo para criar uma nova senha.
           O link é válido por <strong>30 minutos</strong>.</p>
      </td></tr>
      <tr><td align="center" style="padding:16px 0 24px;">
        <a href="{link}"
           style="background:linear-gradient(135deg,#7a2340,#561629);color:#fff;
                  text-decoration:none;padding:14px 32px;border-radius:10px;
                  font-weight:700;font-size:1rem;display:inline-block;">
          Redefinir minha senha
        </a>
      </td></tr>
      <tr><td style="color:#9090b8;font-size:.82rem;line-height:1.5;">
        <p>Se você não solicitou a recuperação de senha, ignore este e-mail.
           Sua senha permanece a mesma.</p>
        <hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:16px 0;">
        <p style="color:#60607a;text-align:center;font-size:.78rem;">
          🔥 Mr. Incêndio · Consulta inteligente às normas do CBMERJ
        </p>
      </td></tr>
    </table>
  </td></tr>
</table>
</body>
</html>
"""

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🔥 Mr. Incêndio — Recuperação de senha"
        msg["From"]    = cfg["from"] or cfg["user"]
        msg["To"]      = destinatario
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP(cfg["host"], cfg["port"], timeout=15) as srv:
            srv.starttls()
            srv.login(cfg["user"], cfg["pwd"])
            srv.sendmail(msg["From"], [destinatario], msg.as_string())

        return True, ""
    except Exception as e:
        return False, str(e)
