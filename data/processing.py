"""
Nettoyage, typage et validation des données de production
issues du Google Sheets, indépendamment de toute commande
spécifique (aucun nom en dur).
"""

from __future__ import annotations

import pandas as pd

from config.settings import FIXED_COLUMNS, PRODUCTION_STEPS, QTY_COLUMN


def clean_order_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convertit les colonnes numériques (quantité + étapes) en entiers,
    et s'assure que les colonnes attendues existent (créées à 0/vide
    si absentes, pour tolérer des feuilles partiellement remplies).
    """
    if df.empty:
        return df

    df = df.copy()

    numeric_columns = [QTY_COLUMN] + PRODUCTION_STEPS
    for col in numeric_columns:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    for col in FIXED_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    return df


def compute_step_totals(df: pd.DataFrame) -> pd.Series:
    """Retourne le nombre total de vannes ayant atteint chaque étape."""
    if df.empty:
        return pd.Series({step: 0 for step in PRODUCTION_STEPS})
    return df[PRODUCTION_STEPS].sum()


def compute_pivot_type_step(df: pd.DataFrame) -> pd.DataFrame:
    """Tableau croisé : type de vanne (lignes) x étape (colonnes)."""
    if df.empty:
        return pd.DataFrame(columns=PRODUCTION_STEPS)
    pivot = df.groupby("Type")[PRODUCTION_STEPS].sum()
    return pivot


def compute_kpis(df: pd.DataFrame) -> dict:
    """
    Calcule les indicateurs clés d'une commande :
    total commandé, total expédié, taux d'avancement global.
    Le taux d'avancement global est la moyenne d'avancement
    pondérée par la quantité totale de chaque item, sur la
    dernière étape du process (Expédition étant l'aboutissement).
    """
    if df.empty:
        return {
            "total_qty": 0,
            "total_shipped": 0,
            "progress_rate": 0.0,
        }

    total_qty = int(df[QTY_COLUMN].sum())
    last_step = PRODUCTION_STEPS[-1]
    total_shipped = int(df[last_step].sum())

    # Avancement global = moyenne de toutes les étapes / (nb_étapes * qty totale)
    total_possible = total_qty * len(PRODUCTION_STEPS)
    total_achieved = int(df[PRODUCTION_STEPS].sum().sum())
    progress_rate = (total_achieved / total_possible * 100) if total_possible else 0.0

    return {
        "total_qty": total_qty,
        "total_shipped": total_shipped,
        "progress_rate": round(progress_rate, 1),
    }


def filter_dataframe(
    df: pd.DataFrame,
    types: list[str] | None = None,
    item_search: str | None = None,
) -> pd.DataFrame:
    """Applique les filtres optionnels (type de vanne, recherche item) au tableau."""
    filtered = df.copy()

    if types:
        filtered = filtered[filtered["Type"].isin(types)]

    if item_search:
        filtered = filtered[
            filtered["Item"].astype(str).str.contains(item_search, case=False, na=False)
        ]

    return filtered