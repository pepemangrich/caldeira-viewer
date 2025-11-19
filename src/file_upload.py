# src/file_upload.py
# type: ignore

"""
Script para lidar com o carregamento dos dados a partir do arquivo de inspeção
"""

import pandas as pd
import streamlit as st


def handle_file_upload():
    """
    Lida com o arquivo carregado e trata seus dados
    """
    uploaded_file = st.file_uploader("Escolha um arquivo .xlsx", type=".xlsx")
    if uploaded_file:
        summary = pd.read_excel(uploaded_file, "Summary", header=None)
        date = pd.to_datetime(summary.iloc[3, 1]).date()
        company = summary.iloc[0, 1]
        site = summary.iloc[1, 1]
        sheets = pd.ExcelFile(uploaded_file).sheet_names
        sheets = [sheet for sheet in sheets if sheet != "Summary"]
        st.text_input("Empresa:", value=company, disabled=True)
        st.text_input("Refinaria:", value=site, disabled=True)
        st.text_input("Data:", value=date, disabled=True)

        return uploaded_file, company, site, date, sheets
    else:
        st.warning("Insira um arquivo para visualização")
        return None, None, None, None, None
