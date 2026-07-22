"""
Vue détaillée d'une commande sélectionnée : KPI, tableaux,
graphiques, filtres. Assemble les modules data / ui / visualizations
sans contenir lui-même de logique de calcul.
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from data.sheets_client import load_order_dataframe
from data.processing import (
    clean_order_dataframe,
    compute_step_totals,
    compute_pivot_type_step,
    compute_kpis,
    filter_dataframe,
)
from ui.components import (
    render_kpis,
    render_order_progress,
    render_step_progress_bars,
    render_detail_table,
    render_step_summary_table,
    render_pivot_table,
)
from visualizations.charts import (
    build_step_bar_chart,
    build_step_pie_chart,
    build_pivot_heatmap,
)


def render_order_view(order_name: str) -> None:
    """Charge et affiche l'intégralité du détail d'une commande donnée."""
    st.subheader(f"Commande : {order_name}")

    raw_df = load_order_dataframe(order_name)
    df = clean_order_dataframe(raw_df)

    if df.empty:
        st.warning("Aucune donnée trouvée pour cette commande.")
        return

    # --- Filtres ---
    with st.expander("Filtres", expanded=False):
        available_types = sorted(df["Type"].dropna().unique().tolist())
        selected_types = st.multiselect("Type de vanne", available_types)
        item_search = st.text_input("Recherche par Item")

    filtered_df = filter_dataframe(df, types=selected_types, item_search=item_search)

    # --- KPI ---
    kpis = compute_kpis(filtered_df)
    last_update = datetime.now().strftime("%d/%m/%Y %H:%M")
    render_kpis(kpis, last_update)

    st.divider()

    # --- Progression ---
    render_order_progress(kpis)
    with st.expander("Détail de l'avancement par étape", expanded=False):
        render_step_progress_bars(compute_step_totals(filtered_df), kpis["total_qty"])

    st.divider()

    # --- Graphiques ---
    step_totals = compute_step_totals(filtered_df)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(build_step_bar_chart(step_totals), use_container_width=True)
    with col2:
        st.plotly_chart(build_step_pie_chart(step_totals), use_container_width=True)

    pivot_df = compute_pivot_type_step(filtered_df)
    st.plotly_chart(build_pivot_heatmap(pivot_df), use_container_width=True)

    st.divider()

    # --- Tableaux ---
    tab1, tab2, tab3 = st.tabs(["Détail par item", "Récap par étape", "Croisé type × étape"])
    with tab1:
        render_detail_table(filtered_df)
    with tab2:
        render_step_summary_table(step_totals)
    with tab3:
        render_pivot_table(pivot_df)