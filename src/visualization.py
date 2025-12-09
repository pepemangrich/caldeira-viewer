# src/visualization.py
# type: ignore

"""
Script para a geração do gráfico e visualização dos dados
(agora com dados já em metros e milímetros — sem conversões)
"""

import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_plotly_events import plotly_events


def _build_image_map(uploaded_file, sheet_name="Photos"):
    try:
        xls = pd.ExcelFile(uploaded_file)
        if sheet_name not in xls.sheet_names:
            return {}

        df = pd.read_excel(uploaded_file, sheet_name)
        df.columns = [str(c).strip().lower() for c in df.columns]

        col_wall = "wall" if "wall" in df.columns else (
            "componente" if "componente" in df.columns else None
        )
        col_tube = "tube" if "tube" in df.columns else (
            "tubo" if "tubo" in df.columns else None
        )
        col_path = "path" if "path" in df.columns else (
            "arquivo" if "arquivo" in df.columns else None
        )

        if not (col_wall and col_tube and col_path):
            return {}

        if "elevation_m" in df.columns:
            elev_m = df["elevation_m"].astype(float)
        elif "elevation_ft" in df.columns:
            elev_m = df["elevation_ft"].astype(float) / 3.281
        else:
            return {}

        wall = df[col_wall].astype(str).str.strip()
        tube = df[col_tube].astype(str).str.strip()
        path = df[col_path].astype(str).str.strip()

        mp = {}
        for w, t, em, p in zip(wall, tube, elev_m, path):
            mp[(w, t, round(float(em), 3))] = p
        return mp
    except Exception:
        return {}


def _guess_image_path(base_folder, wall, tube, elev_m):
    candidates = []
    for ndec in (3, 2, 1, 0):
        fmt = f"{{:.{ndec}f}}"
        em = fmt.format(float(elev_m))
        candidates += [
            os.path.join(base_folder, f"{wall}_T{tube}_E{em}.jpg"),
            os.path.join(base_folder, f"{wall}_T{tube}_E{em}.png"),
        ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def create_heatmap(uploaded_file, sheets, image_folder="imgs/fotos", image_map_sheet="Photos"):
    selected_sheet = st.sidebar.selectbox("Componente:", sheets)

    dataframe = pd.read_excel(uploaded_file, selected_sheet)
    dataframe = dataframe.iloc[3:].reset_index(drop=True)

    # Eixo Y (elevação) em metros
    first_col = pd.to_numeric(dataframe.iloc[:, 0], errors="coerce")

    # Define elevação como índice
    dataframe.set_index(dataframe.columns[0], inplace=True)

    # Leituras em mm
    dataframe = dataframe.apply(pd.to_numeric, errors="coerce")

    if "reduction_mm" not in st.session_state:
        st.session_state.reduction_mm = 0.0
    if "reduction_mm_on" not in st.session_state:
        st.session_state.reduction_mm_on = False

    if "reduction_percent" not in st.session_state:
        st.session_state.reduction_percent = 0.0
    if "reduction_percent_on" not in st.session_state:
        st.session_state.reduction_percent_on = False

    factor = (
        1.0 - (st.session_state.reduction_percent / 100.0)
        if st.session_state.reduction_percent_on and st.session_state.reduction_percent > 0
        else 1.0
    )
    working_df = dataframe * factor

    if st.session_state.reduction_mm_on and st.session_state.reduction_mm > 0:
        working_df = working_df - st.session_state.reduction_mm

    # Sidebar (filtros)
    with st.sidebar:
        slider_min = float(np.nanmin(working_df.values))
        slider_max = float(np.nanmax(working_df.values))
        if slider_min == slider_max:
            slider_max = slider_min + 1e-6

        min_value, max_value = st.slider(
            "Selecione o intervalo de espessuras:",
            min_value=slider_min,
            max_value=slider_max,
            value=(slider_min, slider_max),
            key="thickness_range",
        )

        condition_percent = (working_df >= min_value) & (working_df <= max_value)
        dataframe_total = working_df.count().sum()
        filtered_total = working_df[condition_percent].count().sum()
        percent_interval = (filtered_total / dataframe_total * 100) if dataframe_total else 0.0

        with st.container(border=True):
            st.markdown(
                f"Representa :orange[{percent_interval:.2f}%] das espessuras".replace(".", ",")
            )

        st.markdown("#### Ajuste nas leituras")

        reduction_input_mm = st.number_input(
            "Reduzir espessura em (mm):",
            min_value=0.0,
            step=0.1,
            format="%.3f",
            value=float(st.session_state.reduction_mm),
            help="Subtrai este valor de todas as leituras exibidas."
        )
        col_mm_a, col_mm_b = st.columns(2)
        if col_mm_a.button("Aplicar (mm)", key="apply_mm"):
            st.session_state.reduction_mm = float(reduction_input_mm)
            st.session_state.reduction_mm_on = True
            st.rerun()
        if col_mm_b.button("Limpar (mm)", key="clear_mm"):
            st.session_state.reduction_mm = 0.0
            st.session_state.reduction_mm_on = False
            st.rerun()

        if st.session_state.reduction_mm_on and st.session_state.reduction_mm > 0:
            st.caption(
                f"Ajuste em mm ativo: −{st.session_state.reduction_mm:.3f} mm".replace(".", ",")
            )

        reduction_input_pct = st.number_input(
            "Reduzir espessura em (%):",
            min_value=0.0,
            max_value=1000.0,
            step=0.1,
            format="%.1f",
            value=float(st.session_state.reduction_percent),
            help="Aplica fator multiplicativo: espessura × (1 − %/100)."
        )
        col_pc_a, col_pc_b = st.columns(2)
        if col_pc_a.button("Aplicar (%)", key="apply_pct"):
            st.session_state.reduction_percent = float(reduction_input_pct)
            st.session_state.reduction_percent_on = True
            st.rerun()
        if col_pc_b.button("Limpar (%)", key="clear_pct"):
            st.session_state.reduction_percent = 0.0
            st.session_state.reduction_percent_on = False
            st.rerun()

        if st.session_state.reduction_percent_on and st.session_state.reduction_percent > 0:
            st.caption(
                ("Ajuste percentual ativo: −"
                 f"{st.session_state.reduction_percent:.1f}%").replace(".", ",")
            )

    # ======== ESCALA DE CORES FIXA ========
    FIX_MIN = 2.5
    FIX_MAX = 9.0

    def normalize(v):
        return (v - FIX_MIN) / (FIX_MAX - FIX_MIN)

    colorscale = [
        [normalize(FIX_MIN), "darkred"],
        [normalize(3.5), "red"],
        [normalize(3.6), "yellow"],
        [normalize(4.1), "gold"],
        [normalize(4.2), "lightgreen"],
        [normalize(FIX_MAX), "green"],
    ]
    # =====================================

    in_range = (working_df >= min_value) & (working_df <= max_value) & (working_df > 0)
    color_values = working_df.where(in_range, np.nan)
    mask_black_bool = (working_df <= 0)
    black_mask = np.where(mask_black_bool, 1, np.nan)

    # X categórico na ordem original
    cols = working_df.columns.astype(str).tolist()

    fig = go.Figure(data=go.Heatmap(
        z=color_values,
        y=first_col,
        x=cols,
        zmin=FIX_MIN,
        zmax=FIX_MAX,
        colorscale=colorscale,
        hovertemplate='<b>Tubo:</b> %{x}<br>'
                      '<b>Elevação:</b> %{y:.3f} m<br>'
                      '<b>Espessura:</b> %{z:.3f} mm<extra></extra>',
        hoverongaps=False
    ))

    fig.add_trace(go.Heatmap(
        z=black_mask,
        y=first_col,
        x=cols,
        colorscale=[[0, "black"], [1, "black"]],
        zmin=0,
        zmax=1,
        showscale=False,
        hovertemplate=(
            "<b>Tubo:</b> %{x}<br>"
            "<b>Elevação:</b> %{y:.3f} m<br>"
            "<b>Espessura:</b> %{customdata:.3f} mm"
            "<extra></extra>"
        ),
        customdata=working_df.values,
        hoverongaps=False,
        opacity=1.0
    ))

    # ---- ticks do eixo X: marcar de 5 em 5 colunas ----
    tick_idx = list(range(0, len(cols), 5))
    if cols and (len(cols) - 1) not in tick_idx:
        tick_idx.append(len(cols) - 1)
    x_tickvals = [cols[i] for i in tick_idx]
    x_ticktext = x_tickvals
    # ---------------------------------------------------

    # ---- eixo Y: marcar de 2 em 2 m (dtick) ----
    y_vals = first_col.values
    if np.isfinite(y_vals).any():
        y_min = float(np.nanmin(y_vals))
        y_max = float(np.nanmax(y_vals))
    else:
        y_min, y_max = 0.0, 0.0

    y_tick0 = 2.0 * np.floor(min(y_min, y_max) / 2.0)
    # ---------------------------------------------------

    fig.update_layout(
        hovermode="closest",
        yaxis=dict(
            title="Elevação",
            type="linear",
            tickmode="linear",
            tick0=y_tick0,
            dtick=2.0,
            tickformat=".0f",
            ticksuffix=" m",
        ),
        xaxis=dict(
            title="Tubos",
            type="category",
            categoryorder="array",
            categoryarray=cols,
            tickmode="array",
            tickvals=x_tickvals,
            ticktext=x_ticktext,
            automargin=True,
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    if (working_df <= 0).any().any():
        st.warning("Algumas leituras ficaram ≤ 0 mm após os ajustes. Elas estão destacadas em preto.")

    if "image_map_cache" not in st.session_state:
        st.session_state.image_map_cache = _build_image_map(uploaded_file, sheet_name=image_map_sheet)

    # if selected:
    #     pt = selected[0]
    #     tube_clicked = str(pt.get("x"))
    #     elev_clicked_m = float(pt.get("y"))

    #     idx_nearest = (first_col - elev_clicked_m).abs().idxmin()
    #     elev_row_m = float(first_col.iloc[idx_nearest])

    #     img_path = None
    #     mp = st.session_state.image_map_cache or {}
    #     k = (str(selected_sheet), tube_clicked, round(elev_row_m, 3))
    #     if k in mp:
    #         img_path = mp[k]
    #     else:
    #         img_path = _guess_image_path(image_folder, str(selected_sheet), tube_clicked, elev_row_m)

    #     st.markdown(
    #         f"**Ponto selecionado** → Parede: `{selected_sheet}` • Tubo: `#{tube_clicked}` • Elevação: `{elev_row_m:.3f} m`"
    #         .replace(".", ",")
    #     )
    #     if img_path and os.path.exists(img_path):
    #         st.image(img_path, caption=f"{selected_sheet} — Tubo #{tube_clicked} — {elev_row_m:.3f} m")
    #     else:
    #         st.info("Nenhuma imagem encontrada para este ponto. "
    #                 "Você pode adicionar uma planilha `Photos` ao Excel (wall, tube, elevation_m, path) "
    #                 f"ou salvar as imagens em `{image_folder}` usando o padrão "
    #                 "`{WALL}_T{TUBO}_E{ELEV}.jpg|png` (em m).")

    return working_df