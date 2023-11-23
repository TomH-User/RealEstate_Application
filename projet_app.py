import calendar
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import streamlit as st
import plotly.express as px
import base64
import time
from datetime import datetime
import liste_fonction as lf

def execution_time_logger(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Temps d'execution dans un fichier
        with open("execution_log.txt", "a") as log_file:
            log_file.write(
                f"Timestamp: {timestamp}, Temps d'execution: {execution_time:.2f} seconds\n"
            )

        return result

    return wrapper


### interactive element : date input pour le prix moyen au m2 en fonction du mois indiqué
### ------------- Main -------------------###

@execution_time_logger
def __main__():
    st.set_page_config(
        page_title="Tableau de bord - Immobilier",
        page_icon=":bar_chart:",
        layout="wide",
    )
    # Import des données et création du dataframe
    df = lf.get_data()

    # Filtrage de mes données
    selected_type_local, selected_region, selected_nature_mutation = lf.implement_sidebar(df)

    # Filtrer le DataFrame en fonction de la région et du type_local sélectionnés
    df_selection = lf.filter_dataframe(df, selected_region, selected_type_local,selected_nature_mutation)

    # Gestion du cas où le dataframe est vide:
    if df_selection.empty:
        st.warning("Il n'y a aucune donnée disponible!")
        st.stop()

    # Ajoutez un bouton de téléchargement
    lf.download_button(df_selection, label="Télécharger les données au format CSV")

    # Affichage des graphiques
    lf.affichage_application(df_selection)


__main__()
