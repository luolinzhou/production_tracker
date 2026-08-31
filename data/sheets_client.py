"""
Gestion de la connexion à Google Sheets et découverte dynamique
des commandes (une feuille = une commande).

Aucun nom de commande n'est en dur ici : la liste des commandes
disponibles est toujours dérivée de gspread.worksheets().
"""

from __future__ import annotations

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

from config.settings import (
    GOOGLE_SHEET_NAME,
    GOOGLE_CREDENTIALS_PATH,
    CACHE_TTL_SECONDS,
    CONFIG_SHEET_NAME,
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


@st.cache_resource(show_spinner=False)
def get_client() -> gspread.Client:
    """Crée et met en cache le client gspread authentifié."""

    import os

    secrets_path = ".streamlit/secrets.toml"

    if os.path.exists(secrets_path):
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=SCOPES,
        )
    else:
        creds = Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_PATH,
            scopes=SCOPES,
        )

    return gspread.authorize(creds)


@st.cache_resource(show_spinner=False)
def get_spreadsheet() -> gspread.Spreadsheet:
    """Ouvre et met en cache le classeur Google Sheets cible."""
    client = get_client()
    return client.open(GOOGLE_SHEET_NAME)


def list_order_names() -> list[str]:
    """
    Retourne dynamiquement le nom de toutes les feuilles du classeur
    correspondant aux commandes.

    L'onglet Config est exclu car il est réservé aux informations
    techniques de l'application.
    """
    spreadsheet = get_spreadsheet()
    worksheets = spreadsheet.worksheets()

    return [
        ws.title
        for ws in worksheets
        if ws.title != CONFIG_SHEET_NAME
    ]


@st.cache_data(ttl=60, show_spinner=False)
def get_last_update() -> str:
    """Retourne la date de dernière modification enregistrée dans Config!A2."""
    spreadsheet = get_spreadsheet()
    config_sheet = spreadsheet.worksheet(CONFIG_SHEET_NAME)

    value = config_sheet.acell("A2").value

    if not value:
        return "Inconnue"

    return value


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def load_order_dataframe(order_name: str) -> pd.DataFrame:
    """
    Charge les données brutes d'une commande (une feuille) sous
    forme de DataFrame. Mise en cache avec expiration courte pour
    que les modifications faites sur le Sheet remontent sans
    redémarrer l'application.
    """
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet(order_name)
    records = worksheet.get_all_records()
    df = pd.DataFrame(records)
    return df


def clear_cache() -> None:
    """Force le rechargement complet des données au prochain accès."""
    load_order_dataframe.clear()
    get_last_update.clear()
    get_spreadsheet.clear()