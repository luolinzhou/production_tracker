"""
Vue de la situation actuelle dans l'atelier.

Sont considérées comme présentes dans l'atelier :
- Montage
- Grenaillage
- Peinture
- Test
- Emballage

Sont exclues :
- En attente
- Expédition
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from config.settings import PRODUCTION_STEPS
from data.processing import clean_order_dataframe
from data.sheets_client import list_order_names, load_order_dataframe, get_last_update
from ui.components import render_process_explanation


WORKSHOP_STEPS = [
    "Montage",
    "Grenaillage",
    "Peinture",
    "Test",
    "Emballage",
]


def render_workshop_view() -> None:
    """Affiche la situation actuelle des vannes présentes dans l'atelier."""

    st.header("Situation actuelle dans l'atelier")

    last_update = get_last_update()
    st.caption(f"Dernière mise à jour des données : {last_update}")

    render_process_explanation()

    order_names = list_order_names()

    if not order_names:
        st.info("Aucune commande détectée dans le Google Sheets.")
        return

    # ---------------------------------------------------------
    # Construction du tableau atelier
    # ---------------------------------------------------------

    rows = []

    for order_name in order_names:

        raw_df = load_order_dataframe(order_name)
        df = clean_order_dataframe(raw_df)

        if df.empty:
            continue

        for _, row in df.iterrows():

            for step in WORKSHOP_STEPS:

                quantity = int(row.get(step, 0))

                if quantity <= 0:
                    continue

                rows.append(
                    {
                        "Commande": order_name,
                        "Item": row.get("Item", ""),
                        "Type": row.get("Type", ""),
                        "DN": row.get("DN", ""),
                        "Class": row.get("Class", ""),
                        "Matière": row.get("Matière", ""),
                        "Quantité": quantity,
                        "Étape": step,
                        "Remarque": row.get("Remarque", ""),
                    }
                )

    if not rows:
        st.info("Aucune vanne actuellement présente dans l'atelier.")
        return

    workshop_df = pd.DataFrame(rows)

    # ---------------------------------------------------------
    # Filtres
    # ---------------------------------------------------------

    with st.expander("Filtres", expanded=False):

        selected_orders = st.multiselect(
            "Commande",
            sorted(workshop_df["Commande"].unique()),
        )

        selected_steps = st.multiselect(
            "Étape",
            WORKSHOP_STEPS,
        )

        selected_types = st.multiselect(
            "Type de vanne",
            sorted(workshop_df["Type"].unique()),
        )

    filtered_df = workshop_df.copy()

    if selected_orders:
        filtered_df = filtered_df[
            filtered_df["Commande"].isin(selected_orders)
        ]

    if selected_steps:
        filtered_df = filtered_df[
            filtered_df["Étape"].isin(selected_steps)
        ]

    if selected_types:
        filtered_df = filtered_df[
            filtered_df["Type"].isin(selected_types)
        ]

    # ---------------------------------------------------------
    # KPI
    # ---------------------------------------------------------

    total_workshop = int(filtered_df["Quantité"].sum())

    st.metric(
        "Vannes actuellement dans l'atelier",
        total_workshop,
    )

    st.divider()

    # ---------------------------------------------------------
    # Répartition par étape
    # ---------------------------------------------------------

    st.subheader("Répartition dans l'atelier")

    summary = (
        filtered_df.groupby("Étape")["Quantité"]
        .sum()
        .reindex(WORKSHOP_STEPS, fill_value=0)
    )

    columns = st.columns(len(WORKSHOP_STEPS))

    for column, step in zip(columns, WORKSHOP_STEPS):

        with column:
            st.metric(
                step,
                int(summary[step]),
            )

    st.divider()

    # ---------------------------------------------------------
    # Tableau détaillé
    # ---------------------------------------------------------

    st.subheader("Vannes présentes dans l'atelier")

    display_columns = [
        "Commande",
        "Item",
        "Type",
        "DN",
        "Class",
        "Matière",
        "Quantité",
        "Étape",
        "Remarque",
    ]

    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        hide_index=True,
    )