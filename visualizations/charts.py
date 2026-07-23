"""
Graphiques Plotly pour la répartition des vannes par étape.
Séparé des composants UI pour isoler la logique de visualisation.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config.settings import PRODUCTION_STEPS, STEP_COLORS


def build_step_bar_chart(step_totals: pd.Series) -> go.Figure:
    """Diagramme en barres du nombre de vannes par étape."""
    steps = step_totals.index.tolist()
    values = [step_totals[s] for s in steps]
    colors = [STEP_COLORS.get(s, "#999999") for s in steps]

    fig = go.Figure(
        data=[go.Bar(x=steps, y=values, marker_color=colors, text=values, textposition="outside")]
    )
    fig.update_layout(
        title="Répartition des vannes par étape",
        xaxis_title="Étape",
        yaxis_title="Nombre de vannes",
        showlegend=False,
        margin=dict(t=50, b=20),
    )
    return fig


def build_step_pie_chart(step_totals: pd.Series) -> go.Figure:
    """Camembert de répartition des vannes par étape."""
    steps = step_totals.index.tolist()
    values = [step_totals[s] for s in steps]
    colors = [STEP_COLORS.get(s, "#999999") for s in steps]

    fig = go.Figure(
        data=[go.Pie(labels=steps, values=values, marker=dict(colors=colors))]
    )
    fig.update_layout(title="Part de chaque étape", margin=dict(t=50, b=20))
    return fig