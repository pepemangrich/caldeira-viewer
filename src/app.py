# src/app.py
# type: ignore

"""
Script principal da aplicação
"""

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
    page_icon="imgs/simbolo-integral.png"
)

# Configurações da logo da Integral na barra lateral esquerda
# st.logo(
#     image="imgs/logotipo-integral.png",
#     icon_image="imgs/simbolo-integral.png",
#     size="large",
#     link="https://integral-imi.com"
# )

# Esconde a barra decorativa superior
# hide_decoration_bar_style = """
#     <style>
#         header {visibility: hidden;}
#     </style>
# """
# st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

# Para debugar, tirar na versão final
if st.button("[DEBUG] Rerun"):
    st.rerun()

# Autenticação do usuário
config = load_config()
authenticator = authenticate_user(config)

if st.session_state["authentication_status"]:
    st.write(
        f"Bem-vindo **{st.session_state["name"]}** - {
            config["credentials"]["usernames"]
            [st.session_state["username"]]["email"]}"
    )
    authenticator.logout()

    with st.sidebar:
        uploaded_file, company, site, date, sheets = handle_file_upload()

    if uploaded_file:
        dataframe = create_heatmap(uploaded_file, sheets)

        with st.expander("Sumário"):
            generate_summary(uploaded_file, sheets)


elif st.session_state["authentication_status"] is False:
    st.error("Usuário ou senha incorretos")
    try:
        (email_of_registered_user,
         username_of_registered_user,
         name_of_registered_user) = authenticator.register_user(
            pre_authorized=config["pre-authorized"]["emails"],
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
            domains=["integral-imi.com.br"]
        )
        if email_of_registered_user:
            st.success("Usuário registrado com sucesso")
    except Exception as e:
        st.error(e)

    try:
        username_of_forgotten_password, \
            email_of_forgotten_password, \
            new_random_password = authenticator.forgot_password(
                fields={
                    "Form name": "Esqueci a senha",
                    "Username": "Nome de usuário",
                    "Submit": "Enviar"
                }
            )
        if username_of_forgotten_password:
            email_censored = email_of_forgotten_password.split("@")
            email_censored = email_censored[0][0] + "*" * \
                (len(email_censored[0]) - 2) + \
                email_censored[0][-1] + "@" + email_censored[1]
            st.success(
                f"Senha nova enviada para o e-mail {email_censored}")
            email_reset_password(new_random_password)
        elif username_of_forgotten_password is False:
            st.error("Usuário não encontrado")
    except Exception as e:
        st.error(e)

elif st.session_state["authentication_status"] is None:
    try:
        (email_of_registered_user,
         username_of_registered_user,
         name_of_registered_user) = authenticator.register_user(
             pre_authorized=config["pre-authorized"]["emails"],
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
             domains=["integral-imi.com.br"]
        )
        if email_of_registered_user:
            st.success("Usuário registrado com sucesso")
    except Exception as e:
        st.error(e)

    try:
        username_of_forgotten_password, \
            email_of_forgotten_password, \
            new_random_password = authenticator.forgot_password(
                fields={
                    "Form name": "Esqueci a senha",
                    "Username": "Nome de usuário",
                    "Submit": "Enviar"
                },
                captcha=True
            )
        if username_of_forgotten_password:
            email_censored = email_of_forgotten_password.split("@")
            email_censored = email_censored[0][0] + "*" * \
                (len(email_censored[0]) - 2) + \
                email_censored[0][-1] + "@" + email_censored[1]
            st.success(
                f"Senha nova enviada para o e-mail {email_censored}")
            email_reset_password(new_random_password)
        elif username_of_forgotten_password is False:
            st.error("Usuário não encontrado")
    except Exception as e:
        st.error(e)


# Atualiza os parâmetros de autenticação no arquivo config.yaml
save_config(config)  # deve ser a última função chamada da aplicação
