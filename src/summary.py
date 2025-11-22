# src/summary.py
# type: ignore

"""
Script para geração do sumário e dados gerais relacionados às paredes de tubos
da caldeira
"""

import pandas as pd
import streamlit as st


def generate_summary(uploaded_file, sheets):
    """
    Gera o sumário com informações gerais sobre a inspeção
    """
    for sheet in sheets:
        summarize = pd.read_excel(uploaded_file, sheet)
        summarize = summarize.iloc[3:].reset_index(drop=True)
        summarize.set_index(summarize.columns[0], inplace=True)
        summarize = summarize.apply(pd.to_numeric, errors='coerce')

        summarize_max_elevation = summarize.first_valid_index()
        summarize_min_elevation = summarize.last_valid_index()
        avg_thickness = summarize[summarize.columns[1:]].mean(
            axis=None, numeric_only=True)
        min_thickness = summarize[summarize.columns[1:]].min().nsmallest(3)

        tubes_range = f"{summarize.columns[0]} - {summarize.columns[-1]}"
        elevation_range = f"{summarize_min_elevation:.3f} m - {summarize_max_elevation:.3f} m" \
            .replace(".", ",")
        avg_thickness = f"{avg_thickness:.3f}".replace(".", ",") + " mm"

        data = []
        for index in min_thickness.index:
            thickness_value = min_thickness[index]
            # Agora as elevações já estão em metros — não dividir por 3.281
            elevation_value = summarize.index[summarize[index] == thickness_value][0]
            data.append({
                "min_reading": f"{thickness_value:.3f} mm".replace(".", ","),
                "tube": f"#{index}",
                "elevation": f"{elevation_value:.3f} m".replace(".", ",")
            })

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width,
            initial-scale=1.0">
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