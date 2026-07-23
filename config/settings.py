"""
Configuration centrale de l'application.
Toute constante partagée (étapes de production, colonnes fixes, couleurs)
est définie ici. Aucun nom de commande en dur : les commandes sont
détectées dynamiquement depuis les feuilles du Google Sheets.
"""

# Nom du fichier Google Sheets (à adapter) ou son ID
GOOGLE_SHEET_NAME = "Production_tracker"

# Chemin vers le fichier de credentials du compte de service Google
GOOGLE_CREDENTIALS_PATH = "credentials.json"

# Colonnes techniques fixes (informations produit, non liées à l'avancement)
FIXED_COLUMNS = [
    "Item",
    "Type",
    "DN",
    "Class",
    "Matière",
    "Qté totale",
]

# Étapes de production, dans l'ordre du process.
# L'ordre de cette liste détermine l'ordre d'affichage partout dans l'app.
PRODUCTION_STEPS = [
    "Montage",
    "Test",
    "Grenaillage",
    "Peinture",
    "Emballage",
    "Expédition",
]

# Colonne libre de commentaire (optionnelle, pas utilisée dans les calculs)
REMARK_COLUMN = "Remarque"

# Colonne quantité totale commandée
QTY_COLUMN = "Qté totale"

# Couleur associée à chaque étape (utilisée dans les graphiques et barres)
STEP_COLORS = {
    "Montage": "#4C72B0",
    "Grenaillage": "#DD8452",
    "Peinture": "#55A868",
    "Test": "#C44E52",
    "Emballage": "#8172B2",
    "Expédition": "#37A794",
    "En attente": "#808080",
}

# Durée du cache (secondes) avant re-fetch automatique des données Google Sheets
CACHE_TTL_SECONDS = 60

# Intervalle de rafraîchissement automatique de la page (millisecondes)
AUTOREFRESH_INTERVAL_MS = 60_000