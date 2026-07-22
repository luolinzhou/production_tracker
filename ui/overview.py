"""
Vue d'ensemble de toutes les commandes : avancement global de
chacune, sans devoir sélectionner une commande à la fois.
Aucun nom de commande en dur : la liste vient de sheets_client.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from data.sheets_client import list_order_names, load_order_dataframe
from data.processing import clean_order_dataframe, compute_kpis
from ui.components import render_progress_bar


def render_overview() -> None:
    """Affiche un récapitulatif d'avancement pour chaque commande détectée."""
    order_names = list_order_names()

    if not order_names:
        st.info("Aucune commande détectée dans le Google Sheets.")
        return

    rows = []
    for name in order_names:
        raw_df = load_order_dataframe(name)
        df = clean_order_dataframe(raw_df)
        kpis = compute_kpis(df)
        rows.append(
            {
                "Commande": name,
                "Qté totale": kpis["total_qty"],
                "Expédié": kpis["total_shipped"],
                "Avancement (%)": kpis["progress_rate"],
            }
        )

    overview_df = pd.DataFrame(rows).sort_values("Avancement (%)", ascending=True)

    st.dataframe(overview_df, use_container_width=True)

    st.divider()
    st.subheader("Avancement par commande")
    for _, row in overview_df.iterrows():
        render_progress_bar(row["Commande"], row["Expédié"], row["Qté totale"])