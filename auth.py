import streamlit as st


def check_password():
    """Retourne True si le mot de passe est correct."""

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🔒 Accès sécurisé")

    password = st.text_input(
        "Mot de passe",
        type="password"
    )

    if st.button("Connexion"):
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Mot de passe incorrect")

    return False