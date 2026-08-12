"""
Vue de la situation actuelle dans l'atelier.

Affiche toutes les vannes qui ne sont pas encore expédiées,
avec leur étape actuelle dans le processus de production.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from data.sheets_client import list_order_names, load_order_dataframe
from data.processing import (
    clean_order_dataframe,
    compute_workshop_status,
)


WORKSHOP_STEPS = [
    "En attente",
    "Montage",
    "Grenaillage",
    "Peinture",
    "Test",
    "Emballage",
]


def render_workshop_view() -> None:
    """Affiche la situation actuelle de toutes les vannes dans l'atelier."""

    st.header("Situation actuelle dans l'atelier")

    order_names = list_order_names()

    if not order_names:
        st.info("Aucune commande détectée.")
        return

    # ---------------------------------------------------------
    # Chargement de toutes les commandes
    # ---------------------------------------------------------

    all_workshop_data = []

    for order_name in order_names:

        raw_df = load_order_dataframe(order_name)
        df = clean_order_dataframe(raw_df)

        if df.empty:
            continue

        workshop_df = compute_workshop_status(
            df,
            order_name,
        )

        if not workshop_df.empty:
            all_workshop_data.append(workshop_df)

    if not all_workshop_data:
        st.success("Aucune vanne actuellement dans l'atelier.")
        return

    workshop_df = pd.concat(
        all_workshop_data,
        ignore_index=True,
    )

    # ---------------------------------------------------------
    # Filtres
    # ---------------------------------------------------------

    with st.expander("Filtres", expanded=True):

        col1, col2, col3 = st.columns(3)

        with col1:
            available_orders = sorted(
                workshop_df["Commande"].dropna().unique().tolist()
            )

            selected_orders = st.multiselect(
                "Commande",
                available_orders,
            )

        with col2:
            available_steps = [
                step
                for step in WORKSHOP_STEPS
                if step in workshop_df["Étape actuelle"].unique()
            ]

            selected_steps = st.multiselect(
                "Étape",
                available_steps,
            )

        with col3:
            available_types = sorted(
                workshop_df["Type"].dropna().unique().tolist()
            )

            selected_types = st.multiselect(
                "Type de vanne",
                available_types,
            )

    # ---------------------------------------------------------
    # Application des filtres
    # ---------------------------------------------------------

    filtered_df = workshop_df.copy()

    if selected_orders:
        filtered_df = filtered_df[
            filtered_df["Commande"].isin(selected_orders)
        ]

    if selected_steps:
        filtered_df = filtered_df[
            filtered_df["Étape actuelle"].isin(selected_steps)
        ]

    if selected_types:
        filtered_df = filtered_df[
            filtered_df["Type"].isin(selected_types)
        ]

    # ---------------------------------------------------------
    # KPI
    # ---------------------------------------------------------

    total_workshop = int(filtered_df["Qté atelier"].sum())

    st.metric(
        "Vannes actuellement dans l'atelier",
        total_workshop,
    )

    st.divider()

    # ---------------------------------------------------------
    # Récapitulatif par étape
    # ---------------------------------------------------------

    step_summary = (
        filtered_df
        .groupby("Étape actuelle")["Qté atelier"]
        .sum()
        .reindex(WORKSHOP_STEPS, fill_value=0)
        .astype(int)
    )

    st.subheader("Répartition par étape")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    columns = [
        col1,
        col2,
        col3,
        col4,
        col5,
        col6,
    ]

    for column, step in zip(columns, WORKSHOP_STEPS):
        column.metric(
            step,
            int(step_summary[step]),
        )

    st.divider()

    # ---------------------------------------------------------
    # Tableau détaillé
    # ---------------------------------------------------------

    st.subheader("Détail des vannes dans l'atelier")

    display_columns = [
        "Commande",
        "Item",
        "Type",
        "DN",
        "Class",
        "Matière",
        "Qté totale",
        "Qté atelier",
        "Étape actuelle",
    ]

    display_columns = [
        column
        for column in display_columns
        if column in filtered_df.columns
    ]

    display_df = filtered_df[display_columns].copy()

    # Trier selon l'ordre logique du process.
    display_df["Étape actuelle"] = pd.Categorical(
        display_df["Étape actuelle"],
        categories=WORKSHOP_STEPS,
        ordered=True,
    )

    display_df = display_df.sort_values(
        ["Étape actuelle", "Commande", "Item"]
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )