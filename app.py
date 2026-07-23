"""
Point d'entrée de l'application Streamlit — Suivi de production.

Ce fichier ne contient aucune logique métier : il assemble uniquement
les modules de data / ui / visualizations et gère la navigation.
"""
from auth import check_password
import streamlit as st

from config.settings import AUTOREFRESH_INTERVAL_MS
from data.sheets_client import list_order_names, clear_cache
from ui.order_view import render_order_view
from ui.overview import render_overview

st.set_page_config(
    page_title="Suivi de production - Vannes",
    page_icon="🏭",
    layout="wide",
)


def main() -> None:

    if not check_password():
        return

    st.title("🏭 Suivi de production — Vannes")

    # Rafraîchissement automatique périodique (optionnel, nécessite streamlit-autorefresh)
    try:
        from streamlit_autorefresh import st_autorefresh

        st_autorefresh(interval=AUTOREFRESH_INTERVAL_MS, key="auto_refresh")
    except ImportError:
        pass

    with st.sidebar:
        st.header("Navigation")
        view_mode = st.radio("Vue", ["Commande détaillée", "Vue globale"])

        if st.button("🔄 Forcer le rechargement des données"):
            clear_cache()
            st.rerun()

    if view_mode == "Vue globale":
        render_overview()
        return

    order_names = list_order_names()

    if not order_names:
        st.warning(
            "Aucune commande détectée. Vérifiez que le Google Sheets "
            "contient au moins une feuille et que les accès sont corrects."
        )
        return

    selected_order = st.sidebar.selectbox("Sélectionner une commande", order_names)

    render_order_view(selected_order)


if __name__ == "__main__":
    main()