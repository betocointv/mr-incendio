"""
Banco de dados SQLite — usuários, empresas, créditos, transações, conversas, auditoria.
"""

from __future__ import annotations

import json
import os
import secrets as _secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

DB_PATH        = Path("dados/db.sqlite")
NORMAS_PATH    = Path("dados/atualizacao_normas.json")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def conexao() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    with conexao() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS empresas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nome        TEXT NOT NULL,
            cnpj        TEXT,
            criado_em   TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS usuarios (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            nome             TEXT NOT NULL,
            email            TEXT UNIQUE NOT NULL,
            senha_hash       TEXT NOT NULL,
            tipo             TEXT NOT NULL DEFAULT 'pessoal',
            empresa_id       INTEGER REFERENCES empresas(id),
            creditos         REAL NOT NULL DEFAULT 0,
            pontos           INTEGER NOT NULL DEFAULT 0,
            ativo            INTEGER NOT NULL DEFAULT 1,
            criado_em        TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS transacoes (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id    INTEGER NOT NULL REFERENCES usuarios(id),
            tipo          TEXT NOT NULL,
            creditos      REAL NOT NULL DEFAULT 0,
            tokens_input  INTEGER NOT NULL DEFAULT 0,
            tokens_output INTEGER NOT NULL DEFAULT 0,
            custo_usd     REAL NOT NULL DEFAULT 0,
            descricao     TEXT,
            criado_em     TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS conversas (
            id          TEXT PRIMARY KEY,
            usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
            titulo      TEXT NOT NULL DEFAULT 'Nova conversa',
            mensagens   TEXT NOT NULL DEFAULT '[]',
            criado_em   TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS pacotes (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            nome         TEXT UNIQUE NOT NULL,
            creditos     INTEGER NOT NULL,
            preco_brl    REAL NOT NULL,
            desconto_pct INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS audit_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id  INTEGER REFERENCES usuarios(id),
            acao        TEXT NOT NULL,
            detalhe     TEXT,
            ip          TEXT,
            criado_em   TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS reset_tokens (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
            token       TEXT UNIQUE NOT NULL,
            expira_em   TEXT NOT NULL,
            usado       INTEGER NOT NULL DEFAULT 0,
            criado_em   TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sessoes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
            token       TEXT UNIQUE NOT NULL,
            expira_em   TEXT NOT NULL,
            ativo       INTEGER NOT NULL DEFAULT 1,
            criado_em   TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS pagamentos_pendentes (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id       INTEGER NOT NULL REFERENCES usuarios(id),
            plano_id         INTEGER NOT NULL,
            processado       INTEGER NOT NULL DEFAULT 0,
            order_pagarme_id TEXT NOT NULL DEFAULT '',
            criado_em        TEXT NOT NULL
        );
        """)

        # Migrações: colunas adicionadas após criação inicial
        _migrar_colunas(conn, "usuarios", [
            ("telefone",         "TEXT NOT NULL DEFAULT ''"),
            ("cpf",              "TEXT NOT NULL DEFAULT ''"),
            ("tentativas_login", "INTEGER NOT NULL DEFAULT 0"),
            ("bloqueado_ate",    "TEXT NOT NULL DEFAULT ''"),
        ])
        _migrar_colunas(conn, "pagamentos_pendentes", [
            ("order_pagarme_id", "TEXT NOT NULL DEFAULT ''"),
        ])

        _seed(conn)


def _migrar_colunas(conn, tabela: str, colunas: list):
    """Adiciona colunas novas sem quebrar se já existirem."""
    for col, definition in colunas:
        try:
            conn.execute(f"ALTER TABLE {tabela} ADD COLUMN {col} {definition}")
        except Exception:
            pass  # coluna já existe


def _get_admin_password() -> str:
    """
    Lê senha do admin de:
      1. st.secrets["ADMIN_PASSWORD"]
      2. variável de ambiente ADMIN_PASSWORD
      3. Gera aleatoriamente e imprime aviso (somente na primeira execução)
    """
    # 1. Streamlit secrets
    try:
        import streamlit as st
        pwd = st.secrets.get("ADMIN_PASSWORD")
        if pwd:
            return pwd
    except Exception:
        pass

    # 2. Variável de ambiente
    pwd = os.environ.get("ADMIN_PASSWORD")
    if pwd:
        return pwd

    # 3. Gera senha aleatória e avisa no console
    pwd = _secrets.token_urlsafe(16)
    sep = "=" * 56
    print(f"\n{sep}")
    print("[AVISO SEGURANÇA] Nenhuma ADMIN_PASSWORD definida.")
    print(f"Senha admin gerada: {pwd}")
    print("Adicione em .streamlit/secrets.toml:")
    print(f'ADMIN_PASSWORD = "{pwd}"')
    print(f"{sep}\n")
    return pwd


def _seed(conn: sqlite3.Connection):
    """Insere/atualiza dados iniciais sem duplicatas."""
    # Remove duplicatas e IDs fora do range 1-4
    conn.execute("DELETE FROM pacotes WHERE id NOT IN (1,2,3,4)")
    conn.executemany(
        """INSERT INTO pacotes (id, nome, creditos, preco_brl, desconto_pct)
           VALUES (?,?,?,?,?)
           ON CONFLICT(id) DO UPDATE SET
               nome=excluded.nome,
               creditos=excluded.creditos,
               preco_brl=excluded.preco_brl,
               desconto_pct=excluded.desconto_pct""",
        [
            (1, "Básico",        50,   29.90,  0),
            (2, "Profissional",  200,  69.90,  0),
            (3, "Premium",       500, 149.90, 30),
            (4, "Empresarial",  1000, 199.90, 40),
        ]
    )

    if not conn.execute("SELECT 1 FROM usuarios WHERE tipo='admin'").fetchone():
        from auth import hash_senha
        senha = _get_admin_password()
        conn.execute(
            """INSERT INTO usuarios (nome, email, senha_hash, tipo, creditos, pontos, criado_em)
               VALUES (?,?,?,?,?,?,?)""",
            ("Admin", "admin@cbmerj.app", hash_senha(senha),
             "admin", 9999, 0, datetime.now().isoformat())
        )


# ── Usuários ───────────────────────────────────────────────────────────────────

def criar_usuario(nome: str, email: str, senha_hash: str, tipo: str,
                  empresa_id: Optional[int] = None,
                  creditos_boas_vindas: float = 10,
                  telefone: str = "", cpf: str = "") -> int:
    with conexao() as conn:
        cur = conn.execute(
            """INSERT INTO usuarios
               (nome, email, senha_hash, tipo, empresa_id, creditos, pontos,
                telefone, cpf, criado_em)
               VALUES (?,?,?,?,?,?,0,?,?,?)""",
            (nome, email, senha_hash, tipo, empresa_id,
             creditos_boas_vindas, telefone, cpf, datetime.now().isoformat())
        )
        uid = cur.lastrowid
        if creditos_boas_vindas > 0:
            conn.execute(
                """INSERT INTO transacoes (usuario_id, tipo, creditos, descricao, criado_em)
                   VALUES (?,?,?,?,?)""",
                (uid, "bonus_boas_vindas", creditos_boas_vindas,
                 "Créditos de boas-vindas 🎁", datetime.now().isoformat())
            )
        return uid


def buscar_usuario_email(email: str) -> Optional[sqlite3.Row]:
    with conexao() as conn:
        return conn.execute(
            "SELECT * FROM usuarios WHERE email=? AND ativo=1", (email,)
        ).fetchone()


def buscar_usuario_id(uid: int) -> Optional[sqlite3.Row]:
    """Retorna usuário ATIVO pelo ID. Retorna None se inativo ou inexistente."""
    with conexao() as conn:
        return conn.execute(
            "SELECT * FROM usuarios WHERE id=? AND ativo=1", (uid,)
        ).fetchone()


def listar_usuarios(empresa_id: Optional[int] = None) -> list:
    with conexao() as conn:
        if empresa_id:
            return conn.execute(
                "SELECT * FROM usuarios WHERE empresa_id=? AND ativo=1 ORDER BY nome",
                (empresa_id,)
            ).fetchall()
        return conn.execute(
            "SELECT * FROM usuarios WHERE ativo=1 ORDER BY nome"
        ).fetchall()


def atualizar_creditos(uid: int, delta: float):
    with conexao() as conn:
        conn.execute("UPDATE usuarios SET creditos = creditos + ? WHERE id=?", (delta, uid))


def atualizar_pontos(uid: int, delta: int):
    with conexao() as conn:
        conn.execute("UPDATE usuarios SET pontos = pontos + ? WHERE id=?", (delta, uid))


def desativar_usuario(uid: int):
    with conexao() as conn:
        conn.execute("UPDATE usuarios SET ativo=0 WHERE id=?", (uid,))


def atualizar_tipo_usuario(uid: int, novo_tipo: str):
    with conexao() as conn:
        conn.execute("UPDATE usuarios SET tipo=? WHERE id=?", (novo_tipo, uid))


def vincular_usuario_empresa(uid: int, empresa_id: int):
    with conexao() as conn:
        conn.execute(
            "UPDATE usuarios SET empresa_id=?, tipo='funcionario' WHERE id=?",
            (empresa_id, uid)
        )


# ── Rate limiting (login) ──────────────────────────────────────────────────────

def registrar_tentativa_login(uid: int) -> int:
    """Incrementa contador de tentativas e retorna o novo total."""
    with conexao() as conn:
        conn.execute(
            "UPDATE usuarios SET tentativas_login = tentativas_login + 1 WHERE id=?",
            (uid,)
        )
        row = conn.execute(
            "SELECT tentativas_login FROM usuarios WHERE id=?", (uid,)
        ).fetchone()
        return row["tentativas_login"] if row else 0


def resetar_tentativas_login(uid: int):
    """Reseta contador e remove bloqueio após login bem-sucedido."""
    with conexao() as conn:
        conn.execute(
            "UPDATE usuarios SET tentativas_login=0, bloqueado_ate='' WHERE id=?",
            (uid,)
        )


def bloquear_usuario_login(uid: int, minutos: int):
    """Bloqueia conta por N minutos."""
    ate = (datetime.now() + timedelta(minutes=minutos)).isoformat()
    with conexao() as conn:
        conn.execute(
            "UPDATE usuarios SET bloqueado_ate=? WHERE id=?",
            (ate, uid)
        )


# ── Auditoria ──────────────────────────────────────────────────────────────────

def registrar_auditoria(usuario_id: int, acao: str, detalhe: str = "", ip: str = ""):
    """Registra ação administrativa no log de auditoria."""
    with conexao() as conn:
        conn.execute(
            "INSERT INTO audit_log (usuario_id, acao, detalhe, ip, criado_em) VALUES (?,?,?,?,?)",
            (usuario_id, acao, detalhe, ip, datetime.now().isoformat())
        )


def listar_audit_log(limite: int = 50) -> list:
    with conexao() as conn:
        return conn.execute(
            """SELECT a.criado_em, u.nome, u.email, a.acao, a.detalhe
               FROM audit_log a
               LEFT JOIN usuarios u ON u.id = a.usuario_id
               ORDER BY a.criado_em DESC LIMIT ?""",
            (limite,)
        ).fetchall()


# ── Empresas ───────────────────────────────────────────────────────────────────

def criar_empresa(nome: str, cnpj: str = "") -> int:
    with conexao() as conn:
        cur = conn.execute(
            "INSERT INTO empresas (nome, cnpj, criado_em) VALUES (?,?,?)",
            (nome, cnpj, datetime.now().isoformat())
        )
        return cur.lastrowid


def buscar_empresa(eid: int) -> Optional[sqlite3.Row]:
    with conexao() as conn:
        return conn.execute("SELECT * FROM empresas WHERE id=?", (eid,)).fetchone()


# ── Transações ─────────────────────────────────────────────────────────────────

def registrar_transacao(usuario_id: int, tipo: str, creditos: float,
                        tokens_input: int = 0, tokens_output: int = 0,
                        custo_usd: float = 0.0, descricao: str = ""):
    with conexao() as conn:
        conn.execute(
            """INSERT INTO transacoes
               (usuario_id, tipo, creditos, tokens_input, tokens_output,
                custo_usd, descricao, criado_em)
               VALUES (?,?,?,?,?,?,?,?)""",
            (usuario_id, tipo, creditos, tokens_input, tokens_output,
             custo_usd, descricao, datetime.now().isoformat())
        )


def listar_transacoes(usuario_id: int, limite: int = 30) -> list:
    with conexao() as conn:
        return conn.execute(
            """SELECT * FROM transacoes WHERE usuario_id=?
               ORDER BY criado_em DESC LIMIT ?""",
            (usuario_id, limite)
        ).fetchall()


def consumo_por_usuario(empresa_id: int) -> list:
    with conexao() as conn:
        return conn.execute(
            """SELECT u.nome, u.email,
                      COUNT(t.id)          AS perguntas,
                      SUM(ABS(t.creditos)) AS creditos_usados
               FROM usuarios u
               LEFT JOIN transacoes t ON t.usuario_id = u.id AND t.tipo = 'uso'
               WHERE u.empresa_id = ? AND u.ativo = 1
               GROUP BY u.id ORDER BY creditos_usados DESC""",
            (empresa_id,)
        ).fetchall()


def stats_plataforma() -> dict:
    with conexao() as conn:
        total_usuarios = conn.execute(
            "SELECT COUNT(*) FROM usuarios WHERE ativo=1 AND tipo != 'admin'"
        ).fetchone()[0]
        total_perguntas = conn.execute(
            "SELECT COUNT(*) FROM transacoes WHERE tipo='uso'"
        ).fetchone()[0]
        total_creditos = conn.execute(
            "SELECT COALESCE(SUM(creditos),0) FROM transacoes WHERE tipo='compra'"
        ).fetchone()[0]
        return {
            "usuarios": total_usuarios,
            "perguntas": total_perguntas,
            "creditos_vendidos": total_creditos,
        }


def ranking_pontos(limite: int = 10) -> list:
    with conexao() as conn:
        return conn.execute(
            """SELECT nome, pontos FROM usuarios
               WHERE ativo=1 AND tipo != 'admin'
               ORDER BY pontos DESC LIMIT ?""",
            (limite,)
        ).fetchall()


# ── Conversas ──────────────────────────────────────────────────────────────────

def listar_conversas_db(usuario_id: int) -> list:
    with conexao() as conn:
        rows = conn.execute(
            "SELECT * FROM conversas WHERE usuario_id=? ORDER BY criado_em DESC LIMIT 5",
            (usuario_id,)
        ).fetchall()
    result = []
    for r in rows:
        d = dict(r)
        d["mensagens"] = json.loads(d["mensagens"])
        result.append(d)
    return result


def salvar_conversa_db(conversa: dict, usuario_id: int):
    with conexao() as conn:
        conn.execute(
            """INSERT INTO conversas (id, usuario_id, titulo, mensagens, criado_em)
               VALUES (?,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET
                   titulo=excluded.titulo,
                   mensagens=excluded.mensagens""",
            (conversa["id"], usuario_id, conversa["titulo"],
             json.dumps(conversa["mensagens"], ensure_ascii=False),
             conversa.get("criado_em", datetime.now().isoformat()))
        )


def excluir_conversa_db(conv_id: str, usuario_id: int):
    with conexao() as conn:
        conn.execute(
            "DELETE FROM conversas WHERE id=? AND usuario_id=?", (conv_id, usuario_id)
        )


def contar_conversas(usuario_id: int) -> int:
    with conexao() as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM conversas WHERE usuario_id=?", (usuario_id,)
        ).fetchone()[0]


# ── Pacotes ────────────────────────────────────────────────────────────────────

def listar_pacotes() -> list:
    with conexao() as conn:
        return conn.execute("SELECT * FROM pacotes ORDER BY creditos").fetchall()


# ── Recuperação de senha ────────────────────────────────────────────────────────

def criar_token_reset(usuario_id: int, token: str, expira_minutos: int = 30):
    """Invalida tokens anteriores do usuário e cria um novo."""
    expira = (datetime.now() + timedelta(minutes=expira_minutos)).isoformat()
    with conexao() as conn:
        conn.execute(
            "UPDATE reset_tokens SET usado=1 WHERE usuario_id=? AND usado=0",
            (usuario_id,)
        )
        conn.execute(
            "INSERT INTO reset_tokens (usuario_id, token, expira_em, criado_em) VALUES (?,?,?,?)",
            (usuario_id, token, expira, datetime.now().isoformat())
        )


def buscar_token_reset(token: str) -> Optional[sqlite3.Row]:
    """Retorna token não-usado e não-expirado."""
    with conexao() as conn:
        return conn.execute(
            """SELECT * FROM reset_tokens
               WHERE token=? AND usado=0 AND expira_em > ?""",
            (token, datetime.now().isoformat())
        ).fetchone()


def invalidar_token_reset(token: str):
    with conexao() as conn:
        conn.execute("UPDATE reset_tokens SET usado=1 WHERE token=?", (token,))


def atualizar_senha(usuario_id: int, nova_hash: str):
    with conexao() as conn:
        conn.execute(
            "UPDATE usuarios SET senha_hash=?, tentativas_login=0, bloqueado_ate='' WHERE id=?",
            (nova_hash, usuario_id)
        )


# ── Datas de atualização das normas ──────────────────────────────────────────

_NORMAS_DEFAULT = {"normas_tecnicas": None, "coscip": None}


def get_datas_normas() -> dict:
    """Retorna as datas de última atualização das NTs e COSCIP."""
    if not NORMAS_PATH.exists():
        return _NORMAS_DEFAULT.copy()
    try:
        return json.loads(NORMAS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return _NORMAS_DEFAULT.copy()


def criar_sessao_token(usuario_id: int, dias: int = 30) -> str:
    """Cria token de sessão persistente. Retorna o token."""
    import secrets as _sec
    token = _sec.token_urlsafe(32)
    expira = (datetime.now() + timedelta(days=dias)).isoformat()
    with conexao() as conn:
        conn.execute(
            "INSERT INTO sessoes (usuario_id, token, expira_em, criado_em) VALUES (?,?,?,?)",
            (usuario_id, token, expira, datetime.now().isoformat())
        )
    return token


def validar_sessao_token(token: str) -> Optional[dict]:
    """Retorna dados do usuário se token válido, None caso contrário."""
    with conexao() as conn:
        row = conn.execute(
            """SELECT u.* FROM sessoes s
               JOIN usuarios u ON u.id = s.usuario_id
               WHERE s.token=? AND s.ativo=1 AND s.expira_em > ?""",
            (token, datetime.now().isoformat())
        ).fetchone()
    return dict(row) if row else None


def invalidar_sessao_token(token: str):
    with conexao() as conn:
        conn.execute("UPDATE sessoes SET ativo=0 WHERE token=?", (token,))


def set_data_norma(chave: str, data: str):
    """Atualiza a data de uma norma. chave: 'normas_tecnicas' ou 'coscip'."""
    dados = get_datas_normas()
    dados[chave] = data
    NORMAS_PATH.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


# ── Pagamentos pendentes (links Pagar.me) ──────────────────────────────────────

def criar_pagamento_pendente(usuario_id: int, plano_id: int):
    with conexao() as conn:
        conn.execute(
            "INSERT INTO pagamentos_pendentes (usuario_id, plano_id, criado_em) VALUES (?,?,?)",
            (usuario_id, plano_id, datetime.now().isoformat())
        )


def buscar_pagamentos_pendentes(usuario_id: int) -> list:
    """Retorna pagamentos pendentes não processados das últimas 24h."""
    limite = (datetime.now() - timedelta(hours=24)).isoformat()
    with conexao() as conn:
        rows = conn.execute(
            """SELECT pp.id, pp.plano_id, p.nome, p.creditos, p.preco_brl
               FROM pagamentos_pendentes pp
               JOIN pacotes p ON p.id = pp.plano_id
               WHERE pp.usuario_id=? AND pp.processado=0 AND pp.criado_em > ?
               ORDER BY pp.criado_em DESC""",
            (usuario_id, limite)
        ).fetchall()
    return [dict(r) for r in rows]


def marcar_pagamento_processado(pagamento_id: int, order_id: str = ""):
    with conexao() as conn:
        conn.execute(
            "UPDATE pagamentos_pendentes SET processado=1, order_pagarme_id=? WHERE id=?",
            (order_id, pagamento_id)
        )


def order_ja_processada(order_id: str) -> bool:
    """Verifica se um order_id do Pagar.me já foi usado para adicionar créditos."""
    if not order_id:
        return False
    with conexao() as conn:
        row = conn.execute(
            "SELECT id FROM pagamentos_pendentes WHERE order_pagarme_id=? AND processado=1",
            (order_id,)
        ).fetchone()
    return row is not None
