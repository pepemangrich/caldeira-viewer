# src/app.py
# type: ignore

"""
Script principal da aplicação
"""

from pathlib import Path

import streamlit as st

from auth import authenticate_user, load_config, save_config
from email_smtp import email_reset_password
from file_upload import handle_file_upload
from summary import generate_summary
from visualization import create_heatmap

# Configurações iniciais da página
st.set_page_config(
    layout="centered",
    page_title="Integral IMI - Software Caldeira",
    page_icon="imgs/simbolo-integral.png",
)

# ====== LOGO (Logo.png na raiz do projeto) ======
LOGO_PATH = Path(__file__).resolve().parent.parent / "Logo.png"

if LOGO_PATH.exists():
    # Topo centralizado
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.image(str(LOGO_PATH), use_container_width=True)

    # Sidebar
    st.sidebar.image(str(LOGO_PATH), use_container_width=True)
# ===============================================

# Para debugar, tirar na versão final
if st.button("[DEBUG] Rerun"):
    st.rerun()

# Autenticação do usuário
config = load_config()
authenticator = authenticate_user(config)

auth_status = st.session_state.get("authentication_status")

if auth_status is True:
    username = st.session_state.get("username", "")
    name = st.session_state.get("name", "")

    email = ""
    try:
        email = config["credentials"]["usernames"][username].get("email", "")
    except Exception:
        email = ""

    st.write(f"Bem-vindo **{name}** - {email}")
    authenticator.logout()

    with st.sidebar:
        uploaded_file, company, site, date, sheets = handle_file_upload()

    if uploaded_file:
        _ = create_heatmap(uploaded_file, sheets)

        with st.expander("Sumário"):
            generate_summary(uploaded_file, sheets)

elif auth_status is False:
    st.error("Usuário ou senha incorretos")

    # Registro
    try:
        (
            email_of_registered_user,
            username_of_registered_user,
            name_of_registered_user,
        ) = authenticator.register_user(
            pre_authorized=config.get("pre-authorized", {}).get("emails", []),
            fields={
                "First name": "Nome",
                "Last name": "Sobrenome",
                "Password hint": "Dica da senha",
                "Form name": "Registrar",
                "Name": "Nome",
                "Email": "Email",
                "Username": "Nome de usuário",
                "Password": "Senha",
                "Repeat password": "Repetir senha",
                "Register": "Registrar",
            },
            domains=["integral-imi.com.br"],
        )
        if email_of_registered_user:
            st.success("Usuário registrado com sucesso")
    except Exception as e:
        st.error(e)

    # Esqueci a senha
    try:
        (
            username_of_forgotten_password,
            email_of_forgotten_password,
            new_random_password,
        ) = authenticator.forgot_password(
            fields={
                "Form name": "Esqueci a senha",
                "Username": "Nome de usuário",
                "Submit": "Enviar",
            }
        )

        if username_of_forgotten_password:
            email_parts = email_of_forgotten_password.split("@")
            email_censored = (
                email_parts[0][0]
                + "*" * max(0, len(email_parts[0]) - 2)
                + email_parts[0][-1]
                + "@"
                + email_parts[1]
            )
            st.success(f"Senha nova enviada para o e-mail {email_censored}")
            email_reset_password(new_random_password)
        elif username_of_forgotten_password is False:
            st.error("Usuário não encontrado")
    except Exception as e:
        st.error(e)

elif auth_status is None:
    # Registro
    try:
        (
            email_of_registered_user,
            username_of_registered_user,
            name_of_registered_user,
        ) = authenticator.register_user(
            pre_authorized=config.get("pre-authorized", {}).get("emails", []),
            fields={
                "First name": "Nome",
                "Last name": "Sobrenome",
                "Password hint": "Dica da senha",
                "Form name": "Registrar",
                "Name": "Nome",
                "Email": "Email",
                "Username": "Nome de usuário",
                "Password": "Senha",
                "Repeat password": "Repetir senha",
                "Register": "Registrar",
            },
            domains=["integral-imi.com.br"],
        )
        if email_of_registered_user:
            st.success("Usuário registrado com sucesso")
    except Exception as e:
        st.error(e)

    # Esqueci a senha (com captcha)
    try:
        (
            username_of_forgotten_password,
            email_of_forgotten_password,
            new_random_password,
        ) = authenticator.forgot_password(
            fields={
                "Form name": "Esqueci a senha",
                "Username": "Nome de usuário",
                "Submit": "Enviar",
            },
            captcha=True,
        )

        if username_of_forgotten_password:
            email_parts = email_of_forgotten_password.split("@")
            email_censored = (
                email_parts[0][0]
                + "*" * max(0, len(email_parts[0]) - 2)
                + email_parts[0][-1]
                + "@"
                + email_parts[1]
            )
            st.success(f"Senha nova enviada para o e-mail {email_censored}")
            email_reset_password(new_random_password)
        elif username_of_forgotten_password is False:
            st.error("Usuário não encontrado")
    except Exception as e:
        st.error(e)

# Atualiza os parâmetros de autenticação no arquivo config.yaml
save_config(config)  # deve ser a última função chamada da aplicação