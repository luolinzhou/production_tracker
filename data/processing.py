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
    """
    Retourne le nombre de vannes présentes dans chaque étape de production,
    ainsi que les vannes encore en attente.
    """
    if df.empty:
        return pd.Series(
            {
                "En attente": 0,
                **{step: 0 for step in PRODUCTION_STEPS},
            }
        )

    step_totals = df[PRODUCTION_STEPS].sum()

    pending = (
        df[QTY_COLUMN]
        - df[PRODUCTION_STEPS].sum(axis=1)
    ).clip(lower=0).sum()

    return pd.Series(
        {
            "En attente": int(pending),
            **step_totals.to_dict(),
        }
    )

def compute_kpis(df: pd.DataFrame) -> dict:
    """
    Calcule les indicateurs clés d'une commande :
    total commandé, total expédié, taux d'avancement par commande.
    Le taux d'avancement par commande est la moyenne d'avancement
    pondérée par la quantité de chaque item de la commande, sur la
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

    # Avancement commande = nombre de vannes expédiées / nombre total de vannes
    progress_rate = (
        total_shipped / total_qty * 100
        if total_qty
        else 0.0
    )

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

def compute_workshop_status(
    df: pd.DataFrame,
    order_name: str,
) -> pd.DataFrame:
    """
    Détermine la situation actuelle des vannes dans l'atelier.

    Une vanne est considérée comme étant à l'étape correspondant
    à la première étape non nulle du process :
    Montage → Grenaillage → Peinture → Test → Emballage.

    Les vannes déjà expédiées sont exclues.
    Les vannes n'ayant encore atteint aucune étape sont classées
    comme "En attente".
    """

    if df.empty:
        return pd.DataFrame()

    df = df.copy()

    # Étapes physiques présentes dans l'atelier.
    # Expédition n'est volontairement pas incluse.
    workshop_steps = [
        "Montage",
        "Grenaillage",
        "Peinture",
        "Test",
        "Emballage",
    ]

    # S'assurer que les colonnes existent.
    for step in workshop_steps + ["Expédition"]:
        if step not in df.columns:
            df[step] = 0

    # Une ligne de résultat par item.
    rows = []

    for _, row in df.iterrows():

        qty_total = int(row[QTY_COLUMN])

        # Quantité déjà expédiée.
        qty_shipped = int(row["Expédition"])

        # Quantité restante dans l'atelier.
        qty_workshop = qty_total - qty_shipped

        if qty_workshop <= 0:
            continue

        # Déterminer l'étape actuelle.
        current_step = "En attente"

        for step in workshop_steps:
            if int(row[step]) > 0:
                current_step = step
                break

        rows.append(
            {
                "Commande": order_name,
                "Item": row.get("Item", ""),
                "Type": row.get("Type", ""),
                "DN": row.get("DN", ""),
                "Class": row.get("Class", ""),
                "Matière": row.get("Matière", ""),
                "Qté totale": qty_total,
                "Qté atelier": qty_workshop,
                "Étape actuelle": current_step,
            }
        )

    return pd.DataFrame(rows)