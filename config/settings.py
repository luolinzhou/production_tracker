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

# Ficher affichant date de maj des données
CONFIG_SHEET_NAME = "Config"

# Colonnes techniques fixes (informations produit, non liées à l'avancement)
FIXED_COLUMNS = [
    "Item",
    "JCFC Job Number",
    "Type",
    "DN",
    "Class",
    "Matière",
    "Qté totale",
]

# Étapes de production, dans l'ordre du process.
# L'ordre de cette liste détermine l'ordre d'affichage partout dans l'app.
PRODUCTION_STEPS = [
    "En attente",
    "Montage",
    "Test",
    "Grenaillage",
    "Peinture",
    "Emballage",
    "Expédition",
]

STEP_DESCRIPTIONS = {
    "En attente": (
        "Vannes dont les pièces ne sont pas encore arrivées ou pièces insuffisantes pour permettre le montage."
    ),
    "Montage": (
        "Vannes en cours de montage ou dont toutes les pièces nécessaires "
        "sont disponibles et prêtes à être montées."
    ),
    "Test": (
        "Vannes actuellement en cours de test."
    ),
    "Grenaillage": (
        "Vannes actuellement en cours de grenaillage."
    ),
    "Peinture": (
        "Vannes actuellement en cours de peinture."
    ),
    "Emballage": (
        "Vannes terminées et actuellement en cours d'emballage."
    ),
    "Expédition": (
        "Vannes terminées, emballées et sorties de l'atelier."
    ),
}

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

CONFIG_SHEET_NAME = "Config"