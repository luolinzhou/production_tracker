"""
Composants d'interface réutilisables : KPI, tableaux, barres
de progression. Aucune logique métier ici, uniquement de l'affichage.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from config.settings import PRODUCTION_STEPS, STEP_COLORS


def render_kpis(kpis: dict) -> None:
    """Affiche la ligne de KPI principaux en haut de page."""
    col1, col2, col3 = st.columns(3)
    col1.metric("Vannes commandées", kpis["total_qty"])
    col2.metric("Vannes expédiées", kpis["total_shipped"])
    col3.metric("Avancement de la commande", f"{kpis['progress_rate']} %")


def render_progress_bar(label: str, done: int, total: int) -> None:
    """Affiche une barre de progression Streamlit pour une étape ou une commande."""
    ratio = (done / total) if total else 0
    st.write(f"**{label}** — {done}/{total} ({ratio * 100:.0f}%)")
    st.progress(min(ratio, 1.0))


def render_order_progress(kpis: dict) -> None:
    """Barre de progression globale de la commande (basée sur l'expédition)."""
    render_progress_bar(
        "Avancement de la commande (expédition)",
        kpis["total_shipped"],
        kpis["total_qty"],
    )


def render_step_progress_bars(step_totals: pd.Series, total_qty: int) -> None:
    """Une barre de progression par étape du process."""
    for step in PRODUCTION_STEPS:
        render_progress_bar(step, int(step_totals.get(step, 0)), total_qty)


def render_detail_table(df: pd.DataFrame) -> None:
    """Tableau détaillé de tous les items de la commande, avec mise en forme couleur."""
    st.dataframe(
        df.style.background_gradient(
            subset=PRODUCTION_STEPS, cmap="Greens", vmin=0
        ),
        use_container_width=True,
    )


def render_step_summary_table(step_totals: pd.Series) -> None:
    """Tableau récapitulatif du nombre total de vannes à chaque étape."""
    summary_df = step_totals.rename("Nombre de vannes").to_frame()
    st.dataframe(summary_df, use_container_width=True)


def step_color(step: str) -> str:
    """Retourne la couleur associée à une étape (fallback gris si inconnue)."""
    return STEP_COLORS.get(step, "#999999")