# -*- coding: utf-8 -*-
"""
Gera o hash bcrypt da senha do admin para guardar no secrets.toml.

Uso (rode LOCALMENTE, no terminal):
    python gerar_hash_admin.py

Ele pede a senha (digitação oculta) e imprime SOMENTE o hash.
Copie o hash e cole no .streamlit/secrets.toml:

    ADMIN_PASSWORD_HASH = "<cole o hash aqui>"

A senha em texto puro nunca é salva nem exibida.
"""
import getpass

import bcrypt


def main() -> None:
    senha = getpass.getpass("Senha do admin: ")
    if len(senha) < 8:
        print("ERRO: use pelo menos 8 caracteres.")
        return
    conf = getpass.getpass("Confirme a senha: ")
    if senha != conf:
        print("ERRO: as senhas nao conferem.")
        return

    h = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

    print("\nHash gerado. Cole a linha abaixo no .streamlit/secrets.toml:\n")
    print(f'ADMIN_PASSWORD_HASH = "{h}"')
    print("\nDepois remova a linha antiga ADMIN_PASSWORD (texto puro).")


if __name__ == "__main__":
    main()
