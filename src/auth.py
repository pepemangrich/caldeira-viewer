# src/auth.py
# type: ignore

"""
Script de autenticação de usuários com login e registro usando a biblioteca
Streamlit Authenticator e um arquivo YAML com os parâmetros necessários
"""

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from streamlit_authenticator.utilities import LoginError


def load_config(path="src/config.yaml"):
    """
    Carrega os parâmetros de autenticação a partir do arquivo YAML especificado
    """
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def save_config(config, path="src/config.yaml"):
    """
    Salva os parâmetros de autenticação no arquivo YAML especificado
    """
    with open(path, "w", encoding="utf-8") as file:
        return yaml.safe_dump(config, file, default_flow_style=False)


def authenticate_user(config):
    """
    Autentica o usuário a partir dos parâmetros do arquivo de configuração
    """
    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"]
    )

    try:
        authenticator.login(
            fields={
                "Form name": "Login",
                "Username": "Nome de usuário",
                "Password": "Senha",
                "Login": "Logar"
            },
            max_login_attempts=3
        )
    except LoginError as e:
        st.error(e)

    return authenticator
