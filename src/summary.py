# src/summary.py
# type: ignore

"""
Script para geração do sumário e dados gerais relacionados às paredes de tubos
da caldeira
"""

import numpy as np
import pandas as pd
import streamlit as st


def generate_summary(uploaded_file, sheets):
    """
    Gera o sumário com informações gerais sobre a inspeção
    """
    for sheet in sheets:
        summarize = pd.read_excel(uploaded_file, sheet)

        # Mantém o mesmo corte que você já usava
        summarize = summarize.iloc[3:].reset_index(drop=True)

        # 1ª coluna = elevação (m). Garantir que seja numérica.
        elev = pd.to_numeric(
            summarize.iloc[:, 0].astype(str).str.replace(",", ".", regex=False),
            errors="coerce",
        )

        # Remove linhas sem elevação válida
        summarize = summarize.loc[elev.notna()].copy()
        elev = elev.loc[elev.notna()].astype(float)

        if summarize.empty:
            # não tenta formatar nada
            continue

        # Define elevação como índice
        summarize.iloc[:, 0] = elev.values
        summarize.set_index(summarize.columns[0], inplace=True)

        # Converte leituras para numérico
        summarize = summarize.apply(pd.to_numeric, errors="coerce")

        # Range de elevação (robusto)
        summarize_min_elevation = float(np.nanmin(summarize.index.values))
        summarize_max_elevation = float(np.nanmax(summarize.index.values))

        # Estatísticas usando TODAS as colunas (tubos)
        avg_thickness_val = float(np.nanmean(summarize.values))
        min_thickness = summarize.min().nsmallest(3)

        tubes_range = f"{summarize.columns[0]} - {summarize.columns[-1]}"
        elevation_range = (
            f"{summarize_min_elevation:.3f} m - {summarize_max_elevation:.3f} m"
        ).replace(".", ",")
        avg_thickness = (f"{avg_thickness_val:.3f}".replace(".", ",") + " mm")

        data = []
        for tube_col in min_thickness.index:
            thickness_value = float(min_thickness[tube_col])

            matches = summarize.index[summarize[tube_col] == thickness_value]
            elev_value = float(matches[0]) if len(matches) else float("nan")

            data.append(
                {
                    "min_reading": f"{thickness_value:.3f} mm".replace(".", ","),
                    "tube": f"#{tube_col}",
                    "elevation": f"{elev_value:.3f} m".replace(".", ",")
                    if np.isfinite(elev_value)
                    else "-",
                }
            )

        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    color: #fff;
                    justify-content: center;
                    align-items: center;
                }}
                .container {{
                    width: 400px;
                    background-color: #1e1e1e;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.5);
                }}
                .container h1 {{
                    font-size: 24px;
                    margin-bottom: 10px;
                }}
                .data {{
                    font-size: 14px;
                    line-height: 1.6;
                }}
                .data strong {{
                    font-size: 16px;
                }}
                .table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                .table th, .table td {{
                    padding: 8px;
                    text-align: left;
                }}
                .table th {{
                    font-weight: normal;
                    color: #aaa;
                }}
                .table td {{
                    font-weight: bold;
                }}
                .table tr:nth-child(odd) {{
                    background-color: #2a2a2a;
                }}
                .table tr:nth-child(even) {{
                    background-color: #1e1e1e;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>{sheet}</h1>
                <div class="data">
                    Tubos: <strong>#{tubes_range}</strong><br>
                    Elevação: <strong>{elevation_range}</strong><br>
                    Espessura média: <strong>{avg_thickness}</strong>
                </div>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Espessuras mínimas</th>
                            <th>Tubos</th>
                            <th>Elevação</th>
                        </tr>
                    </thead>
                    <tbody>
        """

        for row in data:
            html_content += f"""
            <tr>
                <td>{row['min_reading']}</td>
                <td>{row['tube']}</td>
                <td>{row['elevation']}</td>
            </tr>
            """

        html_content += """
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """

        st.components.v1.html(html_content, height=350, width=500)